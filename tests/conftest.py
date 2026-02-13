"""Shared fixtures -- MockConnection that records writes and returns
configurable query responses, so tests run without a real instrument."""

from __future__ import annotations

import pytest


class MockConnection:
    """Drop-in replacement for ``keithley2400.connection.Connection``.

    Attributes
    ----------
    commands : list[str]
        Every string passed to :meth:`write` is appended here, in order.
    responses : dict[str, str]
        Mapping of query command -> response string.  Tests pre-load
        this dict before calling the code under test.
    """

    def __init__(self) -> None:
        self.commands: list[str] = []
        self.responses: dict[str, str] = {}

    # -- core I/O --------------------------------------------------------

    def write(self, cmd: str) -> None:
        self.commands.append(cmd)

    def query(self, cmd: str) -> str:
        self.commands.append(cmd)
        return self.responses.get(cmd, "0")

    def query_ascii_values(
        self, cmd: str, separator: str = ","
    ) -> list[float]:
        self.commands.append(cmd)
        raw = self.responses.get(cmd, "")
        if not raw:
            return []
        return [float(v) for v in raw.split(separator)]

    # -- IEEE-488 helpers ------------------------------------------------

    def reset(self) -> None:
        self.write("*RST")

    def clear_status(self) -> None:
        self.write("*CLS")

    def identify(self) -> str:
        return self.query("*IDN?")

    def operation_complete(self) -> bool:
        return self.query("*OPC?") == "1"

    def wait(self) -> None:
        self.write("*WAI")

    def self_test(self) -> int:
        return int(self.query("*TST?"))

    def close(self) -> None:
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


@pytest.fixture
def mock_conn() -> MockConnection:
    """Provide a fresh ``MockConnection`` for each test."""
    return MockConnection()
