"""Exports of the audio pipeline (#100).

The model is composed exactly like the sensor exports (features, then
normalization, then the classifier, all in one graph), but it takes the
window's inputs separately: `audio` (1, samples) and/or `raw_window`
(1, samples, channels), in the order SyncedTimeWindower.export_inputs gives.
The spectrogram is part of the graph (TorchLogMel), so an app only buffers
raw audio and sensor values.

The existing compilers call into this module when the pipeline uses the
time-based windower; nothing changes for sensor-only pipelines.
"""
import json
from io import BytesIO
from typing import List

import torch
from torch import nn

from app.ml.PipelineExport.C.Common.CPart import ExtraFile
from app.ml.PipelineExport.manifest_v2 import build_manifest_v2

OPSET = 17
OUTPUT_NAME = "scores"


def _options(options):
    from app.ml.PipelineExport.Executorch.support import findOption
    from app.ml.Pipelines.Categories.Classifier.BaseClassififer import BaseClassififer
    from app.ml.Pipelines.Categories.FeatureExtraction.BaseFeatureExtractor import BaseFeatureExtractor
    from app.ml.Pipelines.Categories.Normalizer.BaseNormalizer import BaseNormalizer
    from app.ml.Pipelines.Categories.Windowing.BaseWindower import BaseWindower

    return (findOption(options, BaseWindower), findOption(options, BaseFeatureExtractor),
            findOption(options, BaseNormalizer), findOption(options, BaseClassififer))


def is_audio_pipeline(options) -> bool:
    from app.ml.Pipelines.Categories.Windowing.SyncedTimeWindower import SyncedTimeWindower

    return any(isinstance(o, SyncedTimeWindower) for o in options)


def audio_blockers(options, target="ExecuTorch") -> List[str]:
    from app.ml.Pipelines.Categories.Classifier.TorchNeuralNetwork import TorchNeuralNetwork
    from app.ml.Pipelines.Categories.FeatureExtraction.LogMelSensorExtractor import LogMelSensorExtractor
    from app.ml.Pipelines.Categories.Normalizer.ZNormalizer import ZNormalizer

    _, extractor, normalizer, classifier = _options(options)
    blockers = []
    if not isinstance(extractor, LogMelSensorExtractor):
        blockers.append(f"{target} export of time-based windows requires the 'Log-mel spectrogram & sensors' feature extraction.")
    if not isinstance(normalizer, ZNormalizer):
        blockers.append(f"{target} export of time-based windows requires the Per-channel ZNormalizer.")
    if not isinstance(classifier, TorchNeuralNetwork):
        blockers.append(f"{target} export is only available for PyTorch classifiers.")
    return blockers


class _Composed(nn.Module):
    def __init__(self, features, normalize, classifier):
        super().__init__()
        self.features = features
        self.normalize = normalize
        self.classifier = classifier

    def run(self, *inputs):
        return self.classifier(self.normalize(self.features(*inputs)))


class _AudioModel(_Composed):
    def forward(self, audio):
        return self.run(audio)


class _SensorModel(_Composed):
    def forward(self, raw_window):
        return self.run(raw_window)


class _MixedModel(_Composed):
    def forward(self, raw_window, audio):
        return self.run(raw_window, audio)


def build_module(options) -> nn.Module:
    from app.ml.PipelineExport.Executorch.torch_ops import TorchZNormalize

    windower, extractor, normalizer, classifier = _options(options)
    names = [spec["name"] for spec in windower.export_inputs()]
    cls = {("audio",): _AudioModel, ("raw_window",): _SensorModel, ("raw_window", "audio"): _MixedModel}[tuple(names)]
    return cls(extractor.torch_feature_module(), TorchZNormalize(normalizer.mean, normalizer.std),
               classifier.export_torch_module()).eval()


def example_inputs(options):
    windower = _options(options)[0]
    return tuple(torch.zeros(*spec["shape"], dtype=torch.float32) for spec in windower.export_inputs())


def input_names(options):
    return [spec["name"] for spec in _options(options)[0].export_inputs()]


def _check(options, target):
    blockers = audio_blockers(options, target)
    if blockers:
        from app.ml.PipelineExport.Executorch.support import ExecutorchExportError
        from app.ml.PipelineExport.Onnx.support import OnnxExportError

        raise (OnnxExportError if target == "ONNX" else ExecutorchExportError)(" ".join(blockers), status_code=400)


# -- ExecuTorch -------------------------------------------------------------
def build_pte(options) -> bytes:
    from app.ml.PipelineExport.Executorch.support import ExecutorchExportError

    _check(options, "ExecuTorch")
    try:
        from executorch.backends.xnnpack.partition.xnnpack_partitioner import XnnpackPartitioner
        from executorch.exir import to_edge_transform_and_lower
    except ImportError as e:
        raise ExecutorchExportError("ExecuTorch export is not available on this server (executorch is not installed).",
                                    status_code=501) from e
    program = torch.export.export(build_module(options), example_inputs(options))
    return to_edge_transform_and_lower(program, partitioner=[XnnpackPartitioner()]).to_executorch().buffer


