"""Builds a full PipelineRequest from the compact training request the edge-ml
JavaScript library sends with a device API key.

The frontend wizard posts every step with all of its parameter definitions;
a library user should only have to name what they want to change:

    {
      "name": "my-model",
      "labeling": "activities",                 # labeling name or id
      "datasets": ["walk-1", "run-1"],          # optional: names or ids (default: every dataset with that labeling)
      "timeSeries": ["accX", "accY", "accZ"],   # optional: names (default: series shared by all datasets)
      "disabledLabels": ["idle"],               # optional: label names or ids
      "useZeroClass": false,
      "audio": "mic",                            # optional: recording name; trains on its sound (#100)
      "preset": "small_cnn",                     # optional: see device_presets.PRESETS
      "pipeline": {                              # optional, per step: option name + parameter overrides
        "windowing": {"name": "Sample based", "parameters": {"window_size": 50}},
        "classifier": {"name": "Decision Tree Classifier"}
      }
    }

Defaults produce a pipeline that can be exported to ONNX, so the trained model
runs in the browser. Every preset can also be exported to ExecuTorch; `pipeline`
entries are applied on top of the preset.

Sound: the presets "audio_cnn" and "mixed_cnn", or an `audio` recording name,
train with the audio pipeline. Its models take the recording's sound, plus the
time series for mixed models (all shared ones by default for "mixed_cnn"; only
the named ones otherwise). Without `audio`, the recording every selected
dataset has is used when there is exactly one."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.DataModels.PipelineRequest import (
    PipelineRequest,
    PipelineStep,
    PipelineStepOption,
    SelectedPipeline,
    TrainDatasetModel,
    TrainLabelingModel,
)
from app.ml.device_presets import PRESETS, applyPreset, executorchBlockers
from app.ml.Pipelines.ManualClassificationPipeline import ManualClassificationPipeline
from app.ml.Pipelines.AudioClassificationPipeline import AUDIO_CATEGORIES, AudioClassificationPipeline
from app.ml.Pipelines.Categories.Windowing.SyncedTimeWindower import SyncedTimeWindower
from app.ml.Pipelines.Categories.Windowing import WINDOWING_CATEGORY
from app.ml.Pipelines.Categories.FeatureExtraction import FEATUREEXTRACTION_CATEGORY
from app.ml.Pipelines.Categories.Normalizer import NORMALIZER_CATEGORY
from app.ml.Pipelines.Categories.Classifier import CLASSIFIER_CATEGORY
from app.ml.Pipelines.Categories.Evaluation import EVALUATION_CATEGORY
from app.units.deploy import input_units


class DeviceTrainError(Exception):
    """A request problem the caller can fix (mapped to HTTP 400)."""


class DeviceStepSpec(BaseModel):
    name: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)


class DeviceTrainRequest(BaseModel):
    name: str
    labeling: str
    datasets: Optional[List[str]] = None
    timeSeries: Optional[List[str]] = None
    disabledLabels: List[str] = Field(default_factory=list)
    useZeroClass: bool = False
    preset: Optional[str] = None
    pipeline: Dict[str, DeviceStepSpec] = Field(default_factory=dict)
    # name of the recording whose sound the model takes (audio pipeline)
    audio: Optional[str] = None


# Key used in the request -> (pipeline category, default option name).
# The order is the step order of the manual classification pipeline.
STEPS = {
    "windowing": (WINDOWING_CATEGORY, "Sample based"),
    "featureExtraction": (FEATUREEXTRACTION_CATEGORY, "SimpleFeatureExtractor"),
    "normalizer": (NORMALIZER_CATEGORY, "MinMaxNormalizer"),
    "classifier": (CLASSIFIER_CATEGORY, "Random Forest Classifier"),
    "evaluation": (EVALUATION_CATEGORY, "TestTrainSplit"),
}


# The same keys for the audio pipeline (windows of a fixed duration, sound).
AUDIO_STEPS = {
    key: (category, category.options[0].get_name())
    for key, category in zip(STEPS, AUDIO_CATEGORIES)
}


def _has_sound(media: dict) -> bool:
    return ((media.get("kind") == "audio" or bool((media.get("meta") or {}).get("audioCodec")))
            and (media.get("status") or "ready") == "ready")


def usesAudioPipeline(req: "DeviceTrainRequest") -> bool:
    """Audio presets, a time-based windowing step, or a recording to train on."""
    pipeline = effectivePipeline(req)
    windowing = pipeline.get("windowing")
    if windowing is not None and windowing.name:
        return windowing.name == SyncedTimeWindower.get_name()
    return bool(req.audio)


def _steps(req) -> dict:
    return AUDIO_STEPS if usesAudioPipeline(req) else STEPS


def _matches(doc, ref: str) -> bool:
    return str(doc.get("_id")) == ref or doc.get("name") == ref


def _find_one(docs, ref: str, kind: str):
    found = [d for d in docs if _matches(d, ref)]
    if not found:
        raise DeviceTrainError(f"{kind} '{ref}' does not exist in this project.")
    if len(found) > 1:
        raise DeviceTrainError(f"{kind} name '{ref}' is ambiguous; use its id instead.")
    return found[0]


def _option_cls(key: str, spec: Optional[DeviceStepSpec], steps=STEPS):
    category, default_option = steps[key]
    option_name = (spec.name if spec and spec.name else default_option)
    option_cls = next((o for o in category.options if o.get_name() == option_name), None)
    if option_cls is None:
        available = ", ".join(o.get_name() for o in category.options)
        raise DeviceTrainError(f"Unknown {key} option '{option_name}'. Available: {available}.")
    return option_cls


def effectivePipeline(req: DeviceTrainRequest) -> Dict[str, DeviceStepSpec]:
    """The request's pipeline with its preset (if any) applied underneath."""
    if not req.preset:
        return req.pipeline
    if req.preset not in PRESETS:
        raise DeviceTrainError(f"Unknown preset '{req.preset}'. Available: {', '.join(PRESETS)}.")
    overrides = {key: spec.dict() for key, spec in req.pipeline.items()}
    return {key: DeviceStepSpec(**spec) for key, spec in applyPreset(req.preset, overrides).items()}


