"""Tests for the Connection class (via MockConnection stand-in)."""

from tests.conftest import MockConnection


class TestMockConnectionBasics:
    """Verify that MockConnection itself behaves correctly -- these same
    assertions would apply to a real Connection talking to hardware."""

    def test_write_records_command(self, mock_conn: MockConnection):
        mock_conn.write(":OUTP ON")
        assert mock_conn.commands == [":OUTP ON"]

    def test_query_records_and_returns(self, mock_conn: MockConnection):
        mock_conn.responses["*IDN?"] = "KEITHLEY,2400,1234,C30"
        result = mock_conn.query("*IDN?")
        assert result == "KEITHLEY,2400,1234,C30"
        assert "*IDN?" in mock_conn.commands

    def test_query_ascii_values(self, mock_conn: MockConnection):
        mock_conn.responses[":READ?"] = "1.0,2.0,3.0"
        values = mock_conn.query_ascii_values(":READ?")
        assert values == [1.0, 2.0, 3.0]

    def test_reset_sends_rst(self, mock_conn: MockConnection):
        mock_conn.reset()
        assert "*RST" in mock_conn.commands

    def test_identify(self, mock_conn: MockConnection):
        mock_conn.responses["*IDN?"] = "KEITHLEY,2400,SN123,FW1.0"
        assert mock_conn.identify() == "KEITHLEY,2400,SN123,FW1.0"

    def test_clear_status(self, mock_conn: MockConnection):
        mock_conn.clear_status()
        assert "*CLS" in mock_conn.commands

    def test_context_manager(self):
        with MockConnection() as conn:
            conn.write(":OUTP OFF")
        # no exception means __exit__ succeeded