def executorch_manifest(options, model) -> dict:
    from app.ml.PipelineExport.Executorch.ExecutorchCompiler import getExecutorchVersion

    return build_manifest_v2(options, model, "executorch",
                             {"executorch": {"version": getExecutorchVersion(), "backend": "xnnpack"}})


def executorch_files(options, model, pte_bytes):
    manifest = executorch_manifest(options, model)
    return [
        ExtraFile("model.pte", pte_bytes),
        ExtraFile("manifest.json", json.dumps(manifest, indent=2)),
        ExtraFile("README.md", _readme(model, manifest, "executorch")),
    ]


# -- ONNX -------------------------------------------------------------------
def build_onnx(options) -> bytes:
    _check(options, "ONNX")
    names = input_names(options)
    buffer = BytesIO()
    with torch.no_grad():
        torch.onnx.export(
            build_module(options), example_inputs(options), buffer,
            input_names=names, output_names=[OUTPUT_NAME],
            dynamic_axes={**{n: {0: "batch"} for n in names}, OUTPUT_NAME: {0: "batch"}},
            opset_version=OPSET, dynamo=False,
        )
    return buffer.getvalue()


def onnx_manifest(options, model) -> dict:
    return build_manifest_v2(options, model, "onnx", {"opset": OPSET})


def onnx_files(options, model):
    manifest = onnx_manifest(options, model)
    return [
        ExtraFile("model.onnx", build_onnx(options)),
        ExtraFile("manifest.json", json.dumps(manifest, indent=2)),
        ExtraFile("README.md", _readme(model, manifest, "onnx")),
    ]


# -- PyTorch (TorchScript) --------------------------------------------------
def build_torchscript(options) -> bytes:
    _check(options, "PyTorch")
    module = build_module(options)
    with torch.no_grad():
        traced = torch.jit.trace(module, example_inputs(options))
    buffer = BytesIO()
    torch.jit.save(traced, buffer)
    return buffer.getvalue()


def pytorch_files(options, model):
    manifest = build_manifest_v2(options, model, "pytorch")
    return [
        ExtraFile("model.pt", build_torchscript(options)),
        ExtraFile("manifest.json", json.dumps(manifest, indent=2)),
        ExtraFile("README.md", _readme(model, manifest, "pytorch")),
        ExtraFile("inference.py", _inference_py(manifest)),
    ]


# -- docs -------------------------------------------------------------------
def _describe_inputs(manifest):
    lines = []
    for spec in manifest["inputs"]:
        if spec["kind"] == "audio":
            lines.append(f"- `{spec['name']}` float32 `{spec['shape']}`: mono sound at {spec['sample_rate']} Hz, "
                         f"samples in [-1, 1] (16-bit PCM divided by 32768). Trained on the recording \"{spec['recording']}\".")
        else:
            lines.append(f"- `{spec['name']}` float32 `{spec['shape']}`: sensor values at {spec['sampling_rate']} Hz, "
                         f"channels in this order: {', '.join(spec['timeseries'])}.")
    return "\n".join(lines)


_HOW = {
    "executorch": ("model.pte", "Runs on smartphones with ExecuTorch (XNNPACK). The edge-ml Flutter library "
                   "(`edge_ml_dart`) loads it and feeds the microphone and sensors for you."),
    "onnx": ("model.onnx", "Runs in the browser (onnxruntime-web) or in Node.js (onnxruntime-node). The edge-ml "
             "JavaScript library (`edge-ml`) loads it; `addAudio` takes microphone samples at any rate."),
    "pytorch": ("model.pt", "A TorchScript module for servers and scripts: `torch.jit.load(\"model.pt\")`. "
                "See `inference.py`."),
}


def _readme(model, manifest, fmt):
    file, how = _HOW[fmt]
    window = manifest["window"]
    return f"""# {model.name}

{how}

## Inputs
One window is {window['duration_ms']:g} ms; a new one can start every {window['stride_ms']:g} ms.
The model takes, in this order:

{_describe_inputs(manifest)}

The spectrogram and the normalization are part of `{file}`: feed the raw sound and sensor values.
Resample the sound to the rate above and mix stereo down to mono before feeding it.

## Output
`scores` `{manifest['output']['shape']}`: one logit per label, in this order: {', '.join(manifest['output']['labels'])}.

## Files
- `{file}`: the model.
- `manifest.json`: inputs, window, rates and labels (schema 2).
"""


def _inference_py(manifest):
    shapes = ", ".join(f"np.zeros({tuple(s['shape'])}, dtype=np.float32)" for s in manifest["inputs"])
    names = ", ".join(s["name"] for s in manifest["inputs"])
    return f'''"""Minimal inference example for the exported edge-ml model."""
import json

import numpy as np
import torch

with open("manifest.json") as f:
    manifest = json.load(f)
labels = manifest["output"]["labels"]

model = torch.jit.load("model.pt").eval()

# One window per input ({names}); replace the zeros with real data.
# Audio is mono float32 in [-1, 1] at the manifest's sample_rate.
inputs = [{shapes}]

with torch.no_grad():
    scores = model(*[torch.from_numpy(x) for x in inputs])
print("Predicted:", labels[int(scores.argmax(dim=-1))])
'''
