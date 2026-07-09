"""Tests for the PyTorch classifiers and the ExecuTorch (.pte) export.

Covers:
- persist/restore round-trip of torch classifiers through the DATASTORE
- numerical parity: python pipeline vs eager export module vs .pte executed
  with the ExecuTorch runtime
- manifest contents
- export gating (unsupported pipelines are rejected, formats computation)

Run from the ml/ directory: pytest tests/test_torch_executorch.py -v
"""

import json
import os
import tempfile
import unittest
import zipfile
from io import BytesIO
from types import SimpleNamespace

# Environment must be configured before any app import (app.internal.config
# reads it at import time).
_TSDATA_DIR = tempfile.mkdtemp(prefix="edgeml_test_ts_")
_TEST_ENV = {
    "SECRET_KEY": "test",
    "API_URI": "http://localhost",
    "DATABASE_URI": "mongodb://localhost:27017",
    "AUTH_DATABASE_URI": "mongodb://localhost:27017",
    "CLASSIFIER_STORE": "CLASSIFIER_STORE",
    "TS_STORE_MECHANISM": "FS",
    "TSDATA": _TSDATA_DIR,
    "S3_URL": "http://localhost:9444",
    "S3_BUCKET_NAME": "test",
    "S3_ACCESS_KEY": "test",
    "S3_SECRET_KEY": "test",
    "S3_MODEL_BUCKET_NAME": "test-models",
    "FIRMWARE_COMPILE_URL": "http://localhost:3005/",
}
for key, value in _TEST_ENV.items():
    os.environ.setdefault(key, value)

import numpy as np
import torch

from app.DataModels.PipelineRequest import PipelineStepOption
from app.ml.Pipelines.PipelineContainer import PipelineContainer
from app.ml.Pipelines.Categories.Windowing.SampleWindower import SampleWindower
from app.ml.Pipelines.Categories.FeatureExtraction.SimpleFeatureExtractor import SimpleFeatureExtractor
from app.ml.Pipelines.Categories.FeatureExtraction.RawSensorExtractor import RawSensorExtractor
from app.ml.Pipelines.Categories.FeatureExtraction.NoFeatureExtractor import NoFeatureExtractor
from app.ml.Pipelines.Categories.Normalizer.MinMaxNormalizer import MinMaxNormalizer
from app.ml.Pipelines.Categories.Normalizer.ZNormalizer import ZNormalizer
from app.ml.Pipelines.Categories.Classifier.decision_tree import DecisionTree
from app.ml.Pipelines.Categories.Classifier.TorchDense import TorchDense
from app.ml.Pipelines.Categories.Classifier.TorchCNN1D import TorchCNN1D
from app.ml.PipelineExport.Executorch.support import ExecutorchExportError, getExportBlockers
from app.ml.PipelineExport.Executorch.ExecutorchCompiler import (
    buildExecutorchExport,
    buildExportModule,
)
from app.ml.PipelineExport.formats import computeFormats

WINDOW_SIZE = 20
N_SENSORS = 3


def make_windows(n=80, window=WINDOW_SIZE, sensors=N_SENSORS, seed=0):
    """Synthetic labeled windows shaped like SampleWindower output:
    (n, window, 1 + sensors) with the timestamp in column 0."""
    rng = np.random.default_rng(seed)
    X, y = [], []
    for i in range(n):
        label = i % 2
        t = np.arange(window, dtype=np.float32)
        if label == 0:
            signal = np.stack([np.sin(t / 2 + s) for s in range(sensors)], axis=1)
            signal = signal + rng.normal(0, 0.1, (window, sensors))
        else:
            signal = rng.normal(0, 1, (window, sensors))
        timestamps = (t * 40.0 + i * 1000.0)[:, None]
        X.append(np.hstack([timestamps, signal]).astype(np.float32))
        y.append(label)
    return np.asarray(X, dtype=np.float32), np.asarray(y)


