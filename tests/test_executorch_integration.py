"""End-to-end integration tests for the ExecuTorch feature and its review fixes.

Unlike test_torch_executorch.py (which exercises the compiler in isolation),
these drive the real seams the running service uses:
- the full Model document round-trip (persist -> Mongo-shaped doc -> restore)
- Pipeline.export platform dispatch (C vs EXECUTORCH)
- the train-time precompile+cache -> download reuse path
- the deploy route handler's status-code mapping (200 / 400 / 501)

Run from ml/:  FLATC_EXECUTABLE=.../flatc pytest tests/test_executorch_integration.py -v
"""

import asyncio
import json
import os
import tempfile
import zipfile
from io import BytesIO
from types import SimpleNamespace

# Reuse the env bootstrap + helpers from the unit test module.
from tests.test_torch_executorch import (  # noqa: E402
    WINDOW_SIZE,
    N_SENSORS,
    execute_pte,
    get_file,
    make_model_doc,
    make_windows,
    make_windower,
    run_python_pipeline,
    train_pipeline,
)

import numpy as np  # noqa: E402
import torch  # noqa: E402

from app.ml.BaseConfig import Platforms  # noqa: E402
from app.ml.Pipeline import Pipeline  # noqa: E402
from app.ml.Pipelines import getCategory  # noqa: E402
from app.Deploy.Base import downloadModel  # noqa: E402
from app.DataModels.PipelineRequest import PipelineStepOption  # noqa: E402
from app.ml.Pipelines.Categories.Normalizer.ZNormalizer import ZNormalizer  # noqa: E402
from app.ml.Pipelines.Categories.Normalizer.MinMaxNormalizer import MinMaxNormalizer  # noqa: E402
from app.ml.Pipelines.Categories.FeatureExtraction.SimpleFeatureExtractor import SimpleFeatureExtractor  # noqa: E402
from app.ml.Pipelines.Categories.FeatureExtraction.RawSensorExtractor import RawSensorExtractor  # noqa: E402
from app.ml.Pipelines.Categories.Classifier.TorchDense import TorchDense  # noqa: E402
from app.ml.Pipelines.Categories.Classifier.TorchCNN1D import TorchCNN1D  # noqa: E402
from app.ml.PipelineExport.Executorch.ExecutorchCompiler import (  # noqa: E402
    buildExecutorchPte,
    storeExecutorchPte,
)
from app.ml.PipelineExport.Executorch.support import ExecutorchExportError  # noqa: E402
import app.routers.deploy as deploy  # noqa: E402
import app.Deploy.Base as deploy_base  # noqa: E402


def build_pipeline(featureExtractor, normalizer, classifier):
    """Build a real Pipeline (options + category steps) the way buildPipeline does."""
    windower = make_windower()
    options = [windower, featureExtractor, normalizer, classifier]
    steps = [
        getCategory("Windowing"),
        getCategory("Feature extraction"),
        getCategory("Normalizer"),
        getCategory("Classifier"),
    ]
    return Pipeline(options, steps)


def download_with(model, platform, pipeline):
    """downloadModel rebuilds the pipeline from the Mongo doc via getPipeline;
    patch it to return our already-fitted pipeline so we exercise the real
    export/dispatch/zip path without hand-building a full model document."""
    original = deploy_base.getPipeline
    deploy_base.getPipeline = lambda model: pipeline
    try:
        return downloadModel(model, platform)
    finally:
        deploy_base.getPipeline = original


def unzip(buffer):
    result = {}
    with zipfile.ZipFile(BytesIO(buffer.read())) as archive:
        for name in archive.namelist():
            result[name] = archive.read(name)
    return result


