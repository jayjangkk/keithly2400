"""Executable test script for verifying the keithley2400 package against
a real Keithley 2400 Series SourceMeter connected via GPIB.

Run directly:
    python tests/test_instrument.py

Optionally pass a VISA resource string:
    python tests/test_instrument.py GPIB0::24::INSTR
"""

from __future__ import annotations

import sys
import time

from keithley2400 import Keithley2400


# ── helpers ─────────────────────────────────────────────────────────

def _header(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def _pass(msg: str) -> None:
    print(f"  [PASS] {msg}")


def _fail(msg: str) -> None:
    print(f"  [FAIL] {msg}")


def _info(msg: str) -> None:
    print(f"  [INFO] {msg}")


# ── test routines ───────────────────────────────────────────────────

def test_connection(smu: Keithley2400) -> bool:
    """Test 1: Identify the instrument and verify it responds."""
    _header("Test 1: Connection & Identification")
    try:
        idn = smu.identify()
        _info(f"*IDN? -> {idn}")
        if "KEITHLEY" in idn.upper() or "2400" in idn:
            _pass("Instrument identified as Keithley 2400 series.")
            return True
        else:
            _fail(f"Unexpected IDN response: {idn}")
            return False
    except Exception as e:
        _fail(f"Communication error: {e}")
        return False


def test_reset(smu: Keithley2400) -> bool:
    """Test 2: Reset and verify default state."""
    _header("Test 2: Reset (*RST)")
    try:
        smu.reset()
        # After *RST the output should be off
        is_on = smu.config.is_output_on()
        _info(f"Output state after *RST: {'ON' if is_on else 'OFF'}")
        if not is_on:
            _pass("Output is OFF after reset (expected).")
            return True
        else:
            _fail("Output is ON after reset -- unexpected.")
            return False
    except Exception as e:
        _fail(f"Error during reset test: {e}")
        return False


def test_error_queue(smu: Keithley2400) -> bool:
    """Test 3: Read the error queue -- should be clean after reset."""
    _header("Test 3: Error Queue")
    try:
        code, msg = smu.status.read_error()
        _info(f"Error queue: ({code}, \"{msg}\")")
        if code == 0:
            _pass("Error queue is clean.")
            return True
        else:
            _fail(f"Unexpected error in queue: {code}, {msg}")
            return False
    except Exception as e:
        _fail(f"Error reading error queue: {e}")
        return False


def test_config_terminals(smu: Keithley2400) -> bool:
    """Test 4: Query terminal selection."""
    _header("Test 4: Terminal Selection Query")
    try:
        terminals = smu.config.get_terminals()
        _info(f"Active terminals: {terminals}")
        _pass(f"Terminal query returned: {terminals}")
        return True
    except Exception as e:
        _fail(f"Error querying terminals: {e}")
        return False


def test_source_voltage_readback(smu: Keithley2400) -> bool:
    """Test 5: Configure a voltage source and read back the setting
    (output stays OFF -- no voltage is actually applied)."""
    _header("Test 5: Voltage Source Configuration (output OFF)")
    try:
        smu.reset()
        smu.source.set_function("VOLT")
        smu.source.set_voltage_mode("FIX")
        smu.source.set_voltage_range(20)
        smu.source.set_voltage(1.0)

        readback = smu.source.get_voltage()
        _info(f"Programmed 1.0 V, readback: {readback} V")

        if abs(readback - 1.0) < 1e-6:
            _pass("Voltage source readback matches programmed value.")
            return True
        else:
            _fail(f"Readback mismatch: expected 1.0, got {readback}")
            return False
    except Exception as e:
        _fail(f"Error: {e}")
        return False


def test_current_compliance_readback(smu: Keithley2400) -> bool:
    """Test 6: Set current compliance and read it back."""
    _header("Test 6: Current Compliance Readback")
    try:
        smu.measure.set_current_compliance(10e-3)
        readback = smu.measure.get_current_compliance()
        _info(f"Programmed 10 mA compliance, readback: {readback} A")

        if abs(readback - 10e-3) < 1e-6:
            _pass("Current compliance readback matches.")
            return True
        else:
            _fail(f"Readback mismatch: expected 0.01, got {readback}")
            return False
    except Exception as e:
        _fail(f"Error: {e}")
        return False


def test_source_voltage_measure_current(smu: Keithley2400) -> bool:
    """Test 7: Source 0 V, measure current (should read ~0 A with
    nothing connected, or a small leakage current).

    WARNING: This test turns the output ON briefly.
    """
    _header("Test 7: Source 0V / Measure Current (output ON)")
    try:
        smu.reset()
        smu.config.set_data_elements("VOLT", "CURR")
        data = smu.source_voltage(0.0, compliance=10e-3, measure="CURR")
        _info(f"Raw :READ? response: {data}")

        if len(data) >= 2:
            voltage = data[0]
            current = data[1]
            _info(f"Voltage: {voltage} V, Current: {current} A")
            _pass("Source-measure cycle completed successfully.")
            return True
        else:
            _fail(f"Unexpected data length: {len(data)}")
            return False
    except Exception as e:
        _fail(f"Error: {e}")
        return False


def test_source_current_measure_voltage(smu: Keithley2400) -> bool:
    """Test 8: Source 0 A, measure voltage.

    WARNING: This test turns the output ON briefly.
    """
    _header("Test 8: Source 0A / Measure Voltage (output ON)")
    try:
        smu.reset()
        smu.config.set_data_elements("VOLT", "CURR")
        data = smu.source_current(0.0, compliance=1.0, measure="VOLT")
        _info(f"Raw :READ? response: {data}")

        if len(data) >= 2:
            voltage = data[0]
            current = data[1]
            _info(f"Voltage: {voltage} V, Current: {current} A")
            _pass("Source-measure cycle completed successfully.")
            return True
        else:
            _fail(f"Unexpected data length: {len(data)}")
            return False
    except Exception as e:
        _fail(f"Error: {e}")
        return False


def test_data_format_elements(smu: Keithley2400) -> bool:
    """Test 9: Set data elements and verify readback."""
    _header("Test 9: Data Format Elements")
    try:
        smu.config.set_data_elements("VOLT", "CURR")
        readback = smu.config.get_data_elements()
        _info(f"Set VOLT,CURR -> readback: {readback}")

        if "VOLT" in readback and "CURR" in readback:
            _pass("Data elements configured correctly.")
            return True
        else:
            _fail(f"Unexpected readback: {readback}")
            return False
    except Exception as e:
        _fail(f"Error: {e}")
        return False


def test_nplc_readback(smu: Keithley2400) -> bool:
    """Test 10: Set NPLC and verify readback."""
    _header("Test 10: NPLC Speed Setting")
    try:
        smu.reset()
        smu.source.set_function("VOLT")
        smu.measure.set_function("CURR")
        smu.measure.set_nplc("CURR", 0.1)
        readback = smu.measure.get_nplc("CURR")
        _info(f"Set NPLC=0.1, readback: {readback}")

        if abs(readback - 0.1) < 0.01:
            _pass("NPLC readback matches.")
            return True
        else:
            _fail(f"NPLC mismatch: expected 0.1, got {readback}")
            return False
    except Exception as e:
        _fail(f"Error: {e}")
        return False


# ── main ────────────────────────────────────────────────────────────

def main() -> None:
    resource = sys.argv[1] if len(sys.argv) > 1 else "GPIB0::24::INSTR"
    print(f"Keithley 2400 Package Test")
    print(f"VISA resource: {resource}")

    tests = [
        test_connection,
        test_reset,
        test_error_queue,
        test_config_terminals,
        test_source_voltage_readback,
        test_current_compliance_readback,
        test_source_voltage_measure_current,
        test_source_current_measure_voltage,
        test_data_format_elements,
        test_nplc_readback,
    ]

    with Keithley2400(resource) as smu:
        passed = 0
        failed = 0

        for test_fn in tests:
            try:
                ok = test_fn(smu)
            except Exception as e:
                _fail(f"Unhandled exception in {test_fn.__name__}: {e}")
                ok = False

            if ok:
                passed += 1
            else:
                failed += 1

        # Always leave the instrument in a safe state
        smu.reset()

    _header("Summary")
    total = passed + failed
    print(f"  Passed: {passed}/{total}")
    print(f"  Failed: {failed}/{total}")
    print()

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
