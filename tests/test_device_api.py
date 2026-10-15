"""Tests for the device-API routes used by the edge-ml JavaScript and Dart
libraries: compact training request -> PipelineRequest, presets, API-key access
levels, and the ONNX / ExecuTorch download endpoints."""
import json
import os
import sys
import unittest
from types import SimpleNamespace

from bson.objectid import ObjectId

sys.path.insert(0, os.path.dirname(__file__))
from test_torch_executorch import (  # noqa: E402
    execute_pte, fast_params, make_model_doc, make_windower, make_windows, train_pipeline,
)

from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.DataModels.model import ModelStatus  # noqa: E402
from app.ml.device_presets import PRESETS  # noqa: E402
from app.ml.device_train import (  # noqa: E402
    STEPS, DeviceTrainError, DeviceTrainRequest, buildPipelineRequest, executorchWarning,
)
from app.ml.PipelineExport.Executorch.support import supportsExecutorch  # noqa: E402
from app.ml.Pipelines.PipelineContainer import PipelineContainer  # noqa: E402
from app.ml.Pipelines.Categories.FeatureExtraction.RawSensorExtractor import RawSensorExtractor  # noqa: E402
from app.ml.Pipelines.Categories.Normalizer.ZNormalizer import ZNormalizer  # noqa: E402
from app.ml.Pipelines.Categories.Classifier.TorchCNN1D import TorchCNN1D  # noqa: E402
from app.ml.Pipelines.Categories.FeatureExtraction.SimpleFeatureExtractor import SimpleFeatureExtractor  # noqa: E402
from app.ml.Pipelines.Categories.Normalizer.MinMaxNormalizer import MinMaxNormalizer  # noqa: E402
from app.ml.Pipelines.Categories.Classifier.random_forest import RandomForest  # noqa: E402
from app.routers import device  # noqa: E402

LABELING_ID = ObjectId()
OTHER_LABELING_ID = ObjectId()
WALK, RUN, IDLE = ObjectId(), ObjectId(), ObjectId()


def ts(name):
    return {"_id": ObjectId(), "name": name}


DATASETS = [
    {"_id": ObjectId(), "name": "ds1", "labelings": [{"labelingId": LABELING_ID}], "timeSeries": [ts("accX"), ts("accY"), ts("temp")]},
    {"_id": ObjectId(), "name": "ds2", "labelings": [{"labelingId": LABELING_ID}], "timeSeries": [ts("accY"), ts("accX")]},
    {"_id": ObjectId(), "name": "other", "labelings": [{"labelingId": OTHER_LABELING_ID}], "timeSeries": [ts("accX")]},
]
LABELINGS = [
    {"_id": LABELING_ID, "name": "activities", "labels": [
        {"_id": WALK, "name": "walk"}, {"_id": RUN, "name": "run"}, {"_id": IDLE, "name": "idle"}]},
    {"_id": OTHER_LABELING_ID, "name": "other", "labels": []},
]


def build(**kwargs):
    return buildPipelineRequest(DeviceTrainRequest(name="m", labeling="activities", **kwargs), DATASETS, LABELINGS)


