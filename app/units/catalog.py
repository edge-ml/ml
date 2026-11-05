"""Catalog of physical quantities and units for time-series.

Every unit is defined by an affine map onto its quantity's base unit:
``base = value * scale + offset``. Converting between two units of the same
quantity is therefore always affine as well (see ``conversion``).

Each quantity also names a ``defaultUnit``: the unit training converts its
data to, and therefore the unit a model expects as input.

A time-series carries ``quantity`` and ``unit`` strings. ``quantity`` is
empty when unknown (e.g. every dataset uploaded before units existed),
a catalog id for a built-in quantity, or any other string for a custom
quantity. Only built-in quantities with catalog units are converted.
"""

from dataclasses import dataclass
from math import pi
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class Unit:
    id: str
    label: str
    scale: float
    offset: float = 0.0
    aliases: Tuple[str, ...] = ()


@dataclass(frozen=True)
class Quantity:
    id: str
    label: str
    defaultUnit: str
    units: Tuple[Unit, ...]

    def unit(self, unit_id: str) -> Optional[Unit]:
        for u in self.units:
            if u.id == unit_id or unit_id in u.aliases:
                return u
        return None


G = 9.80665

QUANTITIES: Tuple[Quantity, ...] = (
    Quantity("acceleration", "Acceleration", "m/s^2", (
        Unit("m/s^2", "m/s²", 1.0, aliases=("m/s²", "m/s2")),
        Unit("g", "g", G),
        Unit("mg", "mg", G / 1000),
        Unit("cm/s^2", "cm/s²", 0.01, aliases=("cm/s²", "Gal")),
    )),
    Quantity("angular_velocity", "Angular velocity", "deg/s", (
        Unit("deg/s", "°/s", 1.0, aliases=("°/s", "dps")),
        Unit("rad/s", "rad/s", 180 / pi),
        Unit("rpm", "rpm", 6.0),
    )),
    Quantity("angle", "Angle", "deg", (
        Unit("deg", "°", 1.0, aliases=("°",)),
        Unit("rad", "rad", 180 / pi),
    )),
    Quantity("temperature", "Temperature", "degC", (
        Unit("degC", "°C", 1.0, aliases=("°C", "C")),
        Unit("K", "K", 1.0, -273.15),
        Unit("degF", "°F", 5 / 9, -160 / 9, aliases=("°F", "F")),
    )),
    Quantity("pressure", "Pressure", "hPa", (
        Unit("Pa", "Pa", 1.0),
        Unit("hPa", "hPa", 100.0),
        Unit("kPa", "kPa", 1000.0),
        Unit("mbar", "mbar", 100.0),
        Unit("bar", "bar", 1e5),
        Unit("atm", "atm", 101325.0),
        Unit("psi", "psi", 6894.757293168),
        Unit("mmHg", "mmHg", 133.322387415),
    )),
    Quantity("magnetic_flux_density", "Magnetic flux density", "uT", (
        Unit("T", "T", 1.0),
        Unit("mT", "mT", 1e-3),
        Unit("uT", "µT", 1e-6, aliases=("µT", "μT")),
        Unit("nT", "nT", 1e-9),
        Unit("G", "G (gauss)", 1e-4, aliases=("gauss",)),
        Unit("mG", "mG", 1e-7),
    )),
    Quantity("relative_humidity", "Relative humidity", "%", (
        Unit("%", "%", 1.0, aliases=("%RH",)),
        Unit("fraction", "fraction (0–1)", 100.0),
    )),
    Quantity("voltage", "Voltage", "V", (
        Unit("V", "V", 1.0),
        Unit("mV", "mV", 1e-3),
        Unit("uV", "µV", 1e-6, aliases=("µV", "μV")),
        Unit("kV", "kV", 1e3),
    )),
    Quantity("current", "Electric current", "mA", (
        Unit("A", "A", 1.0),
        Unit("mA", "mA", 1e-3),
        Unit("uA", "µA", 1e-6, aliases=("µA", "μA")),
    )),
    Quantity("length", "Length / distance", "m", (
        Unit("m", "m", 1.0),
        Unit("cm", "cm", 0.01),
        Unit("mm", "mm", 0.001),
        Unit("km", "km", 1000.0),
        Unit("in", "in", 0.0254),
        Unit("ft", "ft", 0.3048),
    )),
    Quantity("velocity", "Velocity", "m/s", (
        Unit("m/s", "m/s", 1.0),
        Unit("km/h", "km/h", 1 / 3.6),
        Unit("mph", "mph", 0.44704),
        Unit("kn", "kn", 1852 / 3600),
    )),
    Quantity("frequency", "Frequency / rate", "Hz", (
        Unit("Hz", "Hz", 1.0),
        Unit("kHz", "kHz", 1000.0),
        Unit("bpm", "bpm (per minute)", 1 / 60, aliases=("1/min",)),
    )),
    Quantity("illuminance", "Illuminance", "lx", (
        Unit("lx", "lx", 1.0, aliases=("lux",)),
    )),
    Quantity("sound_level", "Sound level", "dB", (
        Unit("dB", "dB", 1.0, aliases=("dBA", "dB(A)")),
    )),
    Quantity("mass", "Mass", "kg", (
        Unit("kg", "kg", 1.0),
        Unit("g", "g", 1e-3),
    )),
    Quantity("force", "Force", "N", (
        Unit("N", "N", 1.0),
        Unit("kN", "kN", 1e3),
    )),
    Quantity("power", "Power", "W", (
        Unit("W", "W", 1.0),
        Unit("mW", "mW", 1e-3),
        Unit("kW", "kW", 1e3),
    )),
    Quantity("time", "Duration", "s", (
        Unit("s", "s", 1.0),
        Unit("ms", "ms", 1e-3),
        Unit("us", "µs", 1e-6, aliases=("µs", "μs")),
    )),
    Quantity("ratio", "Ratio / dimensionless", "1", (
        Unit("1", "1 (unitless)", 1.0, aliases=("",)),
        Unit("%", "%", 0.01),
    )),
)

_BY_ID: Dict[str, Quantity] = {q.id: q for q in QUANTITIES}


def get_quantity(quantity_id: Optional[str]) -> Optional[Quantity]:
    """The built-in quantity for an id, or None for unknown/custom ones."""
    if not quantity_id:
        return None
    return _BY_ID.get(quantity_id)


def conversion(quantity: Quantity, from_unit: str, to_unit: str) -> Tuple[float, float]:
    """(scale, offset) such that ``to = from * scale + offset``."""
    a = quantity.unit(from_unit)
    b = quantity.unit(to_unit)
    if a is None or b is None:
        raise ValueError(f"No conversion from '{from_unit}' to '{to_unit}' for {quantity.label}")
    return a.scale / b.scale, (a.offset - b.offset) / b.scale


def catalog_json() -> dict:
    """The catalog as served to the web app and the client libraries."""
    return {
        "version": 1,
        "quantities": [
            {
                "id": q.id,
                "label": q.label,
                "defaultUnit": q.defaultUnit,
                "units": [
                    {"id": u.id, "label": u.label, "scale": u.scale, "offset": u.offset,
                     "aliases": list(u.aliases)}
                    for u in q.units
                ],
            }
            for q in QUANTITIES
        ],
    }


def quantity_ids() -> List[str]:
    return [q.id for q in QUANTITIES]
