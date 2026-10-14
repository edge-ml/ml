"""Named training presets for the device-API libraries (JS, Python, Dart).

A preset is a partial `pipeline` for a DeviceTrainRequest. Every preset uses
sample-based windowing, a Z normalizer and a PyTorch classifier, so the trained
model can be exported to ExecuTorch and run on a phone. Keeping them here (not
in each library) lets us tune them without releasing the libraries.

Request `pipeline` entries are applied on top of the preset: the same option
name merges parameters, a different option name replaces the step."""

from typing import Dict, List

from pydantic import BaseModel

from app.ml.Pipelines.Categories.Windowing.SampleWindower import SampleWindower
from app.ml.Pipelines.Categories.FeatureExtraction.SimpleFeatureExtractor import SimpleFeatureExtractor
from app.ml.Pipelines.Categories.FeatureExtraction.RawSensorExtractor import RawSensorExtractor
from app.ml.Pipelines.Categories.Normalizer.MinMaxNormalizer import MinMaxNormalizer
from app.ml.Pipelines.Categories.Normalizer.ZNormalizer import ZNormalizer
from app.ml.Pipelines.Categories.Classifier.TorchNeuralNetwork import TorchNeuralNetwork
from app.ml.Pipelines.Categories.Classifier.TorchCNN1D import TorchCNN1D
from app.ml.Pipelines.Categories.Classifier.TorchDense import TorchDense


class Preset(BaseModel):
    id: str
    name: str
    description: str
    pipeline: Dict[str, dict]


def _window():
    return {"name": SampleWindower.get_name(), "parameters": {"window_size": 50, "sliding_step": 25}}


def _cnn(conv_blocks: int, base_filters: int):
    return {
        "windowing": _window(),
        "featureExtraction": {"name": RawSensorExtractor.get_name()},
        "normalizer": {"name": ZNormalizer.get_name()},
        "classifier": {"name": TorchCNN1D.get_name(),
                       "parameters": {"conv_blocks": conv_blocks, "base_filters": base_filters}},
    }


def _dense(hidden_layers: int, hidden_units: int):
    return {
        "windowing": _window(),
        "featureExtraction": {"name": SimpleFeatureExtractor.get_name()},
        "normalizer": {"name": ZNormalizer.get_name()},
        "classifier": {"name": TorchDense.get_name(),
                       "parameters": {"hidden_layers": hidden_layers, "hidden_units": hidden_units}},
    }


PRESETS: Dict[str, Preset] = {p.id: p for p in [
    Preset(id="small_cnn", name="Small CNN",
           description="1 convolution block, 8 filters, on raw windows. Fastest and smallest.",
           pipeline=_cnn(1, 8)),
    Preset(id="medium_cnn", name="Medium CNN",
           description="2 convolution blocks, 16 filters, on raw windows. A good default.",
           pipeline=_cnn(2, 16)),
    Preset(id="large_cnn", name="Large CNN",
           description="3 convolution blocks, 32 filters, on raw windows. Most accurate, largest.",
           pipeline=_cnn(3, 32)),
    Preset(id="small_dense", name="Small Dense",
           description="1 hidden layer of 16 units on simple statistical features (mean, std, ...).",
           pipeline=_dense(1, 16)),
    Preset(id="large_dense", name="Large Dense",
           description="3 hidden layers of 64 units on simple statistical features.",
           pipeline=_dense(3, 64)),
]}


def listPresets() -> List[dict]:
    return [p.dict() for p in PRESETS.values()]


def applyPreset(preset_id: str, overrides: Dict[str, dict]) -> Dict[str, dict]:
    """Returns the preset's pipeline with the request's per-step overrides
    applied. Raises KeyError for an unknown preset."""
    pipeline = {key: {"name": spec.get("name"), "parameters": dict(spec.get("parameters", {}))}
                for key, spec in PRESETS[preset_id].pipeline.items()}
    for key, spec in overrides.items():
        base = pipeline.get(key)
        if base is not None and (not spec.get("name") or spec["name"] == base["name"]):
            base["parameters"].update(spec.get("parameters") or {})
        else:
            pipeline[key] = {"name": spec.get("name"), "parameters": dict(spec.get("parameters") or {})}
    return pipeline


def executorchBlockers(option_classes: Dict[str, type]) -> List[str]:
    """Static version of Executorch.support.getExportBlockers for a request
    that has not been trained yet: option classes by step key."""
    blockers = []
    if not issubclass(option_classes["windowing"], SampleWindower):
        blockers.append("sample-based windowing")
    if not issubclass(option_classes["featureExtraction"], (SimpleFeatureExtractor, RawSensorExtractor)):
        blockers.append("the SimpleFeatureExtractor or raw time-series features")
    if not issubclass(option_classes["normalizer"], (MinMaxNormalizer, ZNormalizer)):
        blockers.append("a MinMax or Z normalizer")
    if not issubclass(option_classes["classifier"], TorchNeuralNetwork):
        blockers.append("a PyTorch classifier")
    return blockers
