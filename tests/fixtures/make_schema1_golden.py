"""The schema-1 manifests of a fixed sensor-only pipeline, for the golden
test in tests/test_audio_export.py: the audio work (#100) must leave them
exactly as they were. Run from the ml/ directory to regenerate:

    python tests/fixtures/make_schema1_golden.py tests/fixtures/manifest_schema1_golden.json

(only when a change to schema 1 is intended)."""
import json
import os
import sys
import tempfile

if __name__ == "__main__":
    sys.path.insert(0, os.getcwd())
    for key, value in {
        "SECRET_KEY": "test", "API_URI": "http://localhost", "DATABASE_URI": "mongodb://localhost:27017",
        "AUTH_DATABASE_URI": "mongodb://localhost:27017", "CLASSIFIER_STORE": "CLASSIFIER_STORE",
        "TS_STORE_MECHANISM": "FS", "TSDATA": tempfile.mkdtemp(), "S3_URL": "http://localhost:9444",
        "S3_BUCKET_NAME": "test", "S3_ACCESS_KEY": "test", "S3_SECRET_KEY": "test",
        "S3_MODEL_BUCKET_NAME": "test-models", "FIRMWARE_COMPILE_URL": "http://localhost:3005/",
    }.items():
        os.environ.setdefault(key, value)


def schema1_manifests():
    from types import SimpleNamespace

    import numpy as np
    import torch

    import app.DataModels.PipelineRequest  # noqa: F401  (import order: avoids a cycle)
    from app.ml.PipelineExport.Executorch.ExecutorchCompiler import buildExecutorchManifest
    from app.ml.PipelineExport.Onnx.OnnxCompiler import buildOnnxManifest
    from app.ml.PipelineExport.PyTorch.PyTorchCompiler import _manifest as pytorch_manifest
    from app.ml.Pipelines.Categories.Classifier.TorchCNN1D import TorchCNN1D
    from app.ml.Pipelines.Categories.FeatureExtraction.RawSensorExtractor import RawSensorExtractor
    from app.ml.Pipelines.Categories.Normalizer.ZNormalizer import ZNormalizer
    from app.ml.Pipelines.Categories.Windowing.SampleWindower import SampleWindower
    from app.ml.Pipelines.PipelineContainer import PipelineContainer

    torch.manual_seed(0)
    rng = np.random.default_rng(0)
    windower_params = SampleWindower.get_parameters()
    for p in windower_params:
        p.value = {"window_size": 20, "sliding_step": 10}[p.parameter_name]
    windower = SampleWindower(windower_params)
    X = rng.standard_normal((40, 20, 4)).astype(np.float32)  # time + 3 sensors
    y = np.arange(40) % 3
    extractor = RawSensorExtractor([])
    normalizer = ZNormalizer([])
    params = TorchCNN1D.get_parameters()
    for p in params:
        if p.parameter_name == "epochs":
            p.value = 1
    classifier = TorchCNN1D(params)
    data = extractor.fit_exec(PipelineContainer(X, y, [None] * 40))
    classifier.fit_exec(normalizer.fit_exec(data))
    options = [windower, extractor, normalizer, classifier]

    def unit(name):
        return SimpleNamespace(name=name, quantity="acceleration", unit="m/s^2")

    model = SimpleNamespace(
        name="golden", id="0" * 24, timeSeries=["acc_x", "acc_y", "acc_z"], samplingRate=50.0,
        labels=[SimpleNamespace(name=n) for n in ("walk", "run", "sit", "unused")],
        inputUnits=None,
    )
    manifests = {
        "executorch": buildExecutorchManifest(options, model),
        "onnx": buildOnnxManifest(options, model),
        "pytorch": json.loads(pytorch_manifest(model, 20, 3, False)),
    }
    manifests["executorch"]["executorch"]["version"] = "<version>"
    return manifests


if __name__ == "__main__":
    # the app prints while training, so the result goes to a file, not stdout
    with open(sys.argv[1], "w") as f:
        json.dump(schema1_manifests(), f, indent=2, sort_keys=True)
        f.write("\n")
