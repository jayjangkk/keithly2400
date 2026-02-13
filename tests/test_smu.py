"""Tests for smu.py -- Keithley2400 facade integration tests."""

from unittest.mock import patch, MagicMock

import pytest

from keithley2400.smu import Keithley2400
from keithley2400.config import Config
from keithley2400.source import Source
from keithley2400.measure import Measure
from keithley2400.sweep import Sweep
from tests.conftest import MockConnection


def _make_smu(mock_conn: MockConnection) -> Keithley2400:
    """Build a Keithley2400 instance wired to a MockConnection,
    bypassing the real PyVISA resource manager."""
    smu = object.__new__(Keithley2400)
    smu.conn = mock_conn
    smu.config = Config(mock_conn)
    smu.source = Source(mock_conn)
    smu.measure = Measure(mock_conn)
    from keithley2400.trigger import Trigger
    from keithley2400.data import DataBuffer
    from keithley2400.status import Status
    smu.trigger = Trigger(mock_conn)
    smu.buffer = DataBuffer(mock_conn)
    smu.status = Status(mock_conn)
    smu.sweep = Sweep(
        mock_conn, smu.source, smu.measure, smu.trigger, smu.config,
    )
    return smu


class TestFacadeReset:
    def test_reset_sends_rst(self, mock_conn: MockConnection):
        smu = _make_smu(mock_conn)
        smu.reset()
        assert "*RST" in mock_conn.commands

    def test_identify(self, mock_conn: MockConnection):
        mock_conn.responses["*IDN?"] = "KEITHLEY,2400,SN001,C30"
        smu = _make_smu(mock_conn)
        assert smu.identify() == "KEITHLEY,2400,SN001,C30"


class TestSourceVoltageConvenience:
    def test_source_voltage_command_flow(self, mock_conn: MockConnection):
        mock_conn.responses[":READ?"] = "5.0,0.001"
        smu = _make_smu(mock_conn)

        result = smu.source_voltage(5.0, compliance=0.1)

        cmds = mock_conn.commands
        assert ":SOUR:FUNC VOLT" in cmds
        assert ":SOUR:VOLT:MODE FIX" in cmds
        assert ":SOUR:VOLT:LEV 5.000000E+00" in cmds
        assert ":SENS:CURR:PROT 1.000000E-01" in cmds
        assert ':SENS:FUNC "CURR"' in cmds
        assert ":OUTP ON" in cmds
        assert ":READ?" in cmds
        assert ":OUTP OFF" in cmds

    def test_source_voltage_returns_data(self, mock_conn: MockConnection):
        mock_conn.responses[":READ?"] = "5.0,0.001"
        smu = _make_smu(mock_conn)
        result = smu.source_voltage(5.0, compliance=0.1)
        assert result == pytest.approx([5.0, 0.001])

    def test_output_off_after_measurement(self, mock_conn: MockConnection):
        mock_conn.responses[":READ?"] = "1.0"
        smu = _make_smu(mock_conn)
        smu.source_voltage(1.0, compliance=0.1)

        read_idx = mock_conn.commands.index(":READ?")
        off_idx = mock_conn.commands.index(":OUTP OFF")
        assert off_idx > read_idx


class TestSourceCurrentConvenience:
    def test_source_current_command_flow(self, mock_conn: MockConnection):
        mock_conn.responses[":READ?"] = "3.3,0.001"
        smu = _make_smu(mock_conn)

        result = smu.source_current(1e-3, compliance=10.0)

        cmds = mock_conn.commands
        assert ":SOUR:FUNC CURR" in cmds
        assert ":SOUR:CURR:MODE FIX" in cmds
        assert ":SOUR:CURR:LEV 1.000000E-03" in cmds
        assert ":SENS:VOLT:PROT 1.000000E+01" in cmds
        assert ':SENS:FUNC "VOLT"' in cmds
        assert ":OUTP ON" in cmds
        assert ":READ?" in cmds
        assert ":OUTP OFF" in cmds

    def test_source_current_returns_data(self, mock_conn: MockConnection):
        mock_conn.responses[":READ?"] = "3.3,0.001"
        smu = _make_smu(mock_conn)
        result = smu.source_current(1e-3, compliance=10.0)
        assert result == pytest.approx([3.3, 0.001])


class TestFacadeSweepAccess:
    def test_sweep_is_accessible(self, mock_conn: MockConnection):
        smu = _make_smu(mock_conn)
        assert isinstance(smu.sweep, Sweep)

    def test_linear_sweep_via_facade(self, mock_conn: MockConnection):
        mock_conn.responses[":READ?"] = "0.0,1e-6,1.0,2e-6"
        smu = _make_smu(mock_conn)
        result = smu.sweep.voltage_sweep_linear(
            start=0, stop=1.0, step=1.0,
            compliance=0.1,
        )
        assert "voltage" in result
        assert "current" in result


class TestFacadeClose:
    def test_close_turns_off_output(self, mock_conn: MockConnection):
        smu = _make_smu(mock_conn)
        smu.close()
        assert ":OUTP OFF" in mock_conn.commands

    def test_context_manager(self, mock_conn: MockConnection):
        smu = _make_smu(mock_conn)
        smu.__enter__()
        smu.__exit__(None, None, None)
        assert ":OUTP OFF" in mock_conn.commands


class TestSubmoduleComposition:
    """Verify the facade wires all subsystems to the same connection."""

    def test_all_modules_share_connection(self, mock_conn: MockConnection):
        smu = _make_smu(mock_conn)
        # Access different subsystems -- all should route to the same conn
        smu.config.output_on()
        smu.source.set_function("VOLT")
        smu.measure.set_current_compliance(0.1)
        smu.trigger.set_trigger_count(10)
        smu.buffer.set_size(100)

        assert ":OUTP ON" in mock_conn.commands
        assert ":SOUR:FUNC VOLT" in mock_conn.commands
        assert ":SENS:CURR:PROT 1.000000E-01" in mock_conn.commands
        assert ":TRIG:COUN 10" in mock_conn.commands
        assert ":TRAC:POIN 100" in mock_conn.commands
