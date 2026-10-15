"""Models trained before formats were stored (formats=None) get their formats
derived from the pipeline's step types, so the download modal offers what
actually works (e.g. ONNX for an old random forest) instead of only C."""
import os
import sys
import unittest
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(__file__))
import test_torch_executorch  # noqa: E402,F401  (configures the environment before app imports)

from app.controller import ModelController as controller_module  # noqa: E402
from app.DataModels.model import ModelStatus  # noqa: E402
from app.ml.PipelineExport.formats import formatsForStoredModel  # noqa: E402
from app.ml.Pipelines import getPipelineOption  # noqa: E402


def stored_model(classifier, formats=None, status=ModelStatus.done,
                 features="SimpleFeatureExtractor", normalizer="MinMaxNormalizer"):
    names = ["Sample based", features, normalizer, classifier, "TestTrainSplit"]
    steps = []
    for name in names:
        try:
            params = getPipelineOption(name).get_parameters()
        except KeyError:
            params = []
        steps.append(SimpleNamespace(options=SimpleNamespace(name=name, parameters=params)))
    return SimpleNamespace(pipeline=SimpleNamespace(selectedPipeline=SimpleNamespace(steps=steps)),
                           formats=formats, trainStatus=status)


class TestFormatsForStoredModel(unittest.TestCase):

    def test_old_pipelines(self):
        self.assertEqual(formatsForStoredModel(stored_model("Decision Tree Classifier")), ["C", "ONNX"])
        self.assertEqual(formatsForStoredModel(stored_model("Random Forest Classifier")), ["ONNX"])
        self.assertEqual(formatsForStoredModel(stored_model("Small Dense Neural Network")), [])
        self.assertEqual(formatsForStoredModel(stored_model("A classifier that was removed")), [])


class TestControllerFillsMissingFormats(unittest.TestCase):

    def setUp(self):
        self.models = {
            "old_rf": stored_model("Random Forest Classifier"),
            "new_dt": stored_model("Decision Tree Classifier", formats=["C"]),  # stored at train time: kept
            "failed": stored_model("Random Forest Classifier", status=ModelStatus.error),
        }
        db = SimpleNamespace(get_model=lambda mid, pid: self.models[mid],
                             get_project_models=lambda pid: list(self.models.values()))
        self.controller = controller_module.ModelController.__new__(controller_module.ModelController)
        self.controller._model_db = db

    def test_fills_only_missing_formats_of_trained_models(self):
        self.assertEqual(self.controller.get_model_by_id("p", "old_rf").formats, ["ONNX"])
        self.assertEqual(self.controller.get_model_by_id("p", "new_dt").formats, ["C"])
        self.assertIsNone(self.controller.get_model_by_id("p", "failed").formats)
        self.assertEqual([m.formats for m in self.controller.get_models("p")], [["ONNX"], ["C"], None])


if __name__ == "__main__":
    unittest.main()
