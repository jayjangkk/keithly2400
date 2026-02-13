"""Tests for measure.py -- compliance, range, NPLC, filter, read/fetch."""

import pytest

from keithley2400.measure import Measure
from tests.conftest import MockConnection


class TestMeasureFunction:
    def test_set_single_function(self, mock_conn: MockConnection):
        meas = Measure(mock_conn)
        meas.set_function("CURR:DC")
        assert ':SENS:FUNC "CURR:DC"' in mock_conn.commands

    def test_set_multiple_functions(self, mock_conn: MockConnection):
        meas = Measure(mock_conn)
        meas.set_function("VOLT:DC", "CURR:DC")
        assert ':SENS:FUNC "VOLT:DC","CURR:DC"' in mock_conn.commands

    def test_set_concurrent_on(self, mock_conn: MockConnection):
        meas = Measure(mock_conn)
        meas.set_concurrent(True)
        assert ":SENS:FUNC:CONC ON" in mock_conn.commands

    def test_set_concurrent_off(self, mock_conn: MockConnection):
        meas = Measure(mock_conn)
        meas.set_concurrent(False)
        assert ":SENS:FUNC:CONC OFF" in mock_conn.commands


class TestCompliance:
    def test_set_voltage_compliance(self, mock_conn: MockConnection):
        meas = Measure(mock_conn)
        meas.set_voltage_compliance(1.0)
        assert ":SENS:VOLT:PROT 1.000000E+00" in mock_conn.commands

    def test_get_voltage_compliance(self, mock_conn: MockConnection):
        mock_conn.responses[":SENS:VOLT:PROT?"] = "1.000000E+00"
        meas = Measure(mock_conn)
        assert meas.get_voltage_compliance() == 1.0

    def test_set_current_compliance(self, mock_conn: MockConnection):
        meas = Measure(mock_conn)
        meas.set_current_compliance(10e-3)
        assert ":SENS:CURR:PROT 1.000000E-02" in mock_conn.commands

    def test_get_current_compliance(self, mock_conn: MockConnection):
        mock_conn.responses[":SENS:CURR:PROT?"] = "1.000000E-02"
        meas = Measure(mock_conn)
        assert meas.get_current_compliance() == pytest.approx(0.01)

    def test_compliance_tripped_false(self, mock_conn: MockConnection):
        mock_conn.responses[":SENS:CURR:PROT:TRIP?"] = "0"
        meas = Measure(mock_conn)
        assert meas.is_current_compliance_tripped() is False

    def test_compliance_tripped_true(self, mock_conn: MockConnection):
        mock_conn.responses[":SENS:CURR:PROT:TRIP?"] = "1"
        meas = Measure(mock_conn)
        assert meas.is_current_compliance_tripped() is True


class TestRange:
    def test_set_voltage_range(self, mock_conn: MockConnection):
        meas = Measure(mock_conn)
        meas.set_voltage_range(20.0)
        assert ":SENS:VOLT:RANG 2.000000E+01" in mock_conn.commands

    def test_set_current_range(self, mock_conn: MockConnection):
        meas = Measure(mock_conn)
        meas.set_current_range(10e-3)
        assert ":SENS:CURR:RANG 1.000000E-02" in mock_conn.commands

    def test_set_auto_range(self, mock_conn: MockConnection):
        meas = Measure(mock_conn)
        meas.set_auto_range("CURR", True)
        assert ":SENS:CURR:RANG:AUTO ON" in mock_conn.commands

    def test_disable_auto_range(self, mock_conn: MockConnection):
        meas = Measure(mock_conn)
        meas.set_auto_range("VOLT", False)
        assert ":SENS:VOLT:RANG:AUTO OFF" in mock_conn.commands


class TestNPLC:
    def test_set_nplc_current(self, mock_conn: MockConnection):
        meas = Measure(mock_conn)
        meas.set_nplc("CURR", 1.0)
        assert ":SENS:CURR:NPLC 1.0" in mock_conn.commands

    def test_set_nplc_voltage(self, mock_conn: MockConnection):
        meas = Measure(mock_conn)
        meas.set_nplc("VOLT", 0.1)
        assert ":SENS:VOLT:NPLC 0.1" in mock_conn.commands

    def test_get_nplc(self, mock_conn: MockConnection):
        mock_conn.responses[":SENS:CURR:NPLC?"] = "1.000000"
        meas = Measure(mock_conn)
        assert meas.get_nplc("CURR") == pytest.approx(1.0)


class TestFilter:
    def test_enable_repeat_filter(self, mock_conn: MockConnection):
        meas = Measure(mock_conn)
        meas.set_filter(True, filter_type="REP", count=10)
        assert ":SENS:AVER:TCON REP" in mock_conn.commands
        assert ":SENS:AVER:COUN 10" in mock_conn.commands
        assert ":SENS:AVER ON" in mock_conn.commands

    def test_enable_moving_filter(self, mock_conn: MockConnection):
        meas = Measure(mock_conn)
        meas.set_filter(True, filter_type="MOV", count=20)
        assert ":SENS:AVER:TCON MOV" in mock_conn.commands
        assert ":SENS:AVER:COUN 20" in mock_conn.commands
        assert ":SENS:AVER ON" in mock_conn.commands

    def test_disable_filter(self, mock_conn: MockConnection):
        meas = Measure(mock_conn)
        meas.set_filter(False)
        assert ":SENS:AVER OFF" in mock_conn.commands


class TestReadings:
    def test_read_returns_values(self, mock_conn: MockConnection):
        mock_conn.responses[":READ?"] = "1.0E+00,2.5E-03,1.0E+04"
        meas = Measure(mock_conn)
        vals = meas.read()
        assert len(vals) == 3
        assert vals[0] == pytest.approx(1.0)
        assert vals[1] == pytest.approx(2.5e-3)
        assert vals[2] == pytest.approx(1.0e4)

    def test_fetch_returns_values(self, mock_conn: MockConnection):
        mock_conn.responses[":FETC?"] = "5.0,0.001"
        meas = Measure(mock_conn)
        vals = meas.fetch()
        assert len(vals) == 2

    def test_measure_with_function(self, mock_conn: MockConnection):
        mock_conn.responses[":MEAS:VOLT?"] = "3.3"
        meas = Measure(mock_conn)
        vals = meas.measure("VOLT")
        assert ":MEAS:VOLT?" in mock_conn.commands
        assert vals == [pytest.approx(3.3)]

    def test_measure_without_function(self, mock_conn: MockConnection):
        mock_conn.responses[":MEAS?"] = "1.0"
        meas = Measure(mock_conn)
        vals = meas.measure()
        assert ":MEAS?" in mock_conn.commands
