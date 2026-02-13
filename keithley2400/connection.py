"""Layer 1: PyVISA communication wrapper for Keithley 2400 Series."""

from __future__ import annotations

import pyvisa


class Connection:
    """Low-level VISA resource wrapper.

    Every other module receives a ``Connection`` instance -- they never
    import ``pyvisa`` directly.  This makes it straightforward to swap
    in a mock for unit testing.
    """

    def __init__(
        self,
        resource_string: str,
        timeout_ms: int = 10_000,
        resource_manager: pyvisa.ResourceManager | None = None,
    ) -> None:
        self._rm = resource_manager or pyvisa.ResourceManager()
        self._inst = self._rm.open_resource(resource_string)
        self._inst.timeout = timeout_ms
        # Keithley 2400 uses \n as the read/write terminator
        self._inst.read_termination = "\n"
        self._inst.write_termination = "\n"

    # -- core I/O --------------------------------------------------------

    def write(self, cmd: str) -> None:
        """Send a SCPI command string."""
        self._inst.write(cmd)

    def query(self, cmd: str) -> str:
        """Send a SCPI query and return the stripped response string."""
        return self._inst.query(cmd).strip()

    def query_ascii_values(
        self, cmd: str, separator: str = ","
    ) -> list[float]:
        """Query and parse a comma-separated numeric response."""
        return self._inst.query_ascii_values(cmd, separator=separator)

    # -- common IEEE-488 commands ----------------------------------------

    def reset(self) -> None:
        """``*RST`` -- restore GPIB defaults."""
        self.write("*RST")

    def clear_status(self) -> None:
        """``*CLS`` -- clear status registers and error queue."""
        self.write("*CLS")

    def identify(self) -> str:
        """``*IDN?`` -- return manufacturer, model, serial, firmware."""
        return self.query("*IDN?")

    def operation_complete(self) -> bool:
        """``*OPC?`` -- block until all pending operations complete."""
        return self.query("*OPC?") == "1"

    def wait(self) -> None:
        """``*WAI`` -- wait-to-continue."""
        self.write("*WAI")

    def self_test(self) -> int:
        """``*TST?`` -- run self-test; returns 0 on pass."""
        return int(self.query("*TST?"))

    # -- lifecycle -------------------------------------------------------

    def close(self) -> None:
        """Close the VISA session."""
        self._inst.close()

    def __enter__(self) -> Connection:
        return self

    def __exit__(self, *exc) -> None:
        self.close()
