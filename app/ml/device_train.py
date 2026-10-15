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
      "preset": "small_cnn",                     # optional: see device_presets.PRESETS
      "pipeline": {                              # optional, per step: option name + parameter overrides
        "windowing": {"name": "Sample based", "parameters": {"window_size": 50}},
        "classifier": {"name": "Decision Tree Classifier"}
      }
    }

Defaults produce a pipeline that can be exported to ONNX, so the trained model
runs in the browser. Every preset can also be exported to ExecuTorch; `pipeline`
entries are applied on top of the preset."""

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
from app.ml.Pipelines.Categories.Windowing import WINDOWING_CATEGORY
from app.ml.Pipelines.Categories.FeatureExtraction import FEATUREEXTRACTION_CATEGORY
from app.ml.Pipelines.Categories.Normalizer import NORMALIZER_CATEGORY
from app.ml.Pipelines.Categories.Classifier import CLASSIFIER_CATEGORY
from app.ml.Pipelines.Categories.Evaluation import EVALUATION_CATEGORY


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


# Key used in the request -> (pipeline category, default option name).
# The order is the step order of the manual classification pipeline.
STEPS = {
    "windowing": (WINDOWING_CATEGORY, "Sample based"),
    "featureExtraction": (FEATUREEXTRACTION_CATEGORY, "SimpleFeatureExtractor"),
    "normalizer": (NORMALIZER_CATEGORY, "MinMaxNormalizer"),
    "classifier": (CLASSIFIER_CATEGORY, "Random Forest Classifier"),
    "evaluation": (EVALUATION_CATEGORY, "TestTrainSplit"),
}


def _matches(doc, ref: str) -> bool:
    return str(doc.get("_id")) == ref or doc.get("name") == ref


def _find_one(docs, ref: str, kind: str):
    found = [d for d in docs if _matches(d, ref)]
    if not found:
        raise DeviceTrainError(f"{kind} '{ref}' does not exist in this project.")
    if len(found) > 1:
        raise DeviceTrainError(f"{kind} name '{ref}' is ambiguous; use its id instead.")
    return found[0]


def _option_cls(key: str, spec: Optional[DeviceStepSpec]):
    category, default_option = STEPS[key]
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
    blockers = executorchBlockers({key: _option_cls(key, pipeline.get(key)) for key in STEPS})
    if not blockers:
        return None
    return (f"With these overrides the '{req.preset}' model cannot be exported to ExecuTorch "
            f"(it needs {', '.join(blockers)}).")


def _build_step(key: str, spec: Optional[DeviceStepSpec]) -> PipelineStep:
    category, _ = STEPS[key]
    option_cls = _option_cls(key, spec)
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

    if req.datasets:
        selected = [_find_one(datasets, ref, "Dataset") for ref in req.datasets]
    else:
        selected = [
            ds for ds in datasets
            if any(str(l.get("labelingId")) == labeling_id for l in ds.get("labelings", []))
        ]
        if not selected:
            raise DeviceTrainError(f"No dataset is labeled with '{labeling['name']}'.")

    if req.timeSeries:
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
        train_datasets.append(TrainDatasetModel(_id=ds["_id"], timeSeries=[by_name[n] for n in ts_names]))

    disabled = [_find_one(labeling.get("labels", []), ref, "Label")["_id"] for ref in req.disabledLabels]

    pipeline = effectivePipeline(req)
    steps = [_build_step(key, pipeline.get(key)) for key in STEPS]
    return PipelineRequest(
        name=req.name,
        datasets=train_datasets,
        labeling=TrainLabelingModel(_id=labeling["_id"], useZeroClass=req.useZeroClass, disabledLabelIDs=disabled),
        selectedPipeline=SelectedPipeline(
            name=ManualClassificationPipeline.get_name(),
            description=ManualClassificationPipeline.get_description(),
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
        "samplingRate": model.samplingRate,
        "metrics": metrics,
    }
