"""Tests for config.py -- output, terminals, sensing, format, etc."""

from keithley2400.config import Config
from tests.conftest import MockConnection


class TestOutput:
    def test_output_on(self, mock_conn: MockConnection):
        cfg = Config(mock_conn)
        cfg.output_on()
        assert ":OUTP ON" in mock_conn.commands

    def test_output_off(self, mock_conn: MockConnection):
        cfg = Config(mock_conn)
        cfg.output_off()
        assert ":OUTP OFF" in mock_conn.commands

    def test_is_output_on(self, mock_conn: MockConnection):
        mock_conn.responses[":OUTP?"] = "1"
        cfg = Config(mock_conn)
        assert cfg.is_output_on() is True

    def test_is_output_off(self, mock_conn: MockConnection):
        mock_conn.responses[":OUTP?"] = "0"
        cfg = Config(mock_conn)
        assert cfg.is_output_on() is False

    def test_set_output_off_mode(self, mock_conn: MockConnection):
        cfg = Config(mock_conn)
        cfg.set_output_off_mode("HIMP")
        assert ":OUTP:SMOD HIMP" in mock_conn.commands


class TestTerminals:
    def test_set_front(self, mock_conn: MockConnection):
        cfg = Config(mock_conn)
        cfg.set_terminals("FRON")
        assert ":ROUT:TERM FRON" in mock_conn.commands

    def test_set_rear(self, mock_conn: MockConnection):
        cfg = Config(mock_conn)
        cfg.set_terminals("REAR")
        assert ":ROUT:TERM REAR" in mock_conn.commands

    def test_get_terminals(self, mock_conn: MockConnection):
        mock_conn.responses[":ROUT:TERM?"] = "FRON"
        cfg = Config(mock_conn)
        assert cfg.get_terminals() == "FRON"


class TestSensing:
    def test_enable_four_wire(self, mock_conn: MockConnection):
        cfg = Config(mock_conn)
        cfg.set_four_wire(True)
        assert ":SYST:RSEN ON" in mock_conn.commands

    def test_disable_four_wire(self, mock_conn: MockConnection):
        cfg = Config(mock_conn)
        cfg.set_four_wire(False)
        assert ":SYST:RSEN OFF" in mock_conn.commands

    def test_query_four_wire(self, mock_conn: MockConnection):
        mock_conn.responses[":SYST:RSEN?"] = "1"
        cfg = Config(mock_conn)
        assert cfg.is_four_wire() is True


class TestAutoZero:
    def test_set_auto_zero_on(self, mock_conn: MockConnection):
        cfg = Config(mock_conn)
        cfg.set_auto_zero("ON")
        assert ":SYST:AZER:STAT ON" in mock_conn.commands

    def test_set_auto_zero_once(self, mock_conn: MockConnection):
        cfg = Config(mock_conn)
        cfg.set_auto_zero("ONCE")
        assert ":SYST:AZER:STAT ONCE" in mock_conn.commands


class TestDataFormat:
    def test_set_single_element(self, mock_conn: MockConnection):
        cfg = Config(mock_conn)
        cfg.set_data_elements("CURR")
        assert ":FORM:ELEM CURR" in mock_conn.commands

    def test_set_multiple_elements(self, mock_conn: MockConnection):
        cfg = Config(mock_conn)
        cfg.set_data_elements("VOLT", "CURR", "RES")
        assert ":FORM:ELEM VOLT,CURR,RES" in mock_conn.commands

    def test_get_data_elements(self, mock_conn: MockConnection):
        mock_conn.responses[":FORM:ELEM?"] = "VOLT,CURR"
        cfg = Config(mock_conn)
        assert cfg.get_data_elements() == "VOLT,CURR"


class TestGuard:
    def test_set_guard_cable(self, mock_conn: MockConnection):
        cfg = Config(mock_conn)
        cfg.set_guard("CABL")
        assert ":SYST:GUAR CABL" in mock_conn.commands

    def test_set_guard_ohms(self, mock_conn: MockConnection):
        cfg = Config(mock_conn)
        cfg.set_guard("OHMS")
        assert ":SYST:GUAR OHMS" in mock_conn.commands


class TestBeeper:
    def test_enable_beeper(self, mock_conn: MockConnection):
        cfg = Config(mock_conn)
        cfg.set_beeper(True)
        assert ":SYST:BEEP:STAT ON" in mock_conn.commands

    def test_disable_beeper(self, mock_conn: MockConnection):
        cfg = Config(mock_conn)
        cfg.set_beeper(False)
        assert ":SYST:BEEP:STAT OFF" in mock_conn.commands
