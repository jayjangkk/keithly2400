"""Layer 3a: Source control -- SOURce subsystem (fixed-level sourcing)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .connection import Connection


class Source:
    """Configure the voltage or current source."""

    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    # -- function selection ----------------------------------------------

    def set_function(self, func: str) -> None:
        """Select source function.

        Parameters
        ----------
        func : str
            ``"VOLT"`` or ``"CURR"``.
        """
        self._conn.write(f":SOUR:FUNC {func}")

    def get_function(self) -> str:
        return self._conn.query(":SOUR:FUNC?")

    # -- voltage source --------------------------------------------------

    def set_voltage(self, level: float) -> None:
        """Set V-source amplitude (volts)."""
        self._conn.write(f":SOUR:VOLT:LEV {level:E}")

    def get_voltage(self) -> float:
        return float(self._conn.query(":SOUR:VOLT:LEV?"))

    def set_voltage_range(self, range_val: float) -> None:
        self._conn.write(f":SOUR:VOLT:RANG {range_val:E}")

    def get_voltage_range(self) -> float:
        return float(self._conn.query(":SOUR:VOLT:RANG?"))

    def set_voltage_mode(self, mode: str) -> None:
        """Set V-source mode.

        Parameters
        ----------
        mode : str
            ``"FIX"`` (fixed), ``"SWE"`` (sweep), or ``"LIST"``.
        """
        self._conn.write(f":SOUR:VOLT:MODE {mode}")

    def get_voltage_mode(self) -> str:
        return self._conn.query(":SOUR:VOLT:MODE?")

    # -- current source --------------------------------------------------

    def set_current(self, level: float) -> None:
        """Set I-source amplitude (amps)."""
        self._conn.write(f":SOUR:CURR:LEV {level:E}")

    def get_current(self) -> float:
        return float(self._conn.query(":SOUR:CURR:LEV?"))

    def set_current_range(self, range_val: float) -> None:
        self._conn.write(f":SOUR:CURR:RANG {range_val:E}")

    def get_current_range(self) -> float:
        return float(self._conn.query(":SOUR:CURR:RANG?"))

    def set_current_mode(self, mode: str) -> None:
        """Set I-source mode.

        Parameters
        ----------
        mode : str
            ``"FIX"`` (fixed), ``"SWE"`` (sweep), or ``"LIST"``.
        """
        self._conn.write(f":SOUR:CURR:MODE {mode}")

    def get_current_mode(self) -> str:
        return self._conn.query(":SOUR:CURR:MODE?")

    # -- source delay ----------------------------------------------------

    def set_delay(self, seconds: float) -> None:
        """Set source settling delay (0 to 9999.999 s)."""
        self._conn.write(f":SOUR:DEL {seconds}")

    def get_delay(self) -> float:
        return float(self._conn.query(":SOUR:DEL?"))

    def set_auto_delay(self, enable: bool) -> None:
        state = "ON" if enable else "OFF"
        self._conn.write(f":SOUR:DEL:AUTO {state}")

    def is_auto_delay(self) -> bool:
        return self._conn.query(":SOUR:DEL:AUTO?") == "1"

    # -- voltage protection (limit) --------------------------------------

    def set_voltage_protection(self, volts: float) -> None:
        """Set V-source protection level (hardware voltage limit)."""
        self._conn.write(f":SOUR:VOLT:PROT {volts:E}")

    def get_voltage_protection(self) -> float:
        return float(self._conn.query(":SOUR:VOLT:PROT?"))

    def is_voltage_protection_tripped(self) -> bool:
        return self._conn.query(":SOUR:VOLT:PROT:TRIP?") == "1"
