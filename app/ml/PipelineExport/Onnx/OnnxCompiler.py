"""ONNX export — runs in the browser (onnxruntime-web) and in Node
(onnxruntime-node) via the edge-ml JavaScript library.

Every export is a single graph with the same contract as the ExecuTorch /
PyTorch exports: input `raw_window` float32 (batch, window_size, num_sensors),
preprocessing (feature extraction + normalization) baked in. The output is
`scores` (batch, num_outputs); manifest.json maps each output column to its
label name and says whether the scores are logits (torch) or probabilities
(sklearn).

- PyTorch classifiers: the composed module of the ExecuTorch path is exported
  with torch.onnx.
- sklearn trees: the torch preprocessing (+ flatten, matching reshapeSklearn)
  is exported with torch.onnx, the classifier with skl2onnx, and the two
  graphs are merged.
"""
import json
from io import BytesIO

import torch
from torch import nn

from app.ml.PipelineExport.C.Common.CPart import ExtraFile
from app.units.deploy import input_units, units_summary
from app.ml.PipelineExport.Executorch.ExecutorchCompiler import buildExportModule
from app.ml.PipelineExport.Executorch.support import findOption
from app.ml.PipelineExport.Executorch.torch_ops import (
    TorchMinMaxNormalize,
    TorchSimpleFeatures,
    TorchZNormalize,
)
from app.ml.PipelineExport.Onnx.support import (
    OnnxExportError,
    SKLEARN_CLASSIFIERS,
    getOnnxBlockers,
)
from app.ml.Pipelines.Categories.Windowing.BaseWindower import BaseWindower
from app.ml.Pipelines.Categories.FeatureExtraction.BaseFeatureExtractor import BaseFeatureExtractor
from app.ml.Pipelines.Categories.FeatureExtraction.SimpleFeatureExtractor import SimpleFeatureExtractor
from app.ml.Pipelines.Categories.Normalizer.BaseNormalizer import BaseNormalizer
from app.ml.Pipelines.Categories.Normalizer.MinMaxNormalizer import MinMaxNormalizer
from app.ml.Pipelines.Categories.Classifier.BaseClassififer import BaseClassififer

# onnxruntime-web supports opset 17 everywhere; ai.onnx.ml 3 covers the
# TreeEnsembleClassifier skl2onnx emits for sklearn trees.
OPSET = 17
ML_OPSET = 3
INPUT_NAME = "raw_window"
OUTPUT_NAME = "scores"


class _SklearnPreprocess(nn.Module):
    """features -> normalize -> flatten, i.e. what the sklearn classifier sees
    (reshapeSklearn flattens everything after the batch dim, row-major)."""

    def __init__(self, features: nn.Module, normalize: nn.Module):
        super().__init__()
        self.features = features
        self.normalize = normalize

    def forward(self, x):
        return torch.flatten(self.normalize(self.features(x)), start_dim=1)


def _import_onnx():
    try:
        import onnx
        return onnx
    except ImportError as e:
        raise OnnxExportError(
            "ONNX export is not available on this server (onnx is not installed).",
            status_code=501,
        ) from e


def _window_shape(options, model):
    windower = findOption(options, BaseWindower)
    window_size = int(windower.get_param_value_by_name("window_size"))
    return window_size, len(model.timeSeries)


def _torch_to_onnx(module: nn.Module, example_input, output_name):
    onnx = _import_onnx()
    buffer = BytesIO()
    with torch.no_grad():
        module.eval()(example_input)  # materialize lazy layers before tracing
        torch.onnx.export(
            module,
            (example_input,),
            buffer,
            input_names=[INPUT_NAME],
            output_names=[output_name],
            dynamic_axes={INPUT_NAME: {0: "batch"}, output_name: {0: "batch"}},
            opset_version=OPSET,
            dynamo=False,
        )
    return onnx.load_from_string(buffer.getvalue())


