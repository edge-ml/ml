from importlib.metadata import PackageNotFoundError, version as pkg_version
from io import BytesIO

import torch
from torch import nn

from app.dataLoader import DATASTORE
from app.ml.PipelineExport.C.Common.CPart import ExtraFile
from app.ml.PipelineExport.Executorch.support import (
    ExecutorchExportError,
    findOption,
    getExportBlockers,
)
from app.ml.PipelineExport.Executorch.torch_ops import (
    TorchMinMaxNormalize,
    TorchSimpleFeatures,
    TorchZNormalize,
)
from app.ml.PipelineExport.Executorch.manifest import buildManifest
from app.ml.PipelineExport.Executorch.templates import buildKotlinExample, buildReadme
from app.ml.Pipelines.Categories.Windowing.BaseWindower import BaseWindower
from app.ml.Pipelines.Categories.FeatureExtraction.BaseFeatureExtractor import BaseFeatureExtractor
from app.ml.Pipelines.Categories.FeatureExtraction.SimpleFeatureExtractor import SimpleFeatureExtractor
from app.ml.Pipelines.Categories.Normalizer.BaseNormalizer import BaseNormalizer
from app.ml.Pipelines.Categories.Normalizer.MinMaxNormalizer import MinMaxNormalizer
from app.ml.Pipelines.Categories.Classifier.BaseClassififer import BaseClassififer


class ExecutorchExportModule(nn.Module):
    """Composes preprocessing and the trained classifier into one graph.

    Input: (1, window_size, n_sensors) float32 raw sensor samples — exactly
    what a device can buffer. Output: (1, num_classes) logits.
    """

    def __init__(self, features: nn.Module, normalize: nn.Module, classifier: nn.Module):
        super().__init__()
        self.features = features
        self.normalize = normalize
        self.classifier = classifier

    def forward(self, x):
        x = self.features(x)
        x = self.normalize(x)
        return self.classifier(x)


def buildExportModule(options) -> nn.Module:
    """Builds the composed eager module from restored pipeline options.

    The normalizer statistics were fit on sensor-only tensors when the
    SimpleFeatureExtractor or RawSensorExtractor produced them, so they can be
    baked as-is."""
    featureExtractor = findOption(options, BaseFeatureExtractor)
    normalizer = findOption(options, BaseNormalizer)
    classifier = findOption(options, BaseClassififer)

    if isinstance(featureExtractor, SimpleFeatureExtractor):
        features = TorchSimpleFeatures()
    else:  # RawSensorExtractor — the raw window is the feature
        features = nn.Identity()

    if isinstance(normalizer, MinMaxNormalizer):
        normalize = TorchMinMaxNormalize(normalizer.min, normalizer.max)
    else:  # ZNormalizer
        normalize = TorchZNormalize(normalizer.mean, normalizer.std)

    return ExecutorchExportModule(features, normalize, classifier.export_torch_module()).eval()


def compileToPte(module: nn.Module, example_input: torch.Tensor) -> bytes:
    try:
        from executorch.backends.xnnpack.partition.xnnpack_partitioner import XnnpackPartitioner
        from executorch.exir import to_edge_transform_and_lower
    except ImportError as e:
        raise ExecutorchExportError(
            "ExecuTorch export is not available on this server (executorch is not installed).",
            status_code=501,
        ) from e

    exported_program = torch.export.export(module, (example_input,))
    lowered = to_edge_transform_and_lower(exported_program, partitioner=[XnnpackPartitioner()])
    return lowered.to_executorch().buffer


def getExecutorchVersion() -> str:
    try:
        return pkg_version("executorch")
    except PackageNotFoundError:
        return "unknown"


def buildExecutorchPte(options, model) -> bytes:
    """The expensive part: trace + XNNPACK-lower the composed module to a .pte.

    Run once at train time (see trainer.init_train) and cached, rather than on
    every download request."""
    blockers = getExportBlockers(options)
    if blockers:
        raise ExecutorchExportError(" ".join(blockers), status_code=400)

    windower = findOption(options, BaseWindower)
    window_size = int(windower.get_param_value_by_name("window_size"))
    n_sensors = len(model.timeSeries)

    module = buildExportModule(options)
    example_input = torch.zeros(1, window_size, n_sensors, dtype=torch.float32)
    return compileToPte(module, example_input)


def assembleExecutorchFiles(options, model, pte_bytes: bytes):
    """Cheap part: bundle the (possibly cached) .pte with a freshly generated
    manifest, README and example — safe to run per request."""
    windower = findOption(options, BaseWindower)
    featureExtractor = findOption(options, BaseFeatureExtractor)
    normalizer = findOption(options, BaseNormalizer)
    classifier = findOption(options, BaseClassififer)

    window_size = int(windower.get_param_value_by_name("window_size"))
    sliding_step = int(windower.get_param_value_by_name("sliding_step"))
    executorch_version = getExecutorchVersion()
    bakes_features = isinstance(featureExtractor, SimpleFeatureExtractor)

    return [
        ExtraFile("model.pte", pte_bytes),
        ExtraFile("manifest.json", buildManifest(model, windower, featureExtractor, normalizer, classifier, executorch_version)),
        ExtraFile("README.md", buildReadme(model, executorch_version, bakes_features)),
        ExtraFile("ExampleClassifier.kt", buildKotlinExample(model, window_size, sliding_step, classifier.arch["num_classes"])),
    ]


def _pte_store_key(model) -> str:
    return f"executorch_{model.id}"


def storeExecutorchPte(model, pte_bytes: bytes):
    DATASTORE.saveObj(_pte_store_key(model), BytesIO(pte_bytes))


def loadExecutorchPte(model):
    """Returns the cached .pte bytes, or None if it was never precompiled
    (e.g. a model trained before precompilation existed)."""
    try:
        return DATASTORE.loadObj(_pte_store_key(model)).read()
    except Exception:
        return None


def buildExecutorchExport(options, model):
    blockers = getExportBlockers(options)
    if blockers:
        raise ExecutorchExportError(" ".join(blockers), status_code=400)

    pte_bytes = loadExecutorchPte(model)
    if pte_bytes is None:
        # Fallback for models predating train-time precompilation.
        pte_bytes = buildExecutorchPte(options, model)

    return assembleExecutorchFiles(options, model, pte_bytes)