def fast_params(cls, overrides={"epochs": 5}):
    parameters = cls.get_parameters()
    for parameter in parameters:
        if parameter.parameter_name in overrides:
            parameter.value = overrides[parameter.parameter_name]
    return parameters


def make_windower():
    parameters = SampleWindower.get_parameters()
    for parameter in parameters:
        if parameter.parameter_name == "window_size":
            parameter.value = WINDOW_SIZE
        if parameter.parameter_name == "sliding_step":
            parameter.value = WINDOW_SIZE // 2
    return SampleWindower(parameters)


def make_model_doc(num_classes=2):
    return SimpleNamespace(
        name="test_model",
        id="0" * 24,
        timeSeries=["x", "y", "z"],
        samplingRate=25.0,
        labels=[SimpleNamespace(name=f"class_{i}") for i in range(num_classes)],
    )


def train_pipeline(feature_cls, normalizer_cls, classifier_cls, X, y):
    featureExtractor = feature_cls(feature_cls.get_parameters())
    normalizer = normalizer_cls(normalizer_cls.get_parameters())
    classifier = classifier_cls(fast_params(classifier_cls))

    container = PipelineContainer(X, y, [None] * len(y))
    container = featureExtractor.fit_exec(container)
    container = normalizer.fit_exec(container)
    classifier.fit_exec(container)
    return featureExtractor, normalizer, classifier


def run_python_pipeline(featureExtractor, normalizer, classifier, raw_windows):
    container = PipelineContainer(raw_windows, None, None)
    container = featureExtractor.exec(container)
    container = normalizer.exec(container)
    return classifier.predict(container.data)


def execute_pte(pte_bytes, input_tensor):
    from executorch.runtime import Runtime

    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "model.pte")
        with open(path, "wb") as f:
            f.write(pte_bytes)
        method = Runtime.get().load_program(path).load_method("forward")
        return method.execute([input_tensor])[0]


def get_file(files, name):
    return next(f for f in files if f.name == name)


class TestTorchPersistRestore(unittest.TestCase):

    def test_dense_persist_restore_roundtrip(self):
        X, y = make_windows()
        _, _, classifier = train_pipeline(SimpleFeatureExtractor, MinMaxNormalizer, TorchDense, X, y)

        features = SimpleFeatureExtractor(SimpleFeatureExtractor.get_parameters()).extract_features(X)
        persisted = classifier.persist()
        option = PipelineStepOption(**persisted)

        restored = TorchDense()
        restored.restore(option)

        np.testing.assert_array_equal(classifier.predict(features), restored.predict(features))
        self.assertEqual(list(restored.input_shape), list(classifier.input_shape))

    def test_cnn_persist_restore_roundtrip(self):
        X, y = make_windows()
        _, _, classifier = train_pipeline(RawSensorExtractor, ZNormalizer, TorchCNN1D, X, y)

        raw = RawSensorExtractor(RawSensorExtractor.get_parameters()).extract_features(X)
        persisted = classifier.persist()
        option = PipelineStepOption(**persisted)

        restored = TorchCNN1D()
        restored.restore(option)

        np.testing.assert_array_equal(classifier.predict(raw), restored.predict(raw))


