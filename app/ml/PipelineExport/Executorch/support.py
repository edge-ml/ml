from typing import List

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


class ExecutorchExportError(Exception):
    """Raised when a model cannot be exported to ExecuTorch.

    status_code maps to the HTTP status the deploy router should return:
    400 = this pipeline is not exportable, 501 = executorch not installed.
    """

    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.status_code = status_code


def findOption(options, baseClass):
    for option in options:
        if isinstance(option, baseClass):
            return option
    return None


def getExportBlockers(options) -> List[str]:
    """Returns human-readable reasons why this pipeline cannot be exported to
    ExecuTorch. An empty list means the pipeline is exportable."""
    blockers = []

    windower = findOption(options, BaseWindower)
    if not isinstance(windower, SampleWindower):
        blockers.append("ExecuTorch export requires sample-based windowing.")

    featureExtractor = findOption(options, BaseFeatureExtractor)
    if not isinstance(featureExtractor, (SimpleFeatureExtractor, RawSensorExtractor)):
        blockers.append(
            "ExecuTorch export requires the 'SimpleFeatureExtractor' or 'Raw Time-Series (Sensors only)' feature extraction."
        )

    normalizer = findOption(options, BaseNormalizer)
    if not isinstance(normalizer, (MinMaxNormalizer, ZNormalizer)):
        blockers.append("ExecuTorch export requires the MinMaxNormalizer or ZNormalizer.")

    classifier = findOption(options, BaseClassififer)
    if not isinstance(classifier, TorchNeuralNetwork):
        blockers.append("ExecuTorch export is only available for PyTorch classifiers.")

    return blockers


def supportsExecutorch(options) -> bool:
    return len(getExportBlockers(options)) == 0
