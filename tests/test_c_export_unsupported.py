"""C export of a pipeline step without a C exporter must raise
NotImplementedError, which the download route maps to a clear 400. It used to
raise TypeError (exportC was missing self), so e.g. downloading a PyTorch
model as C returned a 500."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import test_torch_executorch as t  # noqa: E402  (configures the environment before app imports)

from app.ml.BaseConfig import Platforms  # noqa: E402
from app.ml.Pipelines.Abstract.AbstractPipelineOption import AbstractPipelineOption  # noqa: E402
from app.ml.Pipelines.Categories.Classifier.TorchCNN1D import TorchCNN1D  # noqa: E402
from app.ml.Pipelines.Categories.Classifier.decision_tree import DecisionTree  # noqa: E402
from app.ml.Pipelines.Categories.Classifier.random_forest import RandomForest  # noqa: E402
from app.ml.Pipelines.Categories.FeatureExtraction.SimpleFeatureExtractor import SimpleFeatureExtractor  # noqa: E402
from app.ml.Pipelines.Categories.Normalizer.MinMaxNormalizer import MinMaxNormalizer  # noqa: E402
from app.ml.Pipelines.Categories.FeatureExtraction.RawSensorExtractor import RawSensorExtractor  # noqa: E402
from app.ml.Pipelines.Categories.Normalizer.ZNormalizer import ZNormalizer  # noqa: E402


class TestUnsupportedCExport(unittest.TestCase):

    def test_options_without_c_export_raise_not_implemented(self):
        X, y = t.make_windows()
        for option in t.train_pipeline(RawSensorExtractor, ZNormalizer, TorchCNN1D, X, y):
            if type(option).exportC is AbstractPipelineOption.exportC:
                with self.subTest(option=option.get_name()), self.assertRaises(NotImplementedError):
                    option.export(t.make_model_doc(), Platforms.C)

    def test_random_forest_c_export_is_not_implemented(self):
        X, y = t.make_windows()
        *_, forest = t.train_pipeline(SimpleFeatureExtractor, MinMaxNormalizer, RandomForest, X, y)
        with self.assertRaises(NotImplementedError):
            forest.export(t.make_model_doc(), Platforms.C)

    def test_train_config_still_reports_c_support(self):
        self.assertTrue(DecisionTree.get_train_config()["exportTargets"]["c"])
        self.assertFalse(TorchCNN1D.get_train_config()["exportTargets"]["c"])
        self.assertFalse(RawSensorExtractor.get_train_config()["exportTargets"]["c"])
        self.assertFalse(RandomForest.get_train_config()["exportTargets"]["c"])


if __name__ == "__main__":
    unittest.main()
