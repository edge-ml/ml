"""Training and exporting audio models (#100): audio-only, sensor-only and
mixed models through the whole pipeline, persist/restore, numerical parity of
the ExecuTorch, ONNX and TorchScript exports, manifest schema 2, the
unchanged schema 1 (golden), export gating and the preflight.

Run from the ml/ directory: pytest tests/test_audio_export.py -v
"""

import io
import json
import os
import sys
import tempfile
import unittest
from types import SimpleNamespace

_TSDATA_DIR = tempfile.mkdtemp(prefix="edgeml_test_audio_export_")
_TEST_ENV = {
    "SECRET_KEY": "test",
    "API_URI": "http://localhost",
    "DATABASE_URI": "mongodb://localhost:27017",
    "AUTH_DATABASE_URI": "mongodb://localhost:27017",
    "CLASSIFIER_STORE": "CLASSIFIER_STORE",
    "TS_STORE_MECHANISM": "FS",
    "TSDATA": _TSDATA_DIR,
    "S3_URL": "http://localhost:9444",
    "S3_BUCKET_NAME": "test",
    "S3_ACCESS_KEY": "test",
    "S3_SECRET_KEY": "test",
    "S3_MODEL_BUCKET_NAME": "test-models",
    "FIRMWARE_COMPILE_URL": "http://localhost:3005/",
    "AUDIO_CACHE_DIR": os.path.join(_TSDATA_DIR, "audio-cache"),
}
for key, value in _TEST_ENV.items():
    os.environ.setdefault(key, value)

import numpy as np
import torch

from app.DataModels.PipelineRequest import PipelineStepOption
from app.DataModels.dataset import DatasetSchema
from app.DataModels.model import AudioInput
from app.DataProcessor.DataLoader import media
from app.DataProcessor.DataLoader.recordings import LabelIntervals, RecordingSource, RecordingsError, align_sources
from app.ml.Pipeline import Pipeline
from app.ml.Pipelines.AudioClassificationPipeline import AUDIO_CATEGORIES, AudioClassificationPipeline
from app.ml.Pipelines.Abstract.StepType import StepType
from app.ml.Pipelines.Categories.Classifier.TorchMultimodalCNN import TorchMultimodalCNN
from app.ml.Pipelines.Categories.Classifier.decision_tree import DecisionTree
from app.ml.Pipelines.Categories.Evaluation.TestTrainSplitEvaluation import TestTrainSplitEvaluation
from app.ml.Pipelines.Categories.FeatureExtraction.LogMelSensorExtractor import LogMelSensorExtractor
from app.ml.Pipelines.Categories.Normalizer.ChannelZNormalizer import ChannelZNormalizer
from app.ml.Pipelines.Categories.Windowing.SyncedTimeWindower import SyncedTimeWindower
from app.ml.Pipelines.PipelineContainer import PipelineContainer
from app.ml.PipelineExport import torch_export
from app.ml.PipelineExport.Executorch.ExecutorchCompiler import (
    assembleExecutorchFiles,
    buildExecutorchManifest,
    buildExecutorchPte,
)
from app.ml.PipelineExport.Executorch.support import getExportBlockers
from app.ml.PipelineExport.Onnx.OnnxCompiler import buildOnnxExport
from app.ml.PipelineExport.Onnx.support import getOnnxBlockers
from app.ml.PipelineExport.PyTorch.PyTorchCompiler import buildPytorchExport
from app.ml.PipelineExport.formats import computeFormats
from app.ml.validation import _preflight_recordings

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "fixtures"))
from make_schema1_golden import schema1_manifests  # noqa: E402

RATE = 16000
SECONDS = 24


def params(cls, **values):
    out = cls.get_parameters()
    for p in out:
        if p.parameter_name in values:
            p.value = values[p.parameter_name]
    return out


