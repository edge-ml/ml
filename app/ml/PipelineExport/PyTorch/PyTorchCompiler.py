"""PyTorch (TorchScript) export — the universal download for any torch model.

Unlike the ExecuTorch (.pte) export, which targets a smartphone and only works
when every op lowers to the mobile runtime (many architectures don't), this
produces a plain TorchScript module that runs anywhere PyTorch runs (a server,
a desktop, a Python script). It reuses the exact same composed module the
ExecuTorch path builds — preprocessing (features + normalization) baked in
front of the trained classifier — so inference matches training, then traces it
with torch.jit so it reloads via torch.jit.load() without any model code.

This is the fallback that makes every trained PyTorch model (WHAR architectures
included) actually downloadable, even when it cannot go on a phone.
"""
import json
from io import BytesIO

import torch

from app.ml.PipelineExport.C.Common.CPart import ExtraFile
from app.ml.PipelineExport.Executorch.ExecutorchCompiler import buildExportModule
from app.ml.PipelineExport.Executorch.support import findOption
from app.ml.Pipelines.Categories.Windowing.BaseWindower import BaseWindower
from app.ml.Pipelines.Categories.FeatureExtraction.BaseFeatureExtractor import (
    BaseFeatureExtractor,
)
from app.ml.Pipelines.Categories.FeatureExtraction.SimpleFeatureExtractor import (
    SimpleFeatureExtractor,
)
from app.ml.Pipelines.Categories.Classifier.BaseClassififer import BaseClassififer


def _torchscript_bytes(module, example_input) -> bytes:
    module = module.eval()
    with torch.no_grad():
        # A warmup forward materializes any lazy (uninitialized) layers before
        # tracing; trained models are already initialized, this is just insurance.
        module(example_input)
        scripted = torch.jit.trace(module, example_input)
    buffer = BytesIO()
    torch.jit.save(scripted, buffer)
    buffer.seek(0)
    return buffer.read()


def _manifest(model, window_size, n_sensors, bakes_features) -> str:
    labels = [l.name for l in (model.labels or [])]
    return json.dumps(
        {
            "name": model.name,
            "framework": "pytorch-torchscript",
            "input_shape": [1, window_size, n_sensors],
            "input_description": (
                "float32 tensor of shape (batch, window_size, num_sensors) — raw "
                "sensor windows. Preprocessing (feature extraction + normalization) "
                "is baked into the model, so feed the raw window directly."
            ),
            "window_size": window_size,
            "num_sensors": n_sensors,
            "sensors": model.timeSeries,
            "samplingRate": model.samplingRate,
            "labels": labels,
            "num_classes": len(labels),
            "bakes_features": bakes_features,
            "output": "raw logits (batch, num_classes); argmax over the last dim gives the class index",
        },
        indent=2,
    )


_README = """# PyTorch model export

This is a TorchScript export of your trained edge-ml model. It runs anywhere
PyTorch runs (a server, a desktop, a Python script) — it is **not** a smartphone
(.pte) or embedded (C) build.

Preprocessing (feature extraction + normalization) is baked into the model, so
you feed it the raw sensor window exactly as recorded.

## Files
- `model.pt` — the TorchScript module (load with `torch.jit.load`).
- `manifest.json` — input shape, sensors, sampling rate and label names.
- `inference.py` — a minimal runnable example.

## Quick start
```
pip install torch numpy
python inference.py
```
"""


def _inference_py(window_size, n_sensors) -> str:
    return f'''"""Minimal inference example for the exported edge-ml PyTorch model."""
import json
import numpy as np
import torch

with open("manifest.json") as f:
    manifest = json.load(f)
labels = manifest["labels"]

model = torch.jit.load("model.pt")
model.eval()

# One window of raw sensor data: (batch, window_size, num_sensors).
# Replace this with your own {window_size}x{n_sensors} window.
window = np.zeros((1, {window_size}, {n_sensors}), dtype=np.float32)

with torch.no_grad():
    logits = model(torch.from_numpy(window))
class_index = int(torch.argmax(logits, dim=-1).item())
print("Predicted:", labels[class_index] if labels else class_index)
'''


def buildPytorchExport(options, model):
    """Bundle the traced model + manifest + README + inference script.

    Works for any PyTorch classifier pipeline; the composed module (baked
    preprocessing + classifier) is the same one the ExecuTorch path uses."""
    windower = findOption(options, BaseWindower)
    featureExtractor = findOption(options, BaseFeatureExtractor)
    classifier = findOption(options, BaseClassififer)

    window_size = int(windower.get_param_value_by_name("window_size"))
    n_sensors = len(model.timeSeries)
    bakes_features = isinstance(featureExtractor, SimpleFeatureExtractor)

    module = buildExportModule(options)
    example_input = torch.zeros(1, window_size, n_sensors, dtype=torch.float32)
    model_bytes = _torchscript_bytes(module, example_input)

    return [
        ExtraFile("model.pt", model_bytes),
        ExtraFile("manifest.json", _manifest(model, window_size, n_sensors, bakes_features)),
        ExtraFile("README.md", _README),
        ExtraFile("inference.py", _inference_py(window_size, n_sensors)),
    ]
