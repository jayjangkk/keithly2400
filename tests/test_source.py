"""Tests for source.py -- voltage/current source configuration."""

from keithley2400.source import Source
from tests.conftest import MockConnection


class TestSourceFunction:
    def test_set_voltage_function(self, mock_conn: MockConnection):
        src = Source(mock_conn)
        src.set_function("VOLT")
        assert ":SOUR:FUNC VOLT" in mock_conn.commands

    def test_set_current_function(self, mock_conn: MockConnection):
        src = Source(mock_conn)
        src.set_function("CURR")
        assert ":SOUR:FUNC CURR" in mock_conn.commands

    def test_get_function(self, mock_conn: MockConnection):
        mock_conn.responses[":SOUR:FUNC?"] = "VOLT"
        src = Source(mock_conn)
        assert src.get_function() == "VOLT"


class TestVoltageSource:
    def test_set_voltage(self, mock_conn: MockConnection):
        src = Source(mock_conn)
        src.set_voltage(10.0)
        assert ":SOUR:VOLT:LEV 1.000000E+01" in mock_conn.commands

    def test_set_voltage_small(self, mock_conn: MockConnection):
        src = Source(mock_conn)
        src.set_voltage(0.5)
        assert ":SOUR:VOLT:LEV 5.000000E-01" in mock_conn.commands

    def test_get_voltage(self, mock_conn: MockConnection):
        mock_conn.responses[":SOUR:VOLT:LEV?"] = "1.000000E+01"
        src = Source(mock_conn)
        assert src.get_voltage() == 10.0

    def test_set_voltage_range(self, mock_conn: MockConnection):
        src = Source(mock_conn)
        src.set_voltage_range(20.0)
        assert ":SOUR:VOLT:RANG 2.000000E+01" in mock_conn.commands

    def test_set_voltage_mode_fixed(self, mock_conn: MockConnection):
        src = Source(mock_conn)
        src.set_voltage_mode("FIX")
        assert ":SOUR:VOLT:MODE FIX" in mock_conn.commands

    def test_set_voltage_mode_sweep(self, mock_conn: MockConnection):
        src = Source(mock_conn)
        src.set_voltage_mode("SWE")
        assert ":SOUR:VOLT:MODE SWE" in mock_conn.commands


class TestCurrentSource:
    def test_set_current(self, mock_conn: MockConnection):
        src = Source(mock_conn)
        src.set_current(1e-3)
        assert ":SOUR:CURR:LEV 1.000000E-03" in mock_conn.commands

    def test_get_current(self, mock_conn: MockConnection):
        mock_conn.responses[":SOUR:CURR:LEV?"] = "1.000000E-03"
        src = Source(mock_conn)
        assert src.get_current() == pytest.approx(1e-3)

    def test_set_current_range(self, mock_conn: MockConnection):
        src = Source(mock_conn)
        src.set_current_range(10e-3)
        assert ":SOUR:CURR:RANG 1.000000E-02" in mock_conn.commands

    def test_set_current_mode_fixed(self, mock_conn: MockConnection):
        src = Source(mock_conn)
        src.set_current_mode("FIX")
        assert ":SOUR:CURR:MODE FIX" in mock_conn.commands


class TestSourceDelay:
    def test_set_delay(self, mock_conn: MockConnection):
        src = Source(mock_conn)
        src.set_delay(0.1)
        assert ":SOUR:DEL 0.1" in mock_conn.commands

    def test_get_delay(self, mock_conn: MockConnection):
        mock_conn.responses[":SOUR:DEL?"] = "0.100000"
        src = Source(mock_conn)
        assert src.get_delay() == pytest.approx(0.1)

    def test_auto_delay_on(self, mock_conn: MockConnection):
        src = Source(mock_conn)
        src.set_auto_delay(True)
        assert ":SOUR:DEL:AUTO ON" in mock_conn.commands

    def test_auto_delay_off(self, mock_conn: MockConnection):
        src = Source(mock_conn)
        src.set_auto_delay(False)
        assert ":SOUR:DEL:AUTO OFF" in mock_conn.commands


class TestVoltageProtection:
    def test_set_protection(self, mock_conn: MockConnection):
        src = Source(mock_conn)
        src.set_voltage_protection(40.0)
        assert ":SOUR:VOLT:PROT 4.000000E+01" in mock_conn.commands

    def test_is_tripped(self, mock_conn: MockConnection):
        mock_conn.responses[":SOUR:VOLT:PROT:TRIP?"] = "0"
        src = Source(mock_conn)
        assert src.is_voltage_protection_tripped() is False


import pytest  # noqa: E402 (used by pytest.approx above)
