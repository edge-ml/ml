"""manifest.json schema 2 (#100): models with several inputs (audio, or
sensors and audio). Schema 1 (one `input`, windows counted in samples) stays
what every sensor-only model ships; libraries pick the code path by
`schema_version`.

Differences to schema 1:
- `inputs` is a list, in the order the model takes them. Each has a `kind`:
  "sensors" (window x channel at `sampling_rate`, like schema 1's `input`) or
  "audio" (mono float32 samples in [-1, 1] at `sample_rate`).
- `window` is a duration: `duration_ms` and `stride_ms`.
"""
from app.units.deploy import input_units


def build_manifest_v2(options, model, fmt, extra=None) -> dict:
    from app.ml.PipelineExport.Executorch.support import findOption
    from app.ml.PipelineExport.Onnx.OnnxCompiler import outputLabels
    from app.ml.Pipelines.Categories.Classifier.BaseClassififer import BaseClassififer
    from app.ml.Pipelines.Categories.FeatureExtraction.BaseFeatureExtractor import BaseFeatureExtractor
    from app.ml.Pipelines.Categories.Normalizer.BaseNormalizer import BaseNormalizer
    from app.ml.Pipelines.Categories.Windowing.BaseWindower import BaseWindower

    windower = findOption(options, BaseWindower)
    extractor = findOption(options, BaseFeatureExtractor)
    normalizer = findOption(options, BaseNormalizer)
    classifier = findOption(options, BaseClassififer)

    inputs = []
    for spec in windower.export_inputs():
        entry = {"name": spec["name"], "kind": spec["kind"], "shape": spec["shape"], "dtype": "float32"}
        if spec["kind"] == "sensors":
            entry.update({
                "layout": "window x channel",
                "sampling_rate": spec["sampling_rate"],
                "timeseries": list(model.timeSeries or []),
                "units": input_units(model),
            })
        else:
            recording = next(iter(model.audioInputs or []), None)
            entry.update({
                "sample_rate": spec["sample_rate"],
                "channels": 1,
                "range": [-1.0, 1.0],
                "recording": recording.name if recording is not None else windower.audio_name,
            })
        inputs.append(entry)

    labels = outputLabels(options, model)
    manifest = {
        "schema_version": 2,
        "format": fmt,
        "model_name": model.name,
        "model_id": str(model.id),
        **(extra or {}),
        "window": {"duration_ms": windower.window_ms, "stride_ms": windower.stride_ms},
        "inputs": inputs,
        "preprocessing": {
            "baked": [extractor.get_name(), normalizer.get_name()],
            "on_device": ["windowing", "resampling"],
            "spectrogram": {
                "sample_rate": extractor.sample_rate,
                "n_fft": extractor.n_fft,
                "hop": extractor.hop,
                "n_mels": extractor.n_mels,
                "window": "hann",
                "mel_scale": "htk",
                "log_offset": 1e-6,
            } if extractor.sample_rate else None,
        },
        "output": {
            "name": "scores",
            "type": "logits",
            "shape": [1, classifier.arch["num_classes"]],
            "labels": labels,
        },
    }
    if windower.stride_ms:
        manifest["classification_frequency_hint_hz"] = round(1000.0 / float(windower.stride_ms), 4)
    return manifest