def _preprocess_module(options) -> nn.Module:
    featureExtractor = findOption(options, BaseFeatureExtractor)
    normalizer = findOption(options, BaseNormalizer)

    features = TorchSimpleFeatures() if isinstance(featureExtractor, SimpleFeatureExtractor) else nn.Identity()
    if isinstance(normalizer, MinMaxNormalizer):
        normalize = TorchMinMaxNormalize(normalizer.min, normalizer.max)
    else:  # ZNormalizer
        normalize = TorchZNormalize(normalizer.mean, normalizer.std)
    return _SklearnPreprocess(features, normalize)


def _sklearn_onnx(options, example_input):
    onnx = _import_onnx()
    try:
        from skl2onnx import convert_sklearn
        from skl2onnx.common.data_types import FloatTensorType
    except ImportError as e:
        raise OnnxExportError(
            "ONNX export is not available on this server (skl2onnx is not installed).",
            status_code=501,
        ) from e
    from onnx import compose, helper

    classifier = findOption(options, BaseClassififer)
    clf = classifier.clf

    pre = _torch_to_onnx(_preprocess_module(options), example_input, "features")
    n_features = int(_preprocess_module(options)(example_input).shape[1])

    clf_onnx = convert_sklearn(
        clf,
        initial_types=[("features", FloatTensorType([None, n_features]))],
        options={id(clf): {"zipmap": False}},
        target_opset={"": OPSET, "ai.onnx.ml": ML_OPSET},
    )
    # target_opset is an upper bound: skl2onnx picks the lowest opset its ops
    # need (e.g. 15 for a single-class tree), and merge_models requires both
    # graphs to share the default-domain opset.
    default_opset = next(o.version for o in clf_onnx.opset_import if o.domain in ("", "ai.onnx"))
    if default_opset != OPSET:
        from onnx import version_converter
        clf_onnx = version_converter.convert_version(clf_onnx, OPSET)
    clf_onnx = compose.add_prefix(clf_onnx, prefix="clf_")

    # merge_models requires matching IR versions.
    ir_version = min(pre.ir_version, clf_onnx.ir_version)
    pre.ir_version = ir_version
    clf_onnx.ir_version = ir_version

    merged = compose.merge_models(
        pre,
        clf_onnx,
        io_map=[("features", "clf_features")],
        outputs=["clf_probabilities"],
    )
    # Expose the same output name as the torch export.
    merged.graph.node.append(helper.make_node("Identity", ["clf_probabilities"], [OUTPUT_NAME]))
    probs = merged.graph.output[0]
    merged.graph.output.remove(probs)
    merged.graph.output.append(
        helper.make_tensor_value_info(
            OUTPUT_NAME, onnx.TensorProto.FLOAT, ["batch", len(clf.classes_)]
        )
    )
    onnx.checker.check_model(merged)
    return merged


def buildOnnxModel(options, model) -> bytes:
    """Builds the .onnx bytes for a restored pipeline."""
    blockers = getOnnxBlockers(options)
    if blockers:
        raise OnnxExportError(" ".join(blockers), status_code=400)

    window_size, n_sensors = _window_shape(options, model)
    example_input = torch.zeros(1, window_size, n_sensors, dtype=torch.float32)

    classifier = findOption(options, BaseClassififer)
    if isinstance(classifier, SKLEARN_CLASSIFIERS):
        onnx_model = _sklearn_onnx(options, example_input)
    else:
        onnx_model = _torch_to_onnx(buildExportModule(options), example_input, OUTPUT_NAME)
    return onnx_model.SerializeToString()


def outputLabels(options, model):
    """Label name for every output column of `scores`."""
    labels = [l.name for l in (model.labels or [])]
    classifier = findOption(options, BaseClassififer)
    if isinstance(classifier, SKLEARN_CLASSIFIERS):
        # sklearn only knows the classes it saw; columns follow clf.classes_.
        return [labels[int(c)] if int(c) < len(labels) else str(c) for c in classifier.clf.classes_]
    # A configured label can end up with no windows, so num_classes may be
    # smaller than the label list (same handling as the ExecuTorch manifest).
    return labels[: classifier.arch["num_classes"]]


