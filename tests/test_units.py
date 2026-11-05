"""Unit-aware time-series: the catalog, how training resolves units across
datasets, the conversion applied while loading data, and the unit
information shipped with exports."""
import os
import sys
import unittest
from types import SimpleNamespace
from unittest import mock

import numpy as np
from bson import ObjectId

sys.path.insert(0, os.path.dirname(__file__))
import test_torch_executorch  # noqa: E402,F401  (configures the environment before app imports)

from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.DataProcessor.DataLoader import DataLoader  # noqa: E402
from app.routers import router  # noqa: E402
from app.units.catalog import QUANTITIES, catalog_json, conversion, get_quantity  # noqa: E402
from app.units.deploy import input_units  # noqa: E402
from app.units.resolve import InputUnit, UnitError, resolve_units  # noqa: E402


def ts(name, unit="", quantity=None):
    return SimpleNamespace(id=ObjectId(), name=name, unit=unit, quantity=quantity,
                           samplingRate=SimpleNamespace(mean=10.0, var=0.0))


def ds(name, *series):
    return SimpleNamespace(id=ObjectId(), name=name, timeSeries=list(series), metaData={}, labelings=[])


def convert(quantity, value, from_unit, to_unit):
    scale, offset = conversion(get_quantity(quantity), from_unit, to_unit)
    return value * scale + offset