def executorchWarning(req: DeviceTrainRequest) -> Optional[str]:
    """A warning when a preset was overridden into a pipeline that can no longer
    be exported to ExecuTorch (only presets promise ExecuTorch support)."""
    if not req.preset:
        return None
    pipeline = effectivePipeline(req)
    steps = _steps(req)
    blockers = executorchBlockers({key: _option_cls(key, pipeline.get(key), steps) for key in steps})
    if not blockers:
        return None
    return (f"With these overrides the '{req.preset}' model cannot be exported to ExecuTorch "
            f"(it needs {', '.join(blockers)}).")


def _build_step(key: str, spec: Optional[DeviceStepSpec], steps=STEPS) -> PipelineStep:
    category, _ = steps[key]
    option_cls = _option_cls(key, spec, steps)
    option_name = option_cls.get_name()

    parameters = option_cls.get_parameters()
    overrides = dict(spec.parameters) if spec else {}
    for parameter in parameters:
        if parameter.parameter_name in overrides:
            parameter.value = overrides.pop(parameter.parameter_name)
    if overrides:
        valid = ", ".join(p.parameter_name for p in parameters) or "none"
        raise DeviceTrainError(
            f"Unknown parameter(s) {', '.join(overrides)} for '{option_name}'. Valid parameters: {valid}."
        )

    return PipelineStep(
        name=category.name,
        description=category.description,
        type=category.type,
        options=PipelineStepOption(
            name=option_cls.get_name(),
            description=option_cls.get_description(),
            parameters=parameters,
        ),
    )