class TestBuildPipelineRequest(unittest.TestCase):

    def test_defaults(self):
        req = build()
        # only datasets labeled with the labeling
        self.assertEqual([str(d.id) for d in req.datasets], [str(DATASETS[0]["_id"]), str(DATASETS[1]["_id"])])
        # shared time-series only, in the order of the first dataset, mapped per dataset
        ds1, ds2 = DATASETS[0]["timeSeries"], DATASETS[1]["timeSeries"]
        self.assertEqual(req.datasets[0].timeSeries, [ds1[0]["_id"], ds1[1]["_id"]])
        self.assertEqual(req.datasets[1].timeSeries, [ds2[1]["_id"], ds2[0]["_id"]])
        self.assertEqual(
            [s.options.name for s in req.selectedPipeline.steps],
            ["Sample based", "SimpleFeatureExtractor", "MinMaxNormalizer", "Random Forest Classifier", "TestTrainSplit"],
        )
        self.assertEqual(req.labeling.disabledLabelIDs, [])
        self.assertFalse(req.labeling.useZeroClass)

    def test_overrides_and_ids(self):
        req = build(
            datasets=[str(DATASETS[1]["_id"])],
            timeSeries=["accX"],
            disabledLabels=["idle", str(RUN)],
            useZeroClass=True,
            pipeline={
                "windowing": {"parameters": {"window_size": 7}},
                "classifier": {"name": "Decision Tree Classifier"},
            },
        )
        self.assertEqual(len(req.datasets), 1)
        self.assertEqual(req.labeling.disabledLabelIDs, [IDLE, RUN])
        self.assertTrue(req.labeling.useZeroClass)
        windowing = req.selectedPipeline.steps[0].options
        self.assertEqual(next(p.value for p in windowing.parameters if p.parameter_name == "window_size"), 7)
        self.assertEqual(req.selectedPipeline.steps[3].options.name, "Decision Tree Classifier")

    def test_errors(self):
        cases = [
            dict(pipeline={"classifier": {"name": "Nope"}}),
            dict(pipeline={"windowing": {"parameters": {"bogus": 1}}}),
            dict(pipeline={"notAStep": {}}),
            dict(datasets=["missing"]),
            dict(timeSeries=["temp"]),  # ds2 has no temp
            dict(disabledLabels=["sleep"]),
        ]
        for kwargs in cases:
            with self.subTest(kwargs=kwargs), self.assertRaises(DeviceTrainError):
                build(**kwargs)

    def test_unknown_labeling(self):
        with self.assertRaises(DeviceTrainError):
            buildPipelineRequest(DeviceTrainRequest(name="m", labeling="nope"), DATASETS, LABELINGS)


def step(req, key):
    options = req.selectedPipeline.steps[list(STEPS).index(key)].options
    return options.name, {p.parameter_name: p.value for p in options.parameters}


def option(req, key):
    """Instantiates the pipeline option the request selected for a step."""
    name, params = step(req, key)
    cls = next(o for o in STEPS[key][0].options if o.get_name() == name)
    return cls(fast_params(cls, params))


class TestPresets(unittest.TestCase):

    def test_preset_expands(self):
        req = build(preset="small_cnn")
        self.assertEqual(step(req, "featureExtraction")[0], "Raw Time-Series (Sensors only)")
        self.assertEqual(step(req, "normalizer")[0], "ZNormalizer")
        name, params = step(req, "classifier")
        self.assertEqual(name, "PyTorch 1D Convolutional Neural Network")
        self.assertEqual((params["conv_blocks"], params["base_filters"]), (1, 8))
        self.assertEqual(step(req, "windowing")[1]["window_size"], 50)
        self.assertEqual(step(req, "evaluation")[0], "TestTrainSplit")

    def test_overrides_merge_or_replace(self):
        # same option (unnamed) -> parameters merge with the preset's
        req = build(preset="large_cnn", pipeline={"classifier": {"parameters": {"epochs": 3}},
                                                  "windowing": {"parameters": {"window_size": 80}}})
        name, params = step(req, "classifier")
        self.assertEqual((params["conv_blocks"], params["base_filters"], params["epochs"]), (3, 32, 3))
        windowing = step(req, "windowing")[1]
        self.assertEqual((windowing["window_size"], windowing["sliding_step"]), (80, 25))
        # different option -> step replaced, preset parameters dropped
        req = build(preset="large_cnn", pipeline={"classifier": {"name": "PyTorch Dense Neural Network"}})
        self.assertEqual(step(req, "classifier")[0], "PyTorch Dense Neural Network")

    def test_unknown_preset(self):
        with self.assertRaises(DeviceTrainError) as ctx:
            build(preset="huge_cnn")
        self.assertIn("small_cnn", str(ctx.exception))

    def test_executorch_warning(self):
        self.assertIsNone(executorchWarning(DeviceTrainRequest(name="m", labeling="a", preset="small_dense")))
        # no preset -> no promise, no warning
        self.assertIsNone(executorchWarning(DeviceTrainRequest(name="m", labeling="a")))
        warning = executorchWarning(DeviceTrainRequest(
            name="m", labeling="a", preset="small_cnn",
            pipeline={"classifier": {"name": "Random Forest Classifier"}}))
        self.assertIn("PyTorch classifier", warning)

    def test_every_preset_exports_to_executorch(self):
        """Train each preset's steps briefly and compile + run the .pte."""
        import torch
        from app.ml.PipelineExport.Executorch.ExecutorchCompiler import buildExecutorchPte

        for preset_id in PRESETS:
            with self.subTest(preset=preset_id):
                req = build(preset=preset_id, pipeline={"classifier": {"parameters": {"epochs": 1}}})
                windower, fe, norm, clf = [option(req, key) for key in ["windowing", "featureExtraction", "normalizer", "classifier"]]
                window_size = int(windower.get_param_value_by_name("window_size"))

                X, y = make_windows(window=window_size)
                container = PipelineContainer(X, y, [None] * len(y))
                container = fe.fit_exec(container)
                container = norm.fit_exec(container)
                clf.fit_exec(container)
                options = [windower, fe, norm, clf]

                self.assertTrue(supportsExecutorch(options))
                model = make_model_doc(num_classes=clf.arch["num_classes"])
                pte = buildExecutorchPte(options, model)
                out = execute_pte(pte, torch.zeros(1, window_size, 3, dtype=torch.float32))
                self.assertEqual(tuple(out.shape), (1, clf.arch["num_classes"]))