class TestCatalog(unittest.TestCase):

    def test_known_conversions(self):
        self.assertAlmostEqual(convert("acceleration", 1, "g", "m/s^2"), 9.80665)
        self.assertAlmostEqual(convert("angular_velocity", np.pi, "rad/s", "deg/s"), 180)
        self.assertAlmostEqual(convert("temperature", 212, "degF", "degC"), 100)
        self.assertAlmostEqual(convert("temperature", 0, "degC", "K"), 273.15)
        self.assertAlmostEqual(convert("temperature", 300, "K", "degF"), 80.33, places=2)
        self.assertAlmostEqual(convert("pressure", 1, "atm", "hPa"), 1013.25)
        self.assertAlmostEqual(convert("magnetic_flux_density", 1, "G", "uT"), 100)
        self.assertAlmostEqual(convert("relative_humidity", 0.5, "fraction", "%"), 50)
        self.assertAlmostEqual(convert("voltage", 1500, "mV", "V"), 1.5)

    def test_every_default_unit_exists_and_ids_are_unique(self):
        for q in QUANTITIES:
            self.assertIsNotNone(q.unit(q.defaultUnit), q.id)
            ids = [u.id for u in q.units]
            self.assertEqual(len(ids), len(set(ids)), q.id)
            for u in q.units:
                # Round trip through the default unit is the identity.
                there = convert(q.id, 7.25, u.id, q.defaultUnit)
                self.assertAlmostEqual(convert(q.id, there, q.defaultUnit, u.id), 7.25, places=9)

    def test_aliases_resolve(self):
        self.assertEqual(get_quantity("acceleration").unit("m/s²").id, "m/s^2")
        self.assertEqual(get_quantity("magnetic_flux_density").unit("µT").id, "uT")

    def test_unknown_and_custom(self):
        self.assertIsNone(get_quantity(None))
        self.assertIsNone(get_quantity(""))
        self.assertIsNone(get_quantity("my strain gauge"))
        with self.assertRaises(ValueError):
            conversion(get_quantity("acceleration"), "furlong", "g")

    def test_required_quantities_present(self):
        ids = {q["id"] for q in catalog_json()["quantities"]}
        for required in ["acceleration", "angular_velocity", "angle", "temperature", "pressure",
                         "magnetic_flux_density", "relative_humidity", "voltage"]:
            self.assertIn(required, ids)

    def test_route_is_public(self):
        app = FastAPI()
        app.include_router(router, prefix="/ml")
        res = TestClient(app).get("/ml/units/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), catalog_json())


class TestResolveUnits(unittest.TestCase):

    def test_unknown_units_pass_through(self):
        a = ds("a", ts("accX", "m/s^2"), ts("temp"))
        b = ds("b", ts("accX", "m/s^2"), ts("temp"))
        inputs, conversions = resolve_units([a, b])
        self.assertEqual(conversions, {})
        self.assertEqual(inputs, [InputUnit(name="accX", unit="m/s^2"), InputUnit(name="temp", unit="")])

    def test_known_units_convert_to_default(self):
        a = ds("a", ts("accX", "g", "acceleration"), ts("temp", "degF", "temperature"))
        b = ds("b", ts("accX", "m/s^2", "acceleration"), ts("temp", "degC", "temperature"))
        inputs, conversions = resolve_units([a, b])
        self.assertEqual(inputs, [InputUnit(name="accX", quantity="acceleration", unit="m/s^2"),
                                  InputUnit(name="temp", quantity="temperature", unit="degC")])
        # Only the series that are not already in the default unit get converted.
        self.assertEqual(set(conversions), {(str(a.id), str(a.timeSeries[0].id)),
                                            (str(a.id), str(a.timeSeries[1].id))})
        self.assertAlmostEqual(conversions[(str(a.id), str(a.timeSeries[0].id))][0], 9.80665)

    def test_known_next_to_unknown_is_an_error(self):
        a = ds("a", ts("accX", "g", "acceleration"))
        b = ds("b", ts("accX", "g"))
        with self.assertRaisesRegex(UnitError, "accX"):
            resolve_units([a, b])

    def test_different_quantities_is_an_error(self):
        a = ds("a", ts("x", "deg", "angle"))
        b = ds("b", ts("x", "deg/s", "angular_velocity"))
        with self.assertRaises(UnitError):
            resolve_units([a, b])

    def test_custom_units_must_match(self):
        same = [ds("a", ts("strain", "ue", "strain")), ds("b", ts("strain", "ue", "strain"))]
        inputs, conversions = resolve_units(same)
        self.assertEqual(inputs, [InputUnit(name="strain", quantity="strain", unit="ue")])
        self.assertEqual(conversions, {})

        differ = [ds("a", ts("strain", "ue", "strain")), ds("b", ts("strain", "mV", "strain"))]
        with self.assertRaisesRegex(UnitError, "cannot convert"):
            resolve_units(differ)

    def test_builtin_quantity_with_custom_unit_is_not_converted(self):
        a = ds("a", ts("acc", "LSB", "acceleration"))
        b = ds("b", ts("acc", "LSB", "acceleration"))
        inputs, conversions = resolve_units([a, b])
        self.assertEqual(inputs, [InputUnit(name="acc", quantity="acceleration", unit="LSB")])
        self.assertEqual(conversions, {})


class TestConversionWhileLoading(unittest.TestCase):

    def test_process_datasets_applies_conversion(self):
        series = ts("acc", "g", "acceleration")
        d = ds("a", series)
        d.labelings = [SimpleNamespace(labelingId="L", labels=[])]
        stored = {"time": np.array([0, 100, 200]), "data": np.array([1.0, 0.5, -1.0])}

        class FakeStore:
            def __init__(self, _id):
                pass

            def loadSeries(self):
                pass

            def getFull(self):
                return stored

        req = SimpleNamespace(useZeroClass=False, id="L", disabledLabelIDs=[])
        _, conversions = resolve_units([d])
        with mock.patch.object(DataLoader, "BinaryStore", FakeStore):
            res, _, _ = DataLoader.processDatasets([d], req, {"x": 0}, conversions)
        np.testing.assert_allclose(res[0][:, 1], [9.80665, 4.903325, -9.80665])

        with mock.patch.object(DataLoader, "BinaryStore", FakeStore):
            res, _, _ = DataLoader.processDatasets([d], req, {"x": 0})
        np.testing.assert_allclose(res[0][:, 1], [1.0, 0.5, -1.0])


class TestDeployUnits(unittest.TestCase):

    def test_legacy_model_has_unknown_units(self):
        model = SimpleNamespace(inputUnits=None, timeSeries=["a", "b"])
        self.assertEqual(input_units(model), [
            {"name": "a", "quantity": None, "unit": "", "conversions": {}},
            {"name": "b", "quantity": None, "unit": "", "conversions": {}},
        ])

    def test_conversions_shipped_for_known_units(self):
        model = SimpleNamespace(timeSeries=["acc", "strain"], inputUnits=[
            InputUnit(name="acc", quantity="acceleration", unit="m/s^2"),
            InputUnit(name="strain", quantity="strain", unit="ue"),
        ])
        acc, strain = input_units(model)
        self.assertEqual(acc["conversions"]["m/s^2"], {"scale": 1.0, "offset": 0.0})
        self.assertAlmostEqual(acc["conversions"]["g"]["scale"], 9.80665)
        self.assertEqual(strain["conversions"], {})


if __name__ == "__main__":
    unittest.main()
