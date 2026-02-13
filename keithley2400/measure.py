"""Layer 3b: Measure / Sense control -- SENSe subsystem + READ?/FETC?."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .connection import Connection


class Measure:
    """Configure measurement functions and acquire readings."""

    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    # -- function selection ----------------------------------------------

    def set_function(self, *funcs: str) -> None:
        """Enable one or more measurement functions.

        Parameters
        ----------
        *funcs : str
            ``"VOLT"`` / ``"VOLT:DC"``, ``"CURR"`` / ``"CURR:DC"``,
            ``"RES"`` / ``"RES"``.
        """
        func_list = ",".join(f'"{f}"' for f in funcs)
        self._conn.write(f":SENS:FUNC {func_list}")

    def get_function(self) -> str:
        return self._conn.query(":SENS:FUNC?")

    def set_concurrent(self, enable: bool) -> None:
        """Enable or disable concurrent (multi-function) measurements."""
        state = "ON" if enable else "OFF"
        self._conn.write(f":SENS:FUNC:CONC {state}")

    def is_concurrent(self) -> bool:
        return self._conn.query(":SENS:FUNC:CONC?") == "1"

    # -- compliance (protection) -----------------------------------------

    def set_voltage_compliance(self, volts: float) -> None:
        """Set voltage compliance limit for I-source."""
        self._conn.write(f":SENS:VOLT:PROT {volts:E}")

    def get_voltage_compliance(self) -> float:
        return float(self._conn.query(":SENS:VOLT:PROT?"))

    def is_voltage_compliance_tripped(self) -> bool:
        return self._conn.query(":SENS:VOLT:PROT:TRIP?") == "1"

    def set_current_compliance(self, amps: float) -> None:
        """Set current compliance limit for V-source."""
        self._conn.write(f":SENS:CURR:PROT {amps:E}")

    def get_current_compliance(self) -> float:
        return float(self._conn.query(":SENS:CURR:PROT?"))

    def is_current_compliance_tripped(self) -> bool:
        return self._conn.query(":SENS:CURR:PROT:TRIP?") == "1"

    # -- range -----------------------------------------------------------

    def set_voltage_range(self, range_val: float) -> None:
        self._conn.write(f":SENS:VOLT:RANG {range_val:E}")

    def get_voltage_range(self) -> float:
        return float(self._conn.query(":SENS:VOLT:RANG?"))

    def set_current_range(self, range_val: float) -> None:
        self._conn.write(f":SENS:CURR:RANG {range_val:E}")

    def get_current_range(self) -> float:
        return float(self._conn.query(":SENS:CURR:RANG?"))

    def set_resistance_range(self, range_val: float) -> None:
        self._conn.write(f":SENS:RES:RANG {range_val:E}")

    def set_auto_range(self, func: str, enable: bool) -> None:
        """Enable/disable auto range for a function.

        Parameters
        ----------
        func : str
            ``"VOLT"``, ``"CURR"``, or ``"RES"``.
        enable : bool
        """
        state = "ON" if enable else "OFF"
        self._conn.write(f":SENS:{func}:RANG:AUTO {state}")

    # -- speed (NPLC) ----------------------------------------------------

    def set_nplc(self, func: str, nplc: float) -> None:
        """Set integration rate in power-line cycles (0.01 to 10).

        Parameters
        ----------
        func : str
            ``"VOLT"``, ``"CURR"``, or ``"RES"``.
        nplc : float
        """
        self._conn.write(f":SENS:{func}:NPLC {nplc}")

    def get_nplc(self, func: str) -> float:
        return float(self._conn.query(f":SENS:{func}:NPLC?"))

    # -- filter ----------------------------------------------------------

    def set_filter(
        self,
        enable: bool,
        filter_type: str = "REP",
        count: int = 10,
    ) -> None:
        """Configure and enable/disable the digital averaging filter.

        Parameters
        ----------
        enable : bool
        filter_type : str
            ``"REP"`` (repeat) or ``"MOV"`` (moving).
        count : int
            Filter count (1 to 100).
        """
        self._conn.write(f":SENS:AVER:TCON {filter_type}")
        self._conn.write(f":SENS:AVER:COUN {count}")
        state = "ON" if enable else "OFF"
        self._conn.write(f":SENS:AVER {state}")

    # -- acquire readings ------------------------------------------------

    def read(self) -> list[float]:
        """:READ? -- trigger a measurement and return readings."""
        return self._conn.query_ascii_values(":READ?")

    def fetch(self) -> list[float]:
        """:FETC? -- return the most recent readings (no trigger)."""
        return self._conn.query_ascii_values(":FETC?")

    def measure(self, func: str | None = None) -> list[float]:
        """:MEAS? -- one-shot configure + read.

        Parameters
        ----------
        func : str or None
            If given, one of ``"VOLT"``, ``"CURR"``, ``"RES"``.
            If *None*, uses the currently configured function.
        """
        if func:
            cmd = f":MEAS:{func}?"
        else:
            cmd = ":MEAS?"
        return self._conn.query_ascii_values(cmd)