class TestFullDownloadFlow:
    """train -> precompile+cache -> downloadModel -> unzip -> run .pte, end to end."""

    def _run(self, feature_cls, normalizer_cls, classifier_cls):
        X, y = make_windows()
        fe, norm, clf = train_pipeline(feature_cls, normalizer_cls, classifier_cls, X, y)
        pipeline = build_pipeline(fe, norm, clf)
        model = make_model_doc(num_classes=clf.arch["num_classes"])
        model.id = f"cafe{feature_cls.__name__[:8]:0<20}"[:24]

        # trainer would precompile here
        storeExecutorchPte(model, buildExecutorchPte(pipeline.options, model))

        buffer = download_with(model, Platforms.EXECUTORCH, pipeline)
        files = unzip(buffer)
        assert set(files) == {"model.pte", "manifest.json", "README.md", "ExampleClassifier.kt"}

        manifest = json.loads(files["manifest.json"])
        assert manifest["input"]["shape"] == [1, WINDOW_SIZE, N_SENSORS]

        # parity: the downloaded .pte matches the python pipeline on fresh windows
        X_test, _ = make_windows(n=5, seed=99)
        preds = run_python_pipeline(fe, norm, clf, X_test)
        for i in range(X_test.shape[0]):
            single = torch.as_tensor(X_test[i : i + 1, :, 1:]).contiguous()
            logits = execute_pte(files["model.pte"], single)
            assert int(torch.argmax(logits, dim=-1).item()) == int(preds[i])

    def test_cnn_raw_znorm(self):
        self._run(RawSensorExtractor, ZNormalizer, TorchCNN1D)

    def test_dense_features_minmax(self):
        self._run(SimpleFeatureExtractor, MinMaxNormalizer, TorchDense)


class TestModelDocRoundTrip:
    """The classifier state must survive a Mongo-shaped persist/restore, and
    the restored module must still export."""

    def test_persist_restore_via_pipelinestepoption_then_export(self):
        X, y = make_windows()
        fe, norm, clf = train_pipeline(RawSensorExtractor, MinMaxNormalizer, TorchCNN1D, X, y)

        # simulate what trainer + getPipeline do: persist each option to a dict,
        # rebuild the pydantic PipelineStepOption, restore fresh instances.
        restored = []
        for option, cls in [
            (make_windower(), None),
            (fe, RawSensorExtractor),
            (norm, MinMaxNormalizer),
            (clf, TorchCNN1D),
        ]:
            persisted = option.persist()
            step = PipelineStepOption(**persisted)
            fresh = type(option)()
            fresh.restore(step)
            restored.append(fresh)

        pipeline = Pipeline(restored, [
            getCategory("Windowing"), getCategory("Feature extraction"),
            getCategory("Normalizer"), getCategory("Classifier"),
        ])
        model = make_model_doc(num_classes=clf.arch["num_classes"])
        model.id = "d0c0" + "0" * 20

        buffer = download_with(model, Platforms.EXECUTORCH, pipeline)
        files = unzip(buffer)
        assert len(files["model.pte"]) > 0


class TestZNormalizerRestore:
    """Regression: ZNormalizer.restore was missing, so restored models lost
    their normalization statistics."""

    def test_restore_recovers_statistics(self):
        rng = np.random.default_rng(3)
        data = rng.normal(5, 2, (40, N_SENSORS)).astype(np.float32)

        norm = ZNormalizer(ZNormalizer.get_parameters())
        norm.fit_normalize(data)
        expected = norm.normalize(data)

        step = PipelineStepOption(**norm.persist())
        restored = ZNormalizer()
        restored.restore(step)

        np.testing.assert_allclose(restored.normalize(data), expected, rtol=1e-6, atol=1e-6)
        np.testing.assert_array_equal(restored.mean, norm.mean)
        np.testing.assert_array_equal(restored.std, norm.std)


class FakeModelDB:
    def __init__(self, model):
        self._model = model

    def get_model(self, model_id, project):
        return self._model