def buildOnnxManifest(options, model) -> dict:
    windower = findOption(options, BaseWindower)
    featureExtractor = findOption(options, BaseFeatureExtractor)
    normalizer = findOption(options, BaseNormalizer)
    classifier = findOption(options, BaseClassififer)

    window_size = int(windower.get_param_value_by_name("window_size"))
    sliding_step = int(windower.get_param_value_by_name("sliding_step"))
    sampling_rate = float(model.samplingRate) if model.samplingRate is not None else None
    is_sklearn = isinstance(classifier, SKLEARN_CLASSIFIERS)

    manifest = {
        "schema_version": 1,
        "format": "onnx",
        "model_name": model.name,
        "model_id": str(model.id),
        "opset": OPSET,
        "sampling_rate": sampling_rate,
        "window": {"size": window_size, "stride": sliding_step, "unit": "samples"},
        "input": {
            "name": INPUT_NAME,
            "shape": [1, window_size, len(model.timeSeries)],
            "dtype": "float32",
            "layout": "window x channel",
            "timeseries": list(model.timeSeries),
            # Per channel: expected quantity/unit and how to convert to it.
            "units": input_units(model),
        },
        "preprocessing": {
            "baked": [featureExtractor.get_name(), normalizer.get_name()]
            if isinstance(featureExtractor, SimpleFeatureExtractor)
            else [normalizer.get_name()],
            "on_device": ["windowing"],
        },
        "output": {
            "name": OUTPUT_NAME,
            "type": "probabilities" if is_sklearn else "logits",
            "labels": outputLabels(options, model),
        },
    }
    if sampling_rate is not None and sliding_step:
        manifest["classification_frequency_hint_hz"] = sampling_rate / sliding_step
    return manifest


def _readme(model) -> str:
    return f"""# ONNX model export — {model.name}

Runs in the browser (onnxruntime-web) or in Node.js (onnxruntime-node).
Preprocessing (feature extraction + normalization) is baked into the model,
so you only feed it windows of raw sensor values.

## Files
- `model.onnx` — the model. Input `raw_window` float32 `[batch, window_size, num_sensors]`, output `scores`.
- `manifest.json` — window size, sensor order, expected units, sampling rate and the label of every output column.

## Input units
Feed each sensor in the unit the model was trained on. `manifest.json` → `input.units`
lists, per sensor, the conversion from other units (`expected = value * scale + offset`);
the edge-ml library applies it when you tell it your sensor's unit.

```
{units_summary(model)}
```
- `index.html` — a minimal browser example using the edge-ml library.

## Quick start (browser)
Serve this folder (e.g. `npx serve .`) and open `index.html`.

## Quick start (Node.js)
```js
const {{ OnnxPredictor }} = require("edge-ml");
const predictor = await OnnxPredictor.fromFiles("model.onnx", "manifest.json");
predictor.addDatapoint("<sensor>", 0.42);
const {{ prediction }} = await predictor.predict();
```
"""


def _example_html(manifest) -> str:
    sensors = manifest["input"]["timeseries"]
    return f"""<!doctype html>
<html>
<head><meta charset="utf-8"><title>edge-ml ONNX example</title></head>
<body>
<pre id="out">loading…</pre>
<script src="https://cdn.jsdelivr.net/npm/onnxruntime-web/dist/ort.min.js"></script>
<script src="https://unpkg.com/edge-ml/dist/index.browser.js"></script>
<script>
(async () => {{
  const predictor = await edgeML.OnnxPredictor.fromUrls("model.onnx", "manifest.json");
  const sensors = {json.dumps(sensors)};
  setInterval(async () => {{
    // Replace Math.random() with your real sensor readings.
    for (const s of sensors) predictor.addDatapoint(s, Math.random());
    try {{
      const res = await predictor.predict();
      document.getElementById("out").textContent = JSON.stringify(res, null, 2);
    }} catch (e) {{
      document.getElementById("out").textContent = e.message;
    }}
  }}, 1000 / ({manifest.get("sampling_rate") or 10}));
}})();
</script>
</body>
</html>
"""


def buildOnnxExport(options, model):
    manifest = buildOnnxManifest(options, model)
    return [
        ExtraFile("model.onnx", buildOnnxModel(options, model)),
        ExtraFile("manifest.json", json.dumps(manifest, indent=2)),
        ExtraFile("README.md", _readme(model)),
        ExtraFile("index.html", _example_html(manifest)),
    ]
