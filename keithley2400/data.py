"""Layer 3: Data buffer -- TRACe subsystem."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .connection import Connection


class DataBuffer:
    """Configure and read the internal data store (trace buffer)."""

    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    def set_size(self, points: int) -> None:
        """Set buffer size (1 to 2500 readings)."""
        self._conn.write(f":TRAC:POIN {points}")

    def get_size(self) -> int:
        return int(float(self._conn.query(":TRAC:POIN?")))

    def clear(self) -> None:
        """Clear all readings from the buffer."""
        self._conn.write(":TRAC:CLE")

    def get_free(self) -> str:
        """Query bytes available and bytes in use."""
        return self._conn.query(":TRAC:FREE?")

    def set_feed(self, source: str) -> None:
        """Select the source of readings for the buffer.

        Parameters
        ----------
        source : str
            ``"SENS"`` (SENSe), ``"CALC"`` (CALCulate1), or
            ``"CALC2"`` (CALCulate2).
        """
        self._conn.write(f":TRAC:FEED {source}")

    def set_control(self, mode: str) -> None:
        """Set buffer control mode.

        Parameters
        ----------
        mode : str
            ``"NEXT"`` -- fill buffer then stop.
            ``"NEV"``  -- buffer storage disabled.
        """
        self._conn.write(f":TRAC:CONT {mode}")

    def get_control(self) -> str:
        return self._conn.query(":TRAC:CONT?")

    def read(self) -> list[float]:
        """Read all data from the buffer."""
        return self._conn.query_ascii_values(":TRAC:DATA?")

    def get_count(self) -> int:
        """Query the number of readings stored in the buffer."""
        return int(float(self._conn.query(":TRAC:POIN:ACT?")))

    def set_timestamp_format(self, fmt: str) -> None:
        """Select timestamp format.

        Parameters
        ----------
        fmt : str
            ``"ABS"`` (absolute) or ``"DELT"`` (delta).
        """
        self._conn.write(f":TRAC:TST:FORM {fmt}")

    def get_timestamp_format(self) -> str:
        return self._conn.query(":TRAC:TST:FORM?")