class TestExecutorchExportParity(unittest.TestCase):
    """The key acceptance tests: the .pte executed by the ExecuTorch runtime
    must match the eager export module and the python pipeline."""

    def _export_and_check(self, feature_cls, normalizer_cls, classifier_cls):
        X, y = make_windows()
        featureExtractor, normalizer, classifier = train_pipeline(
            feature_cls, normalizer_cls, classifier_cls, X, y
        )
        options = [make_windower(), featureExtractor, normalizer, classifier]
        model_doc = make_model_doc(num_classes=classifier.arch["num_classes"])

        files = buildExecutorchExport(options, model_doc)
        self.assertEqual(
            [f.name for f in files],
            ["model.pte", "manifest.json", "README.md", "ExampleClassifier.kt"],
        )
        pte_bytes = get_file(files, "model.pte").content
        self.assertIsInstance(pte_bytes, bytes)
        self.assertGreater(len(pte_bytes), 0)

        # fresh, unseen windows
        X_test, _ = make_windows(n=6, seed=42)
        sensor_windows = torch.as_tensor(X_test[:, :, 1:])  # drop timestamp column

        eager_module = buildExportModule(options)
        python_predictions = run_python_pipeline(featureExtractor, normalizer, classifier, X_test)

        for i in range(X_test.shape[0]):
            # devices hand the runtime a contiguous buffer
            single = sensor_windows[i : i + 1].contiguous()
            eager_logits = eager_module(single)
            pte_logits = execute_pte(pte_bytes, single)
            np.testing.assert_allclose(
                pte_logits.numpy(), eager_logits.detach().numpy(), rtol=1e-4, atol=1e-4
            )
            self.assertEqual(
                int(torch.argmax(pte_logits, dim=-1).item()), int(python_predictions[i])
            )
        return files

    def test_cnn_raw_pipeline(self):
        self._export_and_check(RawSensorExtractor, ZNormalizer, TorchCNN1D)

    def test_cnn_raw_minmax_pipeline(self):
        self._export_and_check(RawSensorExtractor, MinMaxNormalizer, TorchCNN1D)

    def test_dense_features_pipeline(self):
        self._export_and_check(SimpleFeatureExtractor, MinMaxNormalizer, TorchDense)

    def test_manifest_contents(self):
        files = self._export_and_check(RawSensorExtractor, MinMaxNormalizer, TorchDense)
        manifest = json.loads(get_file(files, "manifest.json").content)

        self.assertEqual(manifest["schema_version"], 1)
        self.assertEqual(manifest["model_name"], "test_model")
        self.assertEqual(manifest["sampling_rate"], 25.0)
        self.assertEqual(manifest["window"], {"size": WINDOW_SIZE, "stride": WINDOW_SIZE // 2, "unit": "samples"})
        self.assertEqual(manifest["input"]["shape"], [1, WINDOW_SIZE, N_SENSORS])
        self.assertEqual(manifest["input"]["timeseries"], ["x", "y", "z"])
        self.assertEqual(manifest["input"]["dtype"], "float32")
        self.assertEqual(manifest["output"]["type"], "logits")
        self.assertEqual(manifest["output"]["labels"], ["class_0", "class_1"])
        self.assertEqual(manifest["executorch"]["backend"], "xnnpack")
        self.assertIn("classification_frequency_hint_hz", manifest)

        readme = get_file(files, "README.md").content
        self.assertIn("test_model", readme)
        kotlin = get_file(files, "ExampleClassifier.kt").content
        self.assertIn("WINDOW_SIZE = 20", kotlin)
        self.assertIn('"class_0", "class_1"', kotlin)


class TestExportGating(unittest.TestCase):

    def test_unsupported_feature_extractor_is_blocked(self):
        X, y = make_windows()
        featureExtractor, normalizer, classifier = train_pipeline(
            NoFeatureExtractor, MinMaxNormalizer, TorchDense, X, y
        )
        options = [make_windower(), featureExtractor, normalizer, classifier]

        self.assertTrue(len(getExportBlockers(options)) > 0)
        with self.assertRaises(ExecutorchExportError) as ctx:
            buildExecutorchExport(options, make_model_doc())
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertNotIn("EXECUTORCH", computeFormats(options))

    def test_non_torch_classifier_is_blocked(self):
        windower = make_windower()
        featureExtractor = SimpleFeatureExtractor(SimpleFeatureExtractor.get_parameters())
        normalizer = MinMaxNormalizer(MinMaxNormalizer.get_parameters())
        tree = DecisionTree(DecisionTree.get_parameters())
        options = [windower, featureExtractor, normalizer, tree]

        blockers = getExportBlockers(options)
        self.assertTrue(any("PyTorch" in blocker for blocker in blockers))

    def test_formats_computation(self):
        windower = make_windower()
        featureExtractor = SimpleFeatureExtractor(SimpleFeatureExtractor.get_parameters())
        normalizer = MinMaxNormalizer(MinMaxNormalizer.get_parameters())

        # DecisionTree + Simple + MinMax + SampleWindower is the classic C pipeline
        tree_formats = computeFormats([windower, featureExtractor, normalizer, DecisionTree(DecisionTree.get_parameters())])
        self.assertEqual(tree_formats, ["C"])

        # torch classifier: EXECUTORCH but no C
        torch_formats = computeFormats([windower, featureExtractor, normalizer, TorchDense(TorchDense.get_parameters())])
        self.assertEqual(torch_formats, ["EXECUTORCH"])


class TestZipCompatibility(unittest.TestCase):
    """downloadModel zips the export files directly — binary .pte content has to
    survive, and ExtraFile (what the exporters return) must be zippable without
    a re-wrap into StringFile."""

    def test_zip_with_binary_content(self):
        from app.utils.StringFile import StringFile
        from app.utils.zipfile import zipFiles

        files = [StringFile(b"\x00\x01binary", "model.pte"), StringFile('{"a": 1}', "manifest.json")]
        buffer = zipFiles(files)
        with zipfile.ZipFile(BytesIO(buffer.read())) as archive:
            self.assertEqual(archive.read("model.pte"), b"\x00\x01binary")
            self.assertEqual(archive.read("manifest.json"), b'{"a": 1}')

    def test_extrafile_is_directly_zippable(self):
        from app.ml.PipelineExport.C.Common.CPart import ExtraFile
        from app.utils.zipfile import zipFiles

        files = [ExtraFile("model.pte", b"\x00\x01binary"), ExtraFile("manifest.json", '{"a": 1}')]
        buffer = zipFiles(files)
        with zipfile.ZipFile(BytesIO(buffer.read())) as archive:
            self.assertEqual(archive.read("model.pte"), b"\x00\x01binary")
            self.assertEqual(archive.read("manifest.json"), b'{"a": 1}')


class TestPteCache(unittest.TestCase):
    """Train-time precompilation stores the .pte; downloads reuse it."""

    def test_load_missing_pte_returns_none(self):
        from app.ml.PipelineExport.Executorch.ExecutorchCompiler import loadExecutorchPte

        self.assertIsNone(loadExecutorchPte(make_model_doc()))

    def test_store_then_load_roundtrip(self):
        from app.ml.PipelineExport.Executorch.ExecutorchCompiler import (
            loadExecutorchPte,
            storeExecutorchPte,
        )

        model = make_model_doc()
        model.id = "1" * 24  # avoid clashing with other tests' default id
        storeExecutorchPte(model, b"\x00pte-bytes")
        self.assertEqual(loadExecutorchPte(model), b"\x00pte-bytes")

    def test_export_uses_cached_pte(self):
        """buildExecutorchExport must stream cached bytes rather than recompiling."""
        from app.ml.PipelineExport.Executorch.ExecutorchCompiler import (
            buildExecutorchExport,
            storeExecutorchPte,
        )

        X, y = make_windows()
        featureExtractor, normalizer, classifier = train_pipeline(
            RawSensorExtractor, MinMaxNormalizer, TorchCNN1D, X, y
        )
        options = [make_windower(), featureExtractor, normalizer, classifier]
        model = make_model_doc(num_classes=classifier.arch["num_classes"])
        model.id = "2" * 24

        storeExecutorchPte(model, b"SENTINEL_PTE")
        files = buildExecutorchExport(options, model)
        self.assertEqual(get_file(files, "model.pte").content, b"SENTINEL_PTE")


if __name__ == "__main__":
    unittest.main()