class TestDeployRouteStatusMapping:
    """The deploy route must map export failures to meaningful HTTP statuses
    (finding #4) and run the CPU-bound work off the event loop (finding #7)."""

    def _call(self, download_impl, fmt=Platforms.EXECUTORCH):
        model = SimpleNamespace(name="m", id="0" * 24)
        original_db = deploy.ModelDB
        original_dl = deploy.downloadModel
        deploy.ModelDB = lambda: FakeModelDB(model)
        deploy.downloadModel = download_impl
        try:
            return asyncio.run(deploy.dlmodel(model_id="x", format=fmt, project="p"))
        finally:
            deploy.ModelDB = original_db
            deploy.downloadModel = original_dl

    def test_success_streams_zip(self):
        def ok(model, fmt):
            return BytesIO(b"zip-bytes")

        resp = self._call(ok)
        assert resp.media_type == "application/zip"
        assert "m_EXECUTORCH.zip" in resp.headers["content-disposition"]

    def test_executorch_error_400(self):
        from fastapi import HTTPException

        def boom(model, fmt):
            raise ExecutorchExportError("bad pipeline", status_code=400)

        try:
            self._call(boom)
            assert False, "expected HTTPException"
        except HTTPException as e:
            assert e.status_code == 400
            assert "bad pipeline" in e.detail

    def test_executorch_missing_501(self):
        from fastapi import HTTPException

        def boom(model, fmt):
            raise ExecutorchExportError("executorch not installed", status_code=501)

        try:
            self._call(boom)
            assert False, "expected HTTPException"
        except HTTPException as e:
            assert e.status_code == 501

    def test_notimplemented_maps_to_400(self):
        from fastapi import HTTPException

        def boom(model, fmt):
            raise NotImplementedError()

        try:
            self._call(boom, fmt=Platforms.C)
            assert False, "expected HTTPException"
        except HTTPException as e:
            assert e.status_code == 400
            assert "C" in e.detail

    def test_runs_off_event_loop(self):
        """downloadModel must be dispatched via run_in_threadpool: it should run
        on a worker thread, not the main asyncio thread."""
        import threading

        main_thread = threading.get_ident()
        seen = {}

        def record(model, fmt):
            seen["thread"] = threading.get_ident()
            return BytesIO(b"z")

        self._call(record)
        assert seen["thread"] != main_thread


class TestExportDispatch:
    """The export-dispatch change (Pipeline.export) must route each platform to
    the right builder and leave the C path untouched."""

    def _pipeline(self):
        X, y = make_windows()
        fe, norm, clf = train_pipeline(SimpleFeatureExtractor, MinMaxNormalizer, TorchDense, X, y)
        return build_pipeline(fe, norm, clf), make_model_doc(num_classes=clf.arch["num_classes"])

    def test_executorch_routes_to_executorch_builder(self, monkeypatch):
        import app.ml.PipelineExport.Executorch.ExecutorchCompiler as ec

        pipeline, model = self._pipeline()
        called = {}
        monkeypatch.setattr(ec, "buildExecutorchExport", lambda options, m: called.setdefault("et", True) or [])
        # C builder must NOT be called for the ExecuTorch platform
        import app.ml.Pipeline as pl
        monkeypatch.setattr(pl, "buildCCode", lambda steps, m: called.setdefault("c", True) or [])

        pipeline.export(model, Platforms.EXECUTORCH)
        assert called.get("et") is True
        assert "c" not in called

    def test_c_routes_to_ccode_builder(self, monkeypatch):
        import app.ml.Pipeline as pl
        from app.ml.Pipelines.Categories.Classifier.decision_tree import DecisionTree
        from app.ml.Pipelines.PipelineContainer import PipelineContainer

        # a pipeline whose steps all implement exportC (unlike torch classifiers)
        X, y = make_windows()
        fe = SimpleFeatureExtractor(SimpleFeatureExtractor.get_parameters())
        norm = MinMaxNormalizer(MinMaxNormalizer.get_parameters())
        tree = DecisionTree(DecisionTree.get_parameters())
        container = PipelineContainer(X, y, [None] * len(y))
        container = fe.fit_exec(container)
        container = norm.fit_exec(container)
        tree.fit_exec(container)
        pipeline = build_pipeline(fe, norm, tree)
        model = make_model_doc()

        called = {}
        monkeypatch.setattr(pl, "buildCCode", lambda steps, m: called.setdefault("c", True) or [])

        pipeline.export(model, Platforms.C)
        assert called.get("c") is True
