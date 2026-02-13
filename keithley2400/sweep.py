"""Layer 4: High-level sweep routines.

Each method orchestrates source, measure, trigger, and config modules
to execute a complete sweep and return parsed data.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .config import Config
    from .connection import Connection
    from .measure import Measure
    from .source import Source
    from .trigger import Trigger


class Sweep:
    """High-level sweep operations for the Keithley 2400."""

    def __init__(
        self,
        conn: Connection,
        source: Source,
        measure: Measure,
        trigger: Trigger,
        config: Config,
    ) -> None:
        self._conn = conn
        self._source = source
        self._measure = measure
        self._trigger = trigger
        self._config = config

    # -- linear staircase sweeps -----------------------------------------

    def voltage_sweep_linear(
        self,
        start: float,
        stop: float,
        step: float,
        compliance: float,
        delay: float = 0.1,
        nplc: float = 1.0,
    ) -> dict[str, list[float]]:
        """Linear voltage sweep, measuring current at each point.

        Follows the manual's programming example (Table 10-4).

        Returns
        -------
        dict
            ``{"voltage": [...], "current": [...]}``.
        """
        num_points = int(round(abs(stop - start) / abs(step))) + 1

        self._conn.reset()
        self._measure.set_concurrent(False)
        self._source.set_function("VOLT")
        self._measure.set_function("CURR:DC")
        self._measure.set_current_compliance(compliance)
        self._measure.set_nplc("CURR", nplc)

        # Configure sweep
        self._conn.write(f":SOUR:VOLT:START {start:E}")
        self._conn.write(f":SOUR:VOLT:STOP {stop:E}")
        self._conn.write(f":SOUR:VOLT:STEP {step:E}")
        self._source.set_voltage_mode("SWE")
        self._conn.write(":SOUR:SWE:RANG AUTO")
        self._conn.write(":SOUR:SWE:SPAC LIN")
        self._trigger.set_trigger_count(num_points)
        self._source.set_delay(delay)

        # Select data elements
        self._config.set_data_elements("VOLT", "CURR")

        # Execute
        self._config.output_on()
        raw = self._measure.read()
        self._config.output_off()

        return self._parse_two_element(raw, "voltage", "current")

    def current_sweep_linear(
        self,
        start: float,
        stop: float,
        step: float,
        compliance: float,
        delay: float = 0.1,
        nplc: float = 1.0,
    ) -> dict[str, list[float]]:
        """Linear current sweep, measuring voltage at each point.

        Returns
        -------
        dict
            ``{"voltage": [...], "current": [...]}``.
        """
        num_points = int(round(abs(stop - start) / abs(step))) + 1

        self._conn.reset()
        self._measure.set_concurrent(False)
        self._source.set_function("CURR")
        self._measure.set_function("VOLT:DC")
        self._measure.set_voltage_compliance(compliance)
        self._measure.set_nplc("VOLT", nplc)

        self._conn.write(f":SOUR:CURR:START {start:E}")
        self._conn.write(f":SOUR:CURR:STOP {stop:E}")
        self._conn.write(f":SOUR:CURR:STEP {step:E}")
        self._source.set_current_mode("SWE")
        self._conn.write(":SOUR:SWE:RANG AUTO")
        self._conn.write(":SOUR:SWE:SPAC LIN")
        self._trigger.set_trigger_count(num_points)
        self._source.set_delay(delay)

        self._config.set_data_elements("VOLT", "CURR")

        self._config.output_on()
        raw = self._measure.read()
        self._config.output_off()

        return self._parse_two_element(raw, "voltage", "current")

    # -- logarithmic staircase sweeps ------------------------------------

    def voltage_sweep_log(
        self,
        start: float,
        stop: float,
        points: int,
        compliance: float,
        delay: float = 0.1,
        nplc: float = 1.0,
    ) -> dict[str, list[float]]:
        """Logarithmic voltage sweep, measuring current at each point."""
        self._conn.reset()
        self._measure.set_concurrent(False)
        self._source.set_function("VOLT")
        self._measure.set_function("CURR:DC")
        self._measure.set_current_compliance(compliance)
        self._measure.set_nplc("CURR", nplc)

        self._conn.write(f":SOUR:VOLT:START {start:E}")
        self._conn.write(f":SOUR:VOLT:STOP {stop:E}")
        self._source.set_voltage_mode("SWE")
        self._conn.write(":SOUR:SWE:RANG AUTO")
        self._conn.write(":SOUR:SWE:SPAC LOG")
        self._conn.write(f":SOUR:SWE:POIN {points}")
        self._trigger.set_trigger_count(points)
        self._source.set_delay(delay)

        self._config.set_data_elements("VOLT", "CURR")

        self._config.output_on()
        raw = self._measure.read()
        self._config.output_off()

        return self._parse_two_element(raw, "voltage", "current")

    def current_sweep_log(
        self,
        start: float,
        stop: float,
        points: int,
        compliance: float,
        delay: float = 0.1,
        nplc: float = 1.0,
    ) -> dict[str, list[float]]:
        """Logarithmic current sweep, measuring voltage at each point."""
        self._conn.reset()
        self._measure.set_concurrent(False)
        self._source.set_function("CURR")
        self._measure.set_function("VOLT:DC")
        self._measure.set_voltage_compliance(compliance)
        self._measure.set_nplc("VOLT", nplc)

        self._conn.write(f":SOUR:CURR:START {start:E}")
        self._conn.write(f":SOUR:CURR:STOP {stop:E}")
        self._source.set_current_mode("SWE")
        self._conn.write(":SOUR:SWE:RANG AUTO")
        self._conn.write(":SOUR:SWE:SPAC LOG")
        self._conn.write(f":SOUR:SWE:POIN {points}")
        self._trigger.set_trigger_count(points)
        self._source.set_delay(delay)

        self._config.set_data_elements("VOLT", "CURR")

        self._config.output_on()
        raw = self._measure.read()
        self._config.output_off()

        return self._parse_two_element(raw, "voltage", "current")

    # -- custom (list) sweeps --------------------------------------------

    def voltage_sweep_list(
        self,
        voltages: list[float],
        compliance: float,
        delay: float = 0.1,
        nplc: float = 1.0,
    ) -> dict[str, list[float]]:
        """Custom voltage sweep from a list of arbitrary voltage values."""
        self._conn.reset()
        self._measure.set_concurrent(False)
        self._source.set_function("VOLT")
        self._measure.set_function("CURR:DC")
        self._measure.set_current_compliance(compliance)
        self._measure.set_nplc("CURR", nplc)

        self._source.set_voltage_mode("LIST")
        volt_str = ",".join(f"{v:E}" for v in voltages)
        self._conn.write(f":SOUR:LIST:VOLT {volt_str}")
        self._trigger.set_trigger_count(len(voltages))
        self._source.set_delay(delay)

        self._config.set_data_elements("VOLT", "CURR")

        self._config.output_on()
        raw = self._measure.read()
        self._config.output_off()

        return self._parse_two_element(raw, "voltage", "current")

    def current_sweep_list(
        self,
        currents: list[float],
        compliance: float,
        delay: float = 0.1,
        nplc: float = 1.0,
    ) -> dict[str, list[float]]:
        """Custom current sweep from a list of arbitrary current values."""
        self._conn.reset()
        self._measure.set_concurrent(False)
        self._source.set_function("CURR")
        self._measure.set_function("VOLT:DC")
        self._measure.set_voltage_compliance(compliance)
        self._measure.set_nplc("VOLT", nplc)

        self._source.set_current_mode("LIST")
        curr_str = ",".join(f"{c:E}" for c in currents)
        self._conn.write(f":SOUR:LIST:CURR {curr_str}")
        self._trigger.set_trigger_count(len(currents))
        self._source.set_delay(delay)

        self._config.set_data_elements("VOLT", "CURR")

        self._config.output_on()
        raw = self._measure.read()
        self._config.output_off()

        return self._parse_two_element(raw, "voltage", "current")

    # -- helpers ---------------------------------------------------------

    @staticmethod
    def _parse_two_element(
        raw: list[float], key_a: str, key_b: str
    ) -> dict[str, list[float]]:
        """Parse a flat list of [a0, b0, a1, b1, ...] into two lists."""
        a_vals = raw[0::2]
        b_vals = raw[1::2]
        return {key_a: a_vals, key_b: b_vals}