class FakeCollection:
    def __init__(self, docs):
        self.docs = docs

    async def find_one(self, query):
        (key, value), = query.items()
        return next((d for d in self.docs if d.get(key) == value), None)


PROJECT = ObjectId()
KEYS = FakeCollection([{"readApiKey": "READ", "writeApiKey": "WRITE", "projectId": PROJECT}])


class TestDeviceRoutes(unittest.TestCase):

    def setUp(self):
        self.patches = {}
        self._patch("get_auth_db", lambda: SimpleNamespace(client={device.DEVICE_API_DB_NAME: {device.DEVICE_API_COLLNAME: KEYS}}))
        app = FastAPI()
        app.include_router(device.router, prefix="/ml/device")
        self.client = TestClient(app)

    def tearDown(self):
        for name, original in self.patches.items():
            setattr(device, name, original)

    def _patch(self, name, value):
        self.patches.setdefault(name, getattr(device, name))
        setattr(device, name, value)

    def test_key_access_levels(self):
        self.assertEqual(self.client.get("/ml/device/READ/pipelines").status_code, 200)
        self.assertEqual(self.client.get("/ml/device/WRITE/pipelines").status_code, 200)
        self.assertEqual(self.client.get("/ml/device/BAD/pipelines").status_code, 401)
        res = self.client.post("/ml/device/READ/train", json={"name": "m", "labeling": "activities"})
        self.assertEqual(res.status_code, 401)
        self.assertIn("write", res.json()["detail"])

    def test_train(self):
        calls = {}

        async def datasets(project):
            calls["project"] = project
            return DATASETS

        async def labelings(project):
            return LABELINGS

        async def preflight(req, project):
            return {"valid": True, "errors": [], "warnings": ["few windows"]}

        async def fake_train(req, project, background_tasks, preset=None):
            calls["req"] = req
            calls["preset"] = preset
            return ObjectId("0" * 24)

        self._patch("get_project_datasets_meta", datasets)
        self._patch("get_project_labelings", labelings)
        self._patch("preflight_train", preflight)
        self._patch("train", fake_train)

        res = self.client.post("/ml/device/WRITE/train", json={"name": "m", "labeling": "activities"})
        self.assertEqual(res.status_code, 200, res.text)
        self.assertEqual(res.json(), {"id": "0" * 24, "warnings": ["few windows"]})
        self.assertEqual(calls["project"], str(PROJECT))
        self.assertEqual(calls["req"].name, "m")

        res = self.client.post("/ml/device/WRITE/train", json={"name": "m", "labeling": "nope"})
        self.assertEqual(res.status_code, 400)

        res = self.client.post("/ml/device/WRITE/train", json={"name": "m", "labeling": "activities", "preset": "small_cnn"})
        self.assertEqual(res.status_code, 200, res.text)
        self.assertEqual(calls["preset"], "small_cnn")
        res = self.client.post("/ml/device/WRITE/train", json={
            "name": "m", "labeling": "activities", "preset": "small_cnn",
            "pipeline": {"classifier": {"name": "Decision Tree Classifier"}}})
        self.assertEqual(res.status_code, 200, res.text)
        self.assertIn("ExecuTorch", res.json()["warnings"][-1])
        res = self.client.post("/ml/device/WRITE/train", json={"name": "m", "labeling": "activities", "preset": "nope"})
        self.assertEqual(res.status_code, 400)

        async def failing_preflight(req, project):
            return {"valid": False, "errors": [{"step": "windowing", "message": "too big"}], "warnings": []}

        self._patch("preflight_train", failing_preflight)
        res = self.client.post("/ml/device/WRITE/train", json={"name": "m", "labeling": "activities"})
        self.assertEqual(res.status_code, 400)
        self.assertIn("windowing: too big", res.json()["detail"])

    def test_onnx_download(self):
        X, y = make_windows()
        options = [make_windower(), *train_pipeline(SimpleFeatureExtractor, MinMaxNormalizer, RandomForest, X, y)]
        model = make_model_doc()
        model.trainStatus = ModelStatus.done
        model.formats = ["ONNX"]
        self._patch("_get_model", lambda model_id, project: model)
        self._patch("getPipeline", lambda m: SimpleNamespace(options=options))

        res = self.client.get("/ml/device/READ/models/x/onnx/manifest.json")
        self.assertEqual(res.status_code, 200, res.text)
        self.assertEqual(res.json()["output"]["labels"], ["class_0", "class_1"])

        res = self.client.get("/ml/device/READ/models/x/onnx/model.onnx")
        self.assertEqual(res.status_code, 200)
        self.assertGreater(len(res.content), 100)

        model.formats = ["C"]
        self.assertEqual(self.client.get("/ml/device/READ/models/x/onnx/model.onnx").status_code, 400)
        model.trainStatus = ModelStatus.training
        self.assertEqual(self.client.get("/ml/device/READ/models/x/onnx/model.onnx").status_code, 409)

    def test_presets(self):
        res = self.client.get("/ml/device/READ/presets")
        self.assertEqual(res.status_code, 200)
        self.assertEqual([p["id"] for p in res.json()], list(PRESETS))
        self.assertEqual(self.client.get("/ml/device/BAD/presets").status_code, 401)

    def test_executorch_download(self):
        import torch
        from app.ml.PipelineExport.Executorch import ExecutorchCompiler

        X, y = make_windows()
        fe, norm, clf = train_pipeline(RawSensorExtractor, ZNormalizer, TorchCNN1D, X, y)
        options = [make_windower(), fe, norm, clf]
        model = make_model_doc(num_classes=clf.arch["num_classes"])
        model.id = "3" * 24
        model.trainStatus = ModelStatus.done
        model.formats = ["EXECUTORCH", "ONNX"]
        self._patch("_get_model", lambda model_id, project: model)
        self._patch("getPipeline", lambda m: SimpleNamespace(options=options))

        res = self.client.get("/ml/device/READ/models/x/executorch/manifest.json")
        self.assertEqual(res.status_code, 200, res.text)
        manifest = res.json()
        self.assertEqual(manifest["format"], "executorch")
        self.assertEqual(manifest["input"]["timeseries"], ["x", "y", "z"])
        self.assertEqual(manifest["output"]["labels"], ["class_0", "class_1"])

        # not precompiled -> compiled on request, and the result runs
        res = self.client.get("/ml/device/READ/models/x/executorch/model.pte")
        self.assertEqual(res.status_code, 200, res.text)
        out = execute_pte(res.content, torch.zeros(1, manifest["window"]["size"], 3))
        self.assertEqual(tuple(out.shape), (1, 2))

        # precompiled -> served from the cache
        ExecutorchCompiler.storeExecutorchPte(model, b"CACHED_PTE")
        self.assertEqual(self.client.get("/ml/device/READ/models/x/executorch/model.pte").content, b"CACHED_PTE")

        model.formats = ["ONNX"]
        res = self.client.get("/ml/device/READ/models/x/executorch/model.pte")
        self.assertEqual(res.status_code, 400)
        self.assertIn("preset", res.json()["detail"])
        model.trainStatus = ModelStatus.training
        self.assertEqual(self.client.get("/ml/device/READ/models/x/executorch/manifest.json").status_code, 409)


if __name__ == "__main__":
    unittest.main()
