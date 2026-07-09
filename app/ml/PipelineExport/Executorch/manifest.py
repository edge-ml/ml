import json

from app.ml.Pipelines.Categories.FeatureExtraction.SimpleFeatureExtractor import SimpleFeatureExtractor


def buildManifest(model, windower, featureExtractor, normalizer, classifier, executorch_version):
    window_size = int(windower.get_param_value_by_name("window_size"))
    sliding_step = int(windower.get_param_value_by_name("sliding_step"))
    labels = [x.name for x in model.labels]
    sampling_rate = float(model.samplingRate) if model.samplingRate is not None else None

    manifest = {
        "schema_version": 1,
        "model_name": model.name,
        "model_id": str(model.id),
        "executorch": {
            "version": executorch_version,
            "backend": "xnnpack",
        },
        "sampling_rate": sampling_rate,
        "window": {
            "size": window_size,
            "stride": sliding_step,
            "unit": "samples",
        },
        "input": {
            "name": "raw_window",
            "shape": [1, window_size, len(model.timeSeries)],
            "dtype": "float32",
            "layout": "window x channel",
            "timeseries": list(model.timeSeries),
        },
        "preprocessing": {
            "baked": [featureExtractor.get_name(), normalizer.get_name()]
            if isinstance(featureExtractor, SimpleFeatureExtractor)
            else [normalizer.get_name()],
            "on_device": ["windowing"],
        },
        "output": {
            "type": "logits",
            "shape": [1, classifier.arch["num_classes"]],
            "labels": labels,
        },
    }
    if sampling_rate is not None and sliding_step:
        manifest["classification_frequency_hint_hz"] = sampling_rate / sliding_step

    return json.dumps(manifest, indent=2)
