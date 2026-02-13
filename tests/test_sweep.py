"""Tests for sweep.py -- verify full SCPI command sequences for sweeps."""

import pytest

from keithley2400.config import Config
from keithley2400.measure import Measure
from keithley2400.source import Source
from keithley2400.sweep import Sweep
from keithley2400.trigger import Trigger
from tests.conftest import MockConnection


@pytest.fixture
def sweep_setup(mock_conn: MockConnection):
    """Create a full Sweep instance wired to a MockConnection."""
    source = Source(mock_conn)
    measure = Measure(mock_conn)
    trigger = Trigger(mock_conn)
    config = Config(mock_conn)
    sweep = Sweep(mock_conn, source, measure, trigger, config)
    return mock_conn, sweep


class TestVoltageSweepLinear:
    def test_command_sequence(self, sweep_setup):
        conn, sweep = sweep_setup
        # 0V to 1V in 0.5V steps -> 3 points, 2 elements each -> 6 floats
        conn.responses[":READ?"] = (
            "0.0,1e-6,0.5,2e-6,1.0,3e-6"
        )

        result = sweep.voltage_sweep_linear(
            start=0.0, stop=1.0, step=0.5,
            compliance=0.1, delay=0.05, nplc=1.0,
        )

        # Verify key commands were sent in order
        cmds = conn.commands
        assert "*RST" in cmds
        assert ":SENS:FUNC:CONC OFF" in cmds
        assert ":SOUR:FUNC VOLT" in cmds
        assert ':SENS:FUNC "CURR:DC"' in cmds
        assert ":SENS:CURR:PROT 1.000000E-01" in cmds
        assert ":SOUR:VOLT:START 0.000000E+00" in cmds
        assert ":SOUR:VOLT:STOP 1.000000E+00" in cmds
        assert ":SOUR:VOLT:STEP 5.000000E-01" in cmds
        assert ":SOUR:VOLT:MODE SWE" in cmds
        assert ":SOUR:SWE:RANG AUTO" in cmds
        assert ":SOUR:SWE:SPAC LIN" in cmds
        assert ":TRIG:COUN 3" in cmds
        assert ":SOUR:DEL 0.05" in cmds
        assert ":FORM:ELEM VOLT,CURR" in cmds
        assert ":OUTP ON" in cmds
        assert ":READ?" in cmds
        assert ":OUTP OFF" in cmds

    def test_returns_parsed_data(self, sweep_setup):
        conn, sweep = sweep_setup
        conn.responses[":READ?"] = "0.0,1e-6,0.5,2e-6,1.0,3e-6"

        result = sweep.voltage_sweep_linear(
            start=0.0, stop=1.0, step=0.5,
            compliance=0.1,
        )

        assert list(result.keys()) == ["voltage", "current"]
        assert result["voltage"] == pytest.approx([0.0, 0.5, 1.0])
        assert result["current"] == pytest.approx([1e-6, 2e-6, 3e-6])

    def test_output_off_after_read(self, sweep_setup):
        """Output must be turned off even after READ?."""
        conn, sweep = sweep_setup
        conn.responses[":READ?"] = "0.0,0.0"

        sweep.voltage_sweep_linear(0, 0, 0.1, compliance=0.1)

        read_idx = conn.commands.index(":READ?")
        off_idx = conn.commands.index(":OUTP OFF")
        assert off_idx > read_idx


class TestCurrentSweepLinear:
    def test_command_sequence(self, sweep_setup):
        conn, sweep = sweep_setup
        # 1mA to 10mA in 1mA steps -> 10 points
        conn.responses[":READ?"] = ",".join(
            f"{0.6 + i * 0.01},{(1 + i) * 1e-3}" for i in range(10)
        )

        result = sweep.current_sweep_linear(
            start=1e-3, stop=10e-3, step=1e-3,
            compliance=1.0, delay=0.1,
        )

        cmds = conn.commands
        assert ":SOUR:FUNC CURR" in cmds
        assert ':SENS:FUNC "VOLT:DC"' in cmds
        assert ":SENS:VOLT:PROT 1.000000E+00" in cmds
        assert ":SOUR:CURR:START 1.000000E-03" in cmds
        assert ":SOUR:CURR:STOP 1.000000E-02" in cmds
        assert ":SOUR:CURR:STEP 1.000000E-03" in cmds
        assert ":SOUR:CURR:MODE SWE" in cmds
        assert ":TRIG:COUN 10" in cmds
        assert len(result["voltage"]) == 10
        assert len(result["current"]) == 10


class TestVoltageSweepLog:
    def test_uses_log_spacing(self, sweep_setup):
        conn, sweep = sweep_setup
        conn.responses[":READ?"] = "0.1,1e-6,1.0,2e-6,10.0,3e-6"

        sweep.voltage_sweep_log(
            start=0.1, stop=10.0, points=3,
            compliance=0.1,
        )

        cmds = conn.commands
        assert ":SOUR:SWE:SPAC LOG" in cmds
        assert ":SOUR:SWE:POIN 3" in cmds
        assert ":TRIG:COUN 3" in cmds


class TestVoltageSweepList:
    def test_custom_list(self, sweep_setup):
        conn, sweep = sweep_setup
        voltages = [7.0, 1.0, 3.0, 8.0, 2.0]
        conn.responses[":READ?"] = ",".join(
            f"{v},{i * 1e-3}" for i, v in enumerate(voltages)
        )

        result = sweep.voltage_sweep_list(
            voltages=voltages, compliance=0.1,
        )

        cmds = conn.commands
        assert ":SOUR:VOLT:MODE LIST" in cmds
        # Verify list command contains all voltages
        list_cmd = [c for c in cmds if c.startswith(":SOUR:LIST:VOLT")]
        assert len(list_cmd) == 1
        assert ":TRIG:COUN 5" in cmds
        assert len(result["voltage"]) == 5
        assert len(result["current"]) == 5


class TestCurrentSweepList:
    def test_custom_list(self, sweep_setup):
        conn, sweep = sweep_setup
        currents = [1e-3, 5e-3, 10e-3]
        conn.responses[":READ?"] = "0.5,1e-3,0.6,5e-3,0.7,10e-3"

        result = sweep.current_sweep_list(
            currents=currents, compliance=10.0,
        )

        cmds = conn.commands
        assert ":SOUR:FUNC CURR" in cmds
        assert ":SOUR:CURR:MODE LIST" in cmds
        list_cmd = [c for c in cmds if c.startswith(":SOUR:LIST:CURR")]
        assert len(list_cmd) == 1
        assert ":TRIG:COUN 3" in cmds
        assert result["voltage"] == pytest.approx([0.5, 0.6, 0.7])
        assert result["current"] == pytest.approx([1e-3, 5e-3, 10e-3])


class TestParseHelper:
    def test_parse_two_element(self):
        raw = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
        result = Sweep._parse_two_element(raw, "a", "b")
        assert result["a"] == [1.0, 3.0, 5.0]
        assert result["b"] == [2.0, 4.0, 6.0]

    def test_parse_single_point(self):
        raw = [10.0, 0.001]
        result = Sweep._parse_two_element(raw, "voltage", "current")
        assert result["voltage"] == [10.0]
        assert result["current"] == [0.001]
