"""Tests for the ONNX export (browser / edge-ml JS library).

The exported graph executed by onnxruntime must reproduce the python pipeline
(feature extraction + normalization + classifier) on raw sensor windows, for
both the torch classifiers and the sklearn trees.
"""
import json
import os
import sys
import unittest
import zipfile

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
# Importing the ExecuTorch tests configures the environment and gives us the
# shared synthetic-data / training helpers.
from test_torch_executorch import (  # noqa: E402
    get_file,
    make_model_doc,
    make_windower,
    make_windows,
    run_python_pipeline,
    train_pipeline,
    WINDOW_SIZE,
    N_SENSORS,
)

from app.ml.Pipelines.Categories.FeatureExtraction.SimpleFeatureExtractor import SimpleFeatureExtractor  # noqa: E402
from app.ml.Pipelines.Categories.FeatureExtraction.RawSensorExtractor import RawSensorExtractor  # noqa: E402
from app.ml.Pipelines.Categories.FeatureExtraction.NoFeatureExtractor import NoFeatureExtractor  # noqa: E402
from app.ml.Pipelines.Categories.Normalizer.MinMaxNormalizer import MinMaxNormalizer  # noqa: E402
from app.ml.Pipelines.Categories.Normalizer.ZNormalizer import ZNormalizer  # noqa: E402
from app.ml.Pipelines.Categories.Classifier.decision_tree import DecisionTree  # noqa: E402
from app.ml.Pipelines.Categories.Classifier.random_forest import RandomForest  # noqa: E402
from app.ml.Pipelines.Categories.Classifier.TorchDense import TorchDense  # noqa: E402
from app.ml.Pipelines.Categories.Classifier.TorchCNN1D import TorchCNN1D  # noqa: E402
from app.ml.PipelineExport.Onnx.support import getOnnxBlockers, OnnxExportError  # noqa: E402
from app.ml.PipelineExport.Onnx.OnnxCompiler import buildOnnxExport, buildOnnxModel  # noqa: E402
from app.ml.PipelineExport.formats import computeFormats  # noqa: E402
from app.utils.zipfile import zipFiles  # noqa: E402


def run_onnx(model_bytes, raw_windows):
    import onnxruntime as ort

    session = ort.InferenceSession(model_bytes, providers=["CPUExecutionProvider"])
    (scores,) = session.run(["scores"], {"raw_window": raw_windows})
    return scores


def sensor_windows(X):
    """SampleWindower output minus the timestamp column — what a device buffers."""
    return np.ascontiguousarray(X[:, :, 1:], dtype=np.float32)


class TestOnnxExportParity(unittest.TestCase):

    def _export_and_check(self, feature_cls, normalizer_cls, classifier_cls):
        X, y = make_windows()
        featureExtractor, normalizer, classifier = train_pipeline(
            feature_cls, normalizer_cls, classifier_cls, X, y
        )
        options = [make_windower(), featureExtractor, normalizer, classifier]
        self.assertEqual(getOnnxBlockers(options), [])
        self.assertIn("ONNX", computeFormats(options))

        model_doc = make_model_doc(num_classes=2)
        files = buildOnnxExport(options, model_doc)
        self.assertEqual(
            [f.name for f in files], ["model.onnx", "manifest.json", "README.md", "index.html"]
        )

        X_test, _ = make_windows(n=6, seed=42)
        raw = sensor_windows(X_test)
        scores = run_onnx(get_file(files, "model.onnx").content, raw)
        self.assertEqual(scores.shape, (6, 2))

        expected = run_python_pipeline(featureExtractor, normalizer, classifier, X_test)
        np.testing.assert_array_equal(np.argmax(scores, axis=-1), np.asarray(expected))

        manifest = json.loads(get_file(files, "manifest.json").content)
        self.assertEqual(manifest["format"], "onnx")
        self.assertEqual(manifest["input"]["name"], "raw_window")
        self.assertEqual(manifest["input"]["shape"], [1, WINDOW_SIZE, N_SENSORS])
        self.assertEqual(manifest["input"]["timeseries"], ["x", "y", "z"])
        self.assertEqual(manifest["window"], {"size": WINDOW_SIZE, "stride": WINDOW_SIZE // 2, "unit": "samples"})
        self.assertEqual(manifest["output"]["labels"], ["class_0", "class_1"])

        # the whole bundle zips (the /deploy download path)
        with zipfile.ZipFile(zipFiles(files)) as z:
            self.assertIn("model.onnx", z.namelist())
        return manifest, scores

    def test_random_forest_simple_features(self):
        manifest, scores = self._export_and_check(SimpleFeatureExtractor, MinMaxNormalizer, RandomForest)
        self.assertEqual(manifest["output"]["type"], "probabilities")
        np.testing.assert_allclose(scores.sum(axis=-1), 1.0, rtol=1e-5)

    def test_decision_tree_raw_features(self):
        manifest, _ = self._export_and_check(RawSensorExtractor, ZNormalizer, DecisionTree)
        self.assertEqual(manifest["preprocessing"]["baked"], ["ZNormalizer"])

    def test_torch_dense_simple_features(self):
        manifest, _ = self._export_and_check(SimpleFeatureExtractor, ZNormalizer, TorchDense)
        self.assertEqual(manifest["output"]["type"], "logits")

    def test_torch_cnn_raw_features(self):
        self._export_and_check(RawSensorExtractor, MinMaxNormalizer, TorchCNN1D)

    def test_dynamic_batch(self):
        X, y = make_windows()
        options = [make_windower(), *train_pipeline(SimpleFeatureExtractor, MinMaxNormalizer, RandomForest, X, y)]
        scores = run_onnx(buildOnnxModel(options, make_model_doc()), sensor_windows(X[:1]))
        self.assertEqual(scores.shape[0], 1)

    def test_sklearn_labels_follow_seen_classes(self):
        # Label 1 never appears in training: the output has one column, which
        # must be mapped to class_0 and not shifted onto another label.
        X, _ = make_windows()
        y = np.zeros(len(X), dtype=int)
        options = [make_windower(), *train_pipeline(SimpleFeatureExtractor, MinMaxNormalizer, DecisionTree, X, y)]
        manifest = json.loads(get_file(buildOnnxExport(options, make_model_doc(num_classes=2)), "manifest.json").content)
        self.assertEqual(manifest["output"]["labels"], ["class_0"])


class TestOnnxBlockers(unittest.TestCase):

    def test_unsupported_feature_extractor_is_rejected(self):
        X, y = make_windows()
        featureExtractor, normalizer, classifier = train_pipeline(
            NoFeatureExtractor, MinMaxNormalizer, DecisionTree, X, y
        )
        options = [make_windower(), featureExtractor, normalizer, classifier]
        self.assertTrue(getOnnxBlockers(options))
        self.assertNotIn("ONNX", computeFormats(options))
        with self.assertRaises(OnnxExportError) as ctx:
            buildOnnxModel(options, make_model_doc())
        self.assertEqual(ctx.exception.status_code, 400)


if __name__ == "__main__":
    unittest.main()
