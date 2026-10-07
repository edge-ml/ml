"""Which pipelines can be exported to ONNX (browser / onnxruntime-web).

ONNX reuses the torch preprocessing modules of the ExecuTorch export
(features + normalization baked into the graph), so the same windowing,
feature extraction and normalizer restrictions apply. Unlike ExecuTorch it
also covers the sklearn tree classifiers via skl2onnx."""

from typing import List

from app.ml.PipelineExport.Executorch.support import findOption
from app.ml.Pipelines.Categories.Windowing.BaseWindower import BaseWindower
from app.ml.Pipelines.Categories.Windowing.SampleWindower import SampleWindower
from app.ml.Pipelines.Categories.FeatureExtraction.BaseFeatureExtractor import BaseFeatureExtractor
from app.ml.Pipelines.Categories.FeatureExtraction.SimpleFeatureExtractor import SimpleFeatureExtractor
from app.ml.Pipelines.Categories.FeatureExtraction.RawSensorExtractor import RawSensorExtractor
from app.ml.Pipelines.Categories.Normalizer.BaseNormalizer import BaseNormalizer
from app.ml.Pipelines.Categories.Normalizer.MinMaxNormalizer import MinMaxNormalizer
from app.ml.Pipelines.Categories.Normalizer.ZNormalizer import ZNormalizer
from app.ml.Pipelines.Categories.Classifier.BaseClassififer import BaseClassififer
from app.ml.Pipelines.Categories.Classifier.TorchNeuralNetwork import TorchNeuralNetwork
from app.ml.Pipelines.Categories.Classifier.decision_tree import DecisionTree
from app.ml.Pipelines.Categories.Classifier.random_forest import RandomForest


class OnnxExportError(Exception):
    """status_code: 400 = pipeline not exportable, 501 = onnx tooling missing."""

    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.status_code = status_code


SKLEARN_CLASSIFIERS = (DecisionTree, RandomForest)


def getOnnxBlockers(options) -> List[str]:
    blockers = []

    windower = findOption(options, BaseWindower)
    if not isinstance(windower, SampleWindower):
        blockers.append("ONNX export requires sample-based windowing.")

    featureExtractor = findOption(options, BaseFeatureExtractor)
    if not isinstance(featureExtractor, (SimpleFeatureExtractor, RawSensorExtractor)):
        blockers.append(
            "ONNX export requires the 'SimpleFeatureExtractor' or 'Raw Time-Series (Sensors only)' feature extraction."
        )

    normalizer = findOption(options, BaseNormalizer)
    if not isinstance(normalizer, (MinMaxNormalizer, ZNormalizer)):
        blockers.append("ONNX export requires the MinMaxNormalizer or ZNormalizer.")

    classifier = findOption(options, BaseClassififer)
    if not isinstance(classifier, (TorchNeuralNetwork,) + SKLEARN_CLASSIFIERS):
        blockers.append(
            "ONNX export is available for PyTorch classifiers, the Decision Tree and the Random Forest."
        )

    return blockers


def supportsOnnx(options) -> bool:
    return len(getOnnxBlockers(options)) == 0
