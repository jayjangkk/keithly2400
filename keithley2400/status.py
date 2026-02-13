"""Layer 3: Status registers and error queue -- STATus / SYSTem:ERRor."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .connection import Connection


class Status:
    """Read status registers and manage the error queue."""

    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    # -- error queue -----------------------------------------------------

    def read_error(self) -> tuple[int, str]:
        """Read and clear the oldest error from the queue.

        Returns ``(0, "No error")`` when the queue is empty.
        """
        resp = self._conn.query(":SYST:ERR?")
        # Response format: <code>,"<message>"
        code_str, msg = resp.split(",", 1)
        return int(code_str), msg.strip().strip('"')

    def read_all_errors(self) -> list[tuple[int, str]]:
        """Drain the error queue and return all errors."""
        errors: list[tuple[int, str]] = []
        while True:
            code, msg = self.read_error()
            if code == 0:
                break
            errors.append((code, msg))
        return errors

    # -- clear -----------------------------------------------------------

    def clear(self) -> None:
        """``*CLS`` -- clear all status registers and the error queue."""
        self._conn.clear_status()

    # -- status byte / event register ------------------------------------

    def read_status_byte(self) -> int:
        """``*STB?`` -- read the status byte summary register."""
        return int(self._conn.query("*STB?"))

    def read_event_register(self) -> int:
        """``*ESR?`` -- read and clear the standard event register."""
        return int(self._conn.query("*ESR?"))

    # -- measurement event -----------------------------------------------

    def read_measurement_event(self) -> int:
        return int(self._conn.query(":STAT:MEAS?"))

    def set_measurement_enable(self, mask: int) -> None:
        self._conn.write(f":STAT:MEAS:ENAB {mask}")

    # -- operation event -------------------------------------------------

    def read_operation_event(self) -> int:
        return int(self._conn.query(":STAT:OPER?"))

    def set_operation_enable(self, mask: int) -> None:
        self._conn.write(f":STAT:OPER:ENAB {mask}")

    # -- questionable event ----------------------------------------------

    def read_questionable_event(self) -> int:
        return int(self._conn.query(":STAT:QUES?"))

    def set_questionable_enable(self, mask: int) -> None:
        self._conn.write(f":STAT:QUES:ENAB {mask}")

    # -- preset ----------------------------------------------------------

    def preset(self) -> None:
        """:STAT:PRES -- return status registers to default states."""
        self._conn.write(":STAT:PRES")
