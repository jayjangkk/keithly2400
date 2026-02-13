"""Layer 3: Trigger model control -- TRIGger, ARM, INITiate, ABORt."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .connection import Connection


class Trigger:
    """Configure the trigger model (arm layer + trigger layer)."""

    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    # -- initiate / abort ------------------------------------------------

    def initiate(self) -> None:
        """:INIT -- start the source-measure cycle."""
        self._conn.write(":INIT")

    def abort(self) -> None:
        """:ABOR -- abort a running source-measure cycle."""
        self._conn.write(":ABOR")

    # -- trigger layer ---------------------------------------------------

    def set_trigger_count(self, count: int) -> None:
        """Set trigger count (1 to 2500)."""
        self._conn.write(f":TRIG:COUN {count}")

    def get_trigger_count(self) -> int:
        return int(float(self._conn.query(":TRIG:COUN?")))

    def set_trigger_delay(self, seconds: float) -> None:
        """Set trigger delay (0 to 999.9999 s)."""
        self._conn.write(f":TRIG:DEL {seconds}")

    def get_trigger_delay(self) -> float:
        return float(self._conn.query(":TRIG:DEL?"))

    def set_trigger_source(self, source: str) -> None:
        """Set trigger layer control source.

        Parameters
        ----------
        source : str
            ``"IMM"`` (immediate) or ``"TLIN"`` (trigger link).
        """
        self._conn.write(f":TRIG:SOUR {source}")

    def get_trigger_source(self) -> str:
        return self._conn.query(":TRIG:SOUR?")

    # -- arm layer -------------------------------------------------------

    def set_arm_count(self, count: int) -> None:
        """Set arm count (1 to 2500, or use ``'INF'`` for infinite)."""
        self._conn.write(f":ARM:COUN {count}")

    def get_arm_count(self) -> int:
        resp = self._conn.query(":ARM:COUN?")
        val = float(resp)
        if val > 2500:
            return -1  # represents INFinite
        return int(val)

    def set_arm_source(self, source: str) -> None:
        """Set arm layer control source.

        Parameters
        ----------
        source : str
            ``"IMM"``, ``"TIM"``, ``"MAN"``, ``"BUS"``, ``"TLIN"``,
            ``"NST"``, ``"PST"``, ``"BST"``.
        """
        self._conn.write(f":ARM:SOUR {source}")

    def get_arm_source(self) -> str:
        return self._conn.query(":ARM:SOUR?")

    def set_arm_timer(self, seconds: float) -> None:
        """Set arm timer interval (0.001 to 99999.99 s)."""
        self._conn.write(f":ARM:TIM {seconds}")

    def get_arm_timer(self) -> float:
        return float(self._conn.query(":ARM:TIM?"))
