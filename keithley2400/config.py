"""Layer 2: System configuration -- OUTPut, ROUTe, FORMat, SYSTem subsystems."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .connection import Connection


class Config:
    """Instrument-level configuration that doesn't belong to source or measure."""

    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    # -- output control (:OUTPut) ----------------------------------------

    def output_on(self) -> None:
        self._conn.write(":OUTP ON")

    def output_off(self) -> None:
        self._conn.write(":OUTP OFF")

    def is_output_on(self) -> bool:
        return self._conn.query(":OUTP?") == "1"

    def set_output_off_mode(self, mode: str) -> None:
        """Set output-off state.

        Parameters
        ----------
        mode : str
            ``"HIMP"`` (high-impedance), ``"NORM"`` (normal),
            ``"ZERO"``, or ``"GUAR"`` (guard).
        """
        self._conn.write(f":OUTP:SMOD {mode}")

    def get_output_off_mode(self) -> str:
        return self._conn.query(":OUTP:SMOD?")

    # -- terminal selection (:ROUTe) -------------------------------------

    def set_terminals(self, terminal: str) -> None:
        """Select front or rear terminals.

        Parameters
        ----------
        terminal : str
            ``"FRON"`` or ``"REAR"``.
        """
        self._conn.write(f":ROUT:TERM {terminal}")

    def get_terminals(self) -> str:
        return self._conn.query(":ROUT:TERM?")

    # -- remote sensing (:SYSTem:RSENse) ---------------------------------

    def set_four_wire(self, enable: bool) -> None:
        """Enable or disable 4-wire (remote) sensing."""
        state = "ON" if enable else "OFF"
        self._conn.write(f":SYST:RSEN {state}")

    def is_four_wire(self) -> bool:
        return self._conn.query(":SYST:RSEN?") == "1"

    # -- auto zero (:SYSTem:AZERo) ---------------------------------------

    def set_auto_zero(self, mode: str) -> None:
        """Control auto zero.

        Parameters
        ----------
        mode : str
            ``"ON"``, ``"OFF"``, or ``"ONCE"``.
        """
        self._conn.write(f":SYST:AZER:STAT {mode}")

    def get_auto_zero(self) -> str:
        return self._conn.query(":SYST:AZER:STAT?")

    # -- guard (:SYSTem:GUARd) -------------------------------------------

    def set_guard(self, mode: str) -> None:
        """Select guard type.

        Parameters
        ----------
        mode : str
            ``"OHMS"`` or ``"CABL"`` (cable).
        """
        self._conn.write(f":SYST:GUAR {mode}")

    def get_guard(self) -> str:
        return self._conn.query(":SYST:GUAR?")

    # -- data format (:FORMat) -------------------------------------------

    def set_data_elements(self, *elements: str) -> None:
        """Specify data elements included in response strings.

        Parameters
        ----------
        *elements : str
            One or more of ``"VOLT"``, ``"CURR"``, ``"RES"``,
            ``"TIME"``, ``"STAT"``.
        """
        elem_str = ",".join(elements)
        self._conn.write(f":FORM:ELEM {elem_str}")

    def get_data_elements(self) -> str:
        return self._conn.query(":FORM:ELEM?")

    # -- beeper (:SYSTem:BEEPer) -----------------------------------------

    def set_beeper(self, enable: bool) -> None:
        state = "ON" if enable else "OFF"
        self._conn.write(f":SYST:BEEP:STAT {state}")

    def is_beeper_on(self) -> bool:
        return self._conn.query(":SYST:BEEP:STAT?") == "1"