def buildPipelineRequest(req: DeviceTrainRequest, datasets: List[dict], labelings: List[dict]) -> PipelineRequest:
    """datasets / labelings: raw project documents from the dataset store
    (timeseries data not needed, only ids and names)."""
    unknown_steps = set(req.pipeline) - set(STEPS)
    if unknown_steps:
        raise DeviceTrainError(
            f"Unknown pipeline step(s) {', '.join(sorted(unknown_steps))}. Valid steps: {', '.join(STEPS)}."
        )

    labeling = _find_one(labelings, req.labeling, "Labeling")
    labeling_id = str(labeling["_id"])

    audio = usesAudioPipeline(req)
    if req.audio and not audio:
        raise DeviceTrainError(
            f"'audio' needs the audio pipeline, but the {'preset ' + repr(req.preset) if req.preset else 'windowing step'} "
            "uses sample-based windows. Use the preset 'audio_cnn' or 'mixed_cnn'.")
    preset_inputs = PRESETS[req.preset].inputs if req.preset in PRESETS else None
    if req.datasets:
        selected = [_find_one(datasets, ref, "Dataset") for ref in req.datasets]
    else:
        selected = [
            ds for ds in datasets
            if any(str(l.get("labelingId")) == labeling_id for l in ds.get("labelings", []))
        ]
        if not selected:
            raise DeviceTrainError(f"No dataset is labeled with '{labeling['name']}'.")
        if audio and req.audio:
            # by default, the labeled datasets that have the recording
            selected = [ds for ds in selected if any(m.get("name") == req.audio and _has_sound(m)
                                                     for m in ds.get("mediaSeries", []))]
            if not selected:
                raise DeviceTrainError(f"No dataset labeled with '{labeling['name']}' has a recording "
                                       f"'{req.audio}' with sound.")

    recording = None
    if audio:
        recording = req.audio
        if not recording:
            shared = [m["name"] for m in selected[0].get("mediaSeries", []) if _has_sound(m)]
            shared = sorted({n for n in shared if all(any(m.get("name") == n and _has_sound(m)
                                                          for m in ds.get("mediaSeries", [])) for ds in selected)})
            if len(shared) != 1:
                raise DeviceTrainError(
                    "Name the recording to train on with 'audio'. " + (
                        f"The selected datasets share these recordings with sound: {', '.join(shared)}."
                        if shared else "The selected datasets share no recording with sound."))
            recording = shared[0]

    if audio and not req.timeSeries and preset_inputs != "mixed":
        ts_names = []  # sound only, unless sensors are named or the preset mixes them
    elif req.timeSeries:
        ts_names = list(req.timeSeries)
    else:
        ts_names = [ts["name"] for ts in selected[0].get("timeSeries", [])]
        ts_names = [n for n in ts_names if all(any(t["name"] == n for t in ds.get("timeSeries", [])) for ds in selected)]
        if not ts_names:
            raise DeviceTrainError("The selected datasets share no time-series.")

    train_datasets = []
    for ds in selected:
        by_name = {ts["name"]: ts["_id"] for ts in ds.get("timeSeries", [])}
        missing = [n for n in ts_names if n not in by_name]
        if missing:
            raise DeviceTrainError(f"Dataset '{ds['name']}' has no time-series {', '.join(missing)}.")
        media = []
        if recording:
            found = next((m for m in ds.get("mediaSeries", []) if m.get("name") == recording and _has_sound(m)), None)
            if found is None:
                raise DeviceTrainError(f"Dataset '{ds['name']}' has no recording '{recording}' with sound.")
            media = [found["_id"]]
        train_datasets.append(TrainDatasetModel(_id=ds["_id"], timeSeries=[by_name[n] for n in ts_names],
                                                mediaSeries=media))

    disabled = [_find_one(labeling.get("labels", []), ref, "Label")["_id"] for ref in req.disabledLabels]

    pipeline = effectivePipeline(req)
    step_map = AUDIO_STEPS if audio else STEPS
    steps = [_build_step(key, pipeline.get(key), step_map) for key in step_map]
    creator = AudioClassificationPipeline if audio else ManualClassificationPipeline
    return PipelineRequest(
        name=req.name,
        datasets=train_datasets,
        labeling=TrainLabelingModel(_id=labeling["_id"], useZeroClass=req.useZeroClass, disabledLabelIDs=disabled),
        selectedPipeline=SelectedPipeline(
            name=creator.get_name(),
            description=creator.get_description(),
            steps=steps,
        ),
    )


def modelSummary(model) -> dict:
    """What the library needs to poll a training run and pick a model."""
    metrics = None
    for step in model.pipeline.selectedPipeline.steps:
        if step.options.metrics:
            metrics = step.options.metrics
    return {
        "id": str(model.id),
        "name": model.name,
        "trainStatus": model.trainStatus.value if hasattr(model.trainStatus, "value") else model.trainStatus,
        "stage": model.stage,
        "progress": model.progress,
        "error": model.error or None,
        "formats": model.formats or [],
        "preset": getattr(model, "preset", None),
        "labels": [l.name for l in (model.labels or [])],
        "timeSeries": model.timeSeries or [],
        "inputUnits": input_units(model),
        "samplingRate": model.samplingRate,
        # sound the model takes (audio pipeline); [] for sensor models
        "audioInputs": [a.model_dump() for a in (getattr(model, "audioInputs", None) or [])],
        "metrics": metrics,
    }
