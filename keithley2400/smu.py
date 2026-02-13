"""Facade: Keithley2400 -- single entry point that composes all sub-modules."""

from __future__ import annotations

from .config import Config
from .connection import Connection
from .data import DataBuffer
from .measure import Measure
from .source import Source
from .status import Status
from .sweep import Sweep
from .trigger import Trigger


class Keithley2400:
    """High-level driver for a single Keithley 2400 Series SourceMeter.

    Usage::

        with Keithley2400("GPIB0::24::INSTR") as smu:
            smu.reset()
            reading = smu.source_voltage(5.0, compliance=0.1)
            print(reading)
    """

    def __init__(
        self,
        resource_string: str = "GPIB0::24::INSTR",
        timeout_ms: int = 10_000,
    ) -> None:
        self.conn = Connection(resource_string, timeout_ms)
        self.config = Config(self.conn)
        self.source = Source(self.conn)
        self.measure = Measure(self.conn)
        self.trigger = Trigger(self.conn)
        self.buffer = DataBuffer(self.conn)
        self.status = Status(self.conn)
        self.sweep = Sweep(
            self.conn,
            self.source,
            self.measure,
            self.trigger,
            self.config,
        )

    # -- convenience shortcuts -------------------------------------------

    def reset(self) -> None:
        """``*RST`` -- restore GPIB default settings."""
        self.conn.reset()

    def identify(self) -> str:
        """``*IDN?`` -- query instrument identification."""
        return self.conn.identify()

    def source_voltage(
        self,
        volts: float,
        compliance: float,
        measure: str = "CURR",
    ) -> list[float]:
        """Source a fixed voltage and take a single measurement.

        Parameters
        ----------
        volts : float
            Voltage to source.
        compliance : float
            Current compliance limit (amps).
        measure : str
            Measurement function: ``"CURR"`` (default) or ``"RES"``.

        Returns
        -------
        list[float]
            Reading(s) as returned by ``:READ?`` with the currently
            configured ``:FORM:ELEM``.
        """
        self.source.set_function("VOLT")
        self.source.set_voltage_mode("FIX")
        self.source.set_voltage(volts)
        self.measure.set_current_compliance(compliance)
        self.measure.set_function(measure)
        self.config.output_on()
        data = self.measure.read()
        self.config.output_off()
        return data

    def source_current(
        self,
        amps: float,
        compliance: float,
        measure: str = "VOLT",
    ) -> list[float]:
        """Source a fixed current and take a single measurement.

        Parameters
        ----------
        amps : float
            Current to source.
        compliance : float
            Voltage compliance limit (volts).
        measure : str
            Measurement function: ``"VOLT"`` (default) or ``"RES"``.

        Returns
        -------
        list[float]
            Reading(s) as returned by ``:READ?``.
        """
        self.source.set_function("CURR")
        self.source.set_current_mode("FIX")
        self.source.set_current(amps)
        self.measure.set_voltage_compliance(compliance)
        self.measure.set_function(measure)
        self.config.output_on()
        data = self.measure.read()
        self.config.output_off()
        return data

    # -- lifecycle -------------------------------------------------------

    def close(self) -> None:
        """Turn output off and close the VISA connection."""
        self.config.output_off()
        self.conn.close()

    def __enter__(self) -> Keithley2400:
        return self

    def __exit__(self, *exc) -> None:
        self.close()