def synthetic(seed=0, sensors=True, audio=True):
    """24 s alternating every 2 s between class 0 (a 440 Hz tone, the device
    still) and class 1 (noise, the device shaking)."""
    rng = np.random.default_rng(seed)
    t = np.arange(SECONDS * RATE) / RATE
    cls = (t // 2).astype(int) % 2
    pcm = np.where(cls == 0, 0.3 * np.sin(2 * np.pi * 440 * t), 0.3 * rng.standard_normal(len(t)))
    pcm = (pcm * 32767).astype(np.int16)
    st = np.arange(0, SECONDS * 1000 + 1, 20.0)
    moving = ((st // 2000).astype(int) % 2) == 1
    channels = [(st, np.where(moving, np.sin(st / 30.0) * 5, 0.0) + rng.normal(0, 0.1, len(st))),
                (st, np.where(moving, np.cos(st / 25.0) * 5, 0.0) + rng.normal(0, 0.1, len(st)))]
    starts = np.arange(0, SECONDS * 1000, 2000.0)
    labels = LabelIntervals(starts=starts, ends=starts + 1999, classes=np.arange(len(starts)) % 2)
    from app.DataModels.dataset import MediaSeries

    media_id = f"{seed:024d}"
    src = RecordingSource(
        dataset_id=f"ds{seed}", meta={"subject": f"s{seed}"},
        sensor_names=["acc_x", "acc_y"] if sensors else [], sensor_ids=["x", "y"] if sensors else [],
        sensor_spans=[(0.0, SECONDS * 1000.0)] * (2 if sensors else 0),
        sensor_periods_ms=[20.0] * (2 if sensors else 0), conversions={},
        audio=MediaSeries(_id=media_id, kind="audio", name="mic", start=0, end=SECONDS * 1000,
                          durationMs=SECONDS * 1000) if audio else None,
        labels=labels,
    )
    src._sensors = [(a, b.astype(np.float32)) for a, b in channels] if sensors else []
    return src, media_id, pcm


class AudioPipelineCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._load = media.load_audio
        cls.pcm = {}
        media.load_audio = lambda media_id, rate: cls.pcm[str(media_id)]

    @classmethod
    def tearDownClass(cls):
        media.load_audio = cls._load

    def train(self, sensors=True, audio=True, epochs=8):
        torch.manual_seed(0)
        sources = []
        for seed in (0, 1):
            src, media_id, pcm = synthetic(seed, sensors, audio)
            self.pcm[media_id] = pcm
            sources.append(src)
        options = [
            # a 1 s step keeps every window inside one 2 s label block
            SyncedTimeWindower(params(SyncedTimeWindower, window_ms=1000, stride_ms=1000)),
            LogMelSensorExtractor(LogMelSensorExtractor.get_parameters()),
            ChannelZNormalizer([]),
            TorchMultimodalCNN(params(TorchMultimodalCNN, size="small", epochs=epochs)),
            TestTrainSplitEvaluation(params(TestTrainSplitEvaluation, Train_test_split=75)),
        ]
        pipeline = Pipeline(options, AUDIO_CATEGORIES)
        windower = options[0]
        try:
            metrics = pipeline.eval(PipelineContainer(sources, None, [s.meta for s in sources]), ["still", "shaking"])
            # what the export tests feed: the raw inputs of a few windows
            rows = pipeline.exec(PipelineContainer(sources, None, None), StepType.PRE).data[:6]
            inputs = []
            for spec in windower.export_inputs():
                inputs.append(windower.sensors_for(rows) if spec["kind"] == "sensors" else windower.audio_for(rows))
            expected = self.python_scores(pipeline, rows)
        finally:
            windower.release()
        model = SimpleNamespace(
            name="kitchen", id="1" * 24, timeSeries=windower.channels, samplingRate=windower.sensor_rate,
            labels=[SimpleNamespace(name="still"), SimpleNamespace(name="shaking")], inputUnits=None,
            audioInputs=[AudioInput(name="mic", sampleRate=RATE)] if audio else [],
        )
        return pipeline, model, metrics, inputs, expected

    @staticmethod
    def python_scores(pipeline, rows):
        """Logits of the trained python pipeline (extractor, normalizer, net)."""
        _, extractor, normalizer, classifier, _ = pipeline.options
        feats = normalizer.normalize(extractor.extract_features(rows))
        with torch.no_grad():
            return classifier.model(torch.from_numpy(np.asarray(feats, dtype=np.float32))).numpy()


class TrainingTest(AudioPipelineCase):

    def test_audio_only_learns(self):
        pipeline, model, metrics, inputs, _ = self.train(sensors=False)
        self.assertGreater(metrics["metrics"]["accuracy_score"], 0.9)
        self.assertEqual(pipeline.options[1].layout["sensors"], None)
        self.assertEqual(computeFormats(pipeline.options), ["EXECUTORCH", "PYTORCH", "ONNX"])

    def test_sensor_only_learns(self):
        pipeline, model, metrics, inputs, _ = self.train(audio=False)
        self.assertGreater(metrics["metrics"]["accuracy_score"], 0.9)
        self.assertEqual(pipeline.options[0].export_inputs()[0]["name"], "raw_window")

    def test_mixed_persist_restore(self):
        pipeline, model, metrics, inputs, expected = self.train()
        self.assertGreater(metrics["metrics"]["accuracy_score"], 0.9)
        # through the model document, as the trainer and getPipeline do
        stored = [PipelineStepOption.model_validate(json.loads(json.dumps(o.persist(), default=lambda x: x.model_dump() if hasattr(x, "model_dump") else str(x))))
                  for o in pipeline.options]
        restored = []
        for option, config in zip(pipeline.options, stored):
            fresh = type(option)()
            fresh.restore(config)
            restored.append(fresh)
        module = torch_export.build_module(restored)
        with torch.no_grad():
            got = module(*[torch.from_numpy(x) for x in inputs]).numpy()
        np.testing.assert_allclose(got, expected, atol=1e-4)


class ExportTest(AudioPipelineCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mixed = None

    def get_mixed(self):
        if ExportTest.mixed is None:
            ExportTest.mixed = self.train(epochs=2)
        return ExportTest.mixed

    def test_executorch_parity(self):
        from executorch.runtime import Runtime

        pipeline, model, _, inputs, expected = self.get_mixed()
        pte = buildExecutorchPte(pipeline.options, model)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "model.pte")
            with open(path, "wb") as f:
                f.write(pte)
            method = Runtime.get().load_program(path).load_method("forward")
            for i in range(len(expected)):
                out = method.execute([torch.from_numpy(x[i:i + 1]) for x in inputs])[0].numpy()
                np.testing.assert_allclose(out, expected[i:i + 1], atol=1e-3)
        files = {f.name: f for f in assembleExecutorchFiles(pipeline.options, model, pte)}
        self.assertEqual(sorted(files), ["README.md", "manifest.json", "model.pte"])
        self.assertIn("16000 Hz", files["README.md"].content)

    def test_onnx_parity(self):
        import onnxruntime as ort

        pipeline, model, _, inputs, expected = self.get_mixed()
        files = {f.name: f for f in buildOnnxExport(pipeline.options, model)}
        session = ort.InferenceSession(files["model.onnx"].content)
        self.assertEqual([i.name for i in session.get_inputs()], ["raw_window", "audio"])
        # the whole batch at once: the batch dimension is dynamic
        out = session.run(None, {"raw_window": inputs[0], "audio": inputs[1]})[0]
        np.testing.assert_allclose(out, expected, atol=1e-3)
        manifest = json.loads(files["manifest.json"].content)
        self.assertEqual(manifest["format"], "onnx")
        self.assertEqual(manifest["opset"], 17)

    def test_torchscript_parity_and_example(self):
        pipeline, model, _, inputs, expected = self.get_mixed()
        files = {f.name: f for f in buildPytorchExport(pipeline.options, model)}
        traced = torch.jit.load(io.BytesIO(files["model.pt"].content))
        with torch.no_grad():
            out = traced(*[torch.from_numpy(x) for x in inputs]).numpy()
        np.testing.assert_allclose(out, expected, atol=1e-4)
        with tempfile.TemporaryDirectory() as tmp:
            for name in ("model.pt", "manifest.json", "inference.py"):
                content = files[name].content
                with open(os.path.join(tmp, name), "wb" if isinstance(content, bytes) else "w") as f:
                    f.write(content)
            import subprocess

            res = subprocess.run([sys.executable, "inference.py"], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertRegex(res.stdout, r"Predicted: (still|shaking)")

    def test_manifest_v2(self):
        pipeline, model, _, _, _ = self.get_mixed()
        manifest = buildExecutorchManifest(pipeline.options, model)
        self.assertEqual(manifest["schema_version"], 2)
        self.assertEqual(manifest["window"], {"duration_ms": 1000.0, "stride_ms": 1000.0})
        sensors, audio = manifest["inputs"]
        self.assertEqual(sensors["name"], "raw_window")
        self.assertEqual(sensors["shape"], [1, 50, 2])
        self.assertEqual(sensors["sampling_rate"], 50.0)
        self.assertEqual(sensors["timeseries"], ["acc_x", "acc_y"])
        self.assertEqual(len(sensors["units"]), 2)
        self.assertEqual(audio, {"name": "audio", "kind": "audio", "shape": [1, 16000], "dtype": "float32",
                                 "sample_rate": 16000, "channels": 1, "range": [-1.0, 1.0], "recording": "mic"})
        self.assertEqual(manifest["preprocessing"]["spectrogram"]["n_fft"], 400)
        self.assertEqual(manifest["output"]["labels"], ["still", "shaking"])
        self.assertEqual(manifest["classification_frequency_hint_hz"], 1.0)
        self.assertNotIn("input", manifest)


class GatingTest(unittest.TestCase):

    def test_no_c_and_blockers(self):
        options = [SyncedTimeWindower([]), LogMelSensorExtractor([]), ChannelZNormalizer([]), TorchMultimodalCNN([])]
        self.assertEqual(getExportBlockers(options), [])
        self.assertEqual(getOnnxBlockers(options), [])
        self.assertNotIn("C", computeFormats(options))
        tree = [SyncedTimeWindower([]), LogMelSensorExtractor([]), ChannelZNormalizer([]), DecisionTree([])]
        self.assertEqual(len(getExportBlockers(tree)), 1)
        self.assertEqual(computeFormats(tree), [])

    def test_pipeline_is_offered(self):
        from app.ml.Pipelines import PIPELINES_CONFIG

        config = next(p for p in PIPELINES_CONFIG if p["name"] == AudioClassificationPipeline.get_name())
        self.assertTrue(config["usesRecordings"])
        self.assertNotIn("usesRecordings", PIPELINES_CONFIG[0])
        self.assertEqual([s["name"] for s in config["steps"]], ["Windowing", "Feature extraction", "Normalizer", "Classifier", "Evaluator"])
        classifier = config["steps"][3]["options"][0]
        self.assertFalse(classifier["exportTargets"]["c"])
        self.assertTrue(classifier["exportTargets"]["onnx"])

    def test_schema1_manifests_unchanged(self):
        with open(os.path.join(os.path.dirname(__file__), "fixtures", "manifest_schema1_golden.json")) as f:
            golden = json.load(f)
        self.assertEqual(json.loads(json.dumps(schema1_manifests(), sort_keys=True)), golden)


def dataset(name, media=None, sensors=("acc_x",), labels=((0, 4999, "a"), (5000, 9999, "b"))):
    lid = "6" * 24
    types = {"a": "a" * 24, "b": "b" * 24}
    return DatasetSchema.model_validate({
        "_id": f"{abs(hash(name)) % 10 ** 24:024d}", "name": name, "metaData": {},
        "timeSeries": [{"_id": f"{i + 1:024d}", "name": n, "start": 0, "end": 10000,
                        "samplingRate": {"mean": 20, "var": 0}} for i, n in enumerate(sensors)],
        "labelings": [{"labelingId": lid, "labels": [{"start": s, "end": e, "type": types[t]} for s, e, t in labels]}],
        "mediaSeries": media or [],
    }), {"_id": lid, "useZeroClass": False, "disabledLabelIDs": []}, {types["a"]: 0, types["b"]: 1}


def recording(name="mic", **extra):
    base = {"_id": "c" * 24, "kind": "audio", "name": name, "start": 0, "end": 10000, "durationMs": 10000,
            "status": "ready", "meta": {"audioCodec": "aac", "sampleRate": 44100}}
    base.update(extra)
    return base


class PreflightTest(unittest.TestCase):

    def run_preflight(self, datasets, window_ms=1000, stride_ms=500):
        from app.DataModels.PipelineRequest import TrainLabelingModel

        dss = [d for d, _, _ in datasets]
        labeling = TrainLabelingModel.model_validate(datasets[0][1])
        req = SimpleNamespace(labeling=labeling)
        step = SimpleNamespace(options=SimpleNamespace(
            name=SyncedTimeWindower.get_name(), parameters=params(SyncedTimeWindower, window_ms=window_ms, stride_ms=stride_ms)))
        return _preflight_recordings(req, dss, step, datasets[0][2], {}, [], [])

    def test_valid(self):
        res = self.run_preflight([dataset("one", [recording()]), dataset("two", [recording()])])
        self.assertTrue(res["valid"], res)

    def test_silent_video_and_processing(self):
        res = self.run_preflight([dataset("one", [recording(kind="video", meta={"audioCodec": None})])])
        self.assertIn("no sound track", res["errors"][0]["message"])
        res = self.run_preflight([dataset("one", [recording(status="processing")])])
        self.assertIn("still being processed", res["errors"][0]["message"])

    def test_audio_in_some_datasets_only(self):
        res = self.run_preflight([dataset("one", [recording()]), dataset("two")])
        self.assertIn("1 of 2 selected datasets have no selected recording", res["errors"][0]["message"])

    def test_two_recordings_and_low_rate(self):
        res = self.run_preflight([dataset("one", [recording(), recording("other", _id="d" * 24)])])
        self.assertIn("select one recording", res["errors"][0]["message"])
        res = self.run_preflight([dataset("one", [recording(meta={"audioCodec": "pcm_s16le", "sampleRate": 8000})])])
        self.assertTrue(res["valid"])
        self.assertIn("8000 Hz", res["warnings"][0]["message"])

    def test_caps(self):
        import app.ml.Pipelines.Categories.Windowing.SyncedTimeWindower  # noqa: F401
        import app.internal.config as config

        old = config.MAX_TRAIN_WINDOWS
        config.MAX_TRAIN_WINDOWS = 5
        try:
            res = self.run_preflight([dataset("one", [recording()])])
        finally:
            config.MAX_TRAIN_WINDOWS = old
        self.assertIn("at most 5", res["errors"][0]["message"])

    def test_one_class_left(self):
        res = self.run_preflight([dataset("one", [recording()], labels=((0, 9999, "a"),))])
        self.assertIn("Only 1 class", res["errors"][0]["message"])

    def test_different_sensors(self):
        a = synthetic(0)[0]
        b = synthetic(1)[0]
        b.sensor_names = ["acc_y", "acc_x"]
        aligned = align_sources([a, b])
        self.assertEqual(aligned[1].sensor_ids, ["y", "x"])
        b.sensor_names = ["gyro_x", "acc_x"]
        with self.assertRaises(RecordingsError):
            align_sources([a, b])


if __name__ == "__main__":
    unittest.main()


class TrainerTest(unittest.TestCase):
    """init_train end to end for a mixed model: datasets and labeling from
    (mocked) Mongo, sensors from the file store, audio from (mocked) storage."""

    def test_init_train_mixed(self):
        import asyncio
        from unittest import mock

        from app.DataModels.PipelineRequest import PipelineRequest
        from app.DataModels.labelings import LabelingModel
        from app.DataModels.model import Model, ModelStatus
        from app.DataProcessor.DataLoader.binaryStore import BinaryStore
        from app.ml import trainer

        project, labeling_id = "7" * 24, "6" * 24
        still, shaking = "a" * 24, "b" * 24
        datasets = {}
        pcm = {}
        for n in range(2):
            src, media_id, audio = synthetic(n)
            pcm[media_id] = audio
            series = []
            for c, (times, values) in enumerate(src._sensors):
                ts_id = f"{n + 1}{c + 1}".ljust(24, "0")
                store = BinaryStore(ts_id)
                store.time_arr = times.astype(np.uint64)
                store.data_arr = values
                store.saveSeries()
                series.append({"_id": ts_id, "name": src.sensor_names[c], "start": 0, "end": SECONDS * 1000,
                               "samplingRate": {"mean": 20, "var": 0}})
            ds_id = f"{n + 1}".ljust(24, "d")
            datasets[ds_id] = DatasetSchema.model_validate({
                "_id": ds_id, "name": f"kitchen {n}", "metaData": {"subject": f"s{n}"}, "timeSeries": series,
                "labelings": [{"labelingId": labeling_id, "labels": [
                    {"start": int(s), "end": int(e), "type": still if c == 0 else shaking}
                    for s, e, c in zip(src.labels.starts, src.labels.ends, src.labels.classes)]}],
                "mediaSeries": [{"_id": media_id, "kind": "video", "name": "mic", "start": 0, "end": SECONDS * 1000,
                                 "durationMs": SECONDS * 1000, "status": "ready", "meta": {"audioCodec": "aac"}},
                                {"_id": "e" * 24, "kind": "audio", "name": "not selected", "start": 0, "end": 1000,
                                 "durationMs": 1000, "meta": {"audioCodec": "mp3"}}],
            })
        labeling = LabelingModel.model_validate({"_id": labeling_id, "name": "activity", "projectId": project, "labels": [
            {"_id": still, "name": "still", "color": "#000000"}, {"_id": shaking, "name": "shaking", "color": "#ffffff"}]})

        steps = []
        overrides = {"Windowing": {"window_ms": 1000, "stride_ms": 1000}, "Classifier": {"size": "small", "epochs": 6},
                     "Evaluator": {"Train_test_split": 75}}
        for category in AUDIO_CATEGORIES:
            option = category.options[0]
            steps.append({"name": category.name, "description": category.description, "type": category.type,
                          "options": {"name": option.get_name(), "description": option.get_description(),
                                      "parameters": params(option, **overrides.get(category.name, {}))}})
        req = PipelineRequest.model_validate({
            "name": "kitchen", "options": [],
            "datasets": [{"_id": ds_id, "timeSeries": [ts.id for ts in ds.timeSeries], "mediaSeries": [ds.mediaSeries[0].id]}
                         for ds_id, ds in datasets.items()],
            "labeling": {"_id": labeling_id, "useZeroClass": False, "disabledLabelIDs": []},
            "selectedPipeline": {"name": AudioClassificationPipeline.get_name(), "description": "", "steps": steps},
        })
        model = Model(name="kitchen", pipeline=req, projectId=project)

        async def get_dataset(id, _):
            return datasets[str(id)].model_copy(deep=True)

        async def get_labeling(id, _):
            return labeling

        old_load = media.load_audio
        media.load_audio = lambda media_id, rate: pcm[str(media_id)]
        try:
            with mock.patch.object(trainer, "get_dataset", get_dataset), \
                    mock.patch.object(trainer, "get_labeling", get_labeling), \
                    mock.patch.object(trainer, "modelDB") as db:
                asyncio.run(trainer.init_train(req, model, model.id, project))
        finally:
            media.load_audio = old_load

        self.assertEqual(model.trainStatus, ModelStatus.done, model.error)
        self.assertEqual(model.timeSeries, ["acc_x", "acc_y"])
        self.assertEqual(model.samplingRate, 50.0)
        self.assertEqual([a.model_dump() for a in model.audioInputs], [{"name": "mic", "sampleRate": 16000}])
        self.assertEqual(model.formats, ["EXECUTORCH", "PYTORCH", "ONNX"])
        evaluator = model.pipeline.selectedPipeline.steps[-1].options
        self.assertGreater(evaluator["metrics"]["metrics"]["accuracy_score"], 0.9)
        self.assertTrue(db.update_model.called)
        # the decoded audio is not kept after training
        from app.ml.Pipelines.Categories.Windowing import SyncedTimeWindower as windowing
        self.assertEqual(windowing._ACTIVE, {})
