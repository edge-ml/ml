"""Pre-flight validation for a training request.

Runs the cheap, deterministic prefix of the pipeline (data load + windowing)
against the *real* data to catch data-dependent problems the wizard cannot see
— e.g. a window larger than the recordings, or fewer than two classes
surviving windowing. It never fits the classifier and never saves a model, so
it is safe to call repeatedly and is independent of the training flow.

Returns a plain dict: { valid: bool, errors: [{step, message}], warnings: [...] }
"""

from app.db.datasets import get_dataset
from app.db.labelings import get_labeling
from app.DataProcessor.DataLoader.DataLoader import processDatasets
from app.DataModels import PipelineRequest
from app.ml.Pipelines import getPipelineOption, getCategory
from app.ml.Pipelines.Abstract.StepType import StepType
from app.ml.Pipelines.PipelineContainer import PipelineContainer


def _msg(step, message):
    return {"step": step, "message": message}


async def preflight_train(trainReq: PipelineRequest, project: str):
    errors = []
    warnings = []

    # --- checks that need no data ---
    if not trainReq.datasets:
        return {"valid": False, "errors": [_msg("datasets", "Select at least one dataset.")], "warnings": warnings}

    datasets = [await get_dataset(x.id, project) for x in trainReq.datasets]
    labeling = await get_labeling(trainReq.labeling.id, project)

    # keep only the selected timeseries (mirrors trainer.init_train)
    for ds in datasets:
        reqDs = next(r for r in trainReq.datasets if r.id == ds.id)
        ds.timeSeries = [ts for ts in ds.timeSeries if ts.id in reqDs.timeSeries]

    if len(datasets[0].timeSeries) == 0:
        errors.append(_msg("datasets", "No timeseries are selected."))
    if not all(len(x.timeSeries) == len(datasets[0].timeSeries) for x in datasets):
        errors.append(_msg("datasets", "Selected datasets have a mismatching number of timeseries."))

    selectedLabels = [l for l in labeling.labels if l.id not in trainReq.labeling.disabledLabelIDs]
    n_classes = len(selectedLabels) + (1 if trainReq.labeling.useZeroClass else 0)
    if len(selectedLabels) == 0:
        errors.append(_msg("labeling", "Select at least one label."))
    elif n_classes < 2:
        errors.append(_msg("labeling", "At least two classes are required — enable another label or the zero-class."))

    if errors:
        return {"valid": False, "errors": errors, "warnings": warnings}

    # --- run the deterministic prefix (load + windowing) on the real data ---
    labelMap = {str(x.id): i for i, x in enumerate(selectedLabels)}
    maxIdx = max(labelMap.values())
    if trainReq.labeling.useZeroClass:
        labelMap["Zero"] = maxIdx + 1

    try:
        datasets_processed, datasetMetaData, samplingRate = processDatasets(
            datasets, trainReq.labeling, labelMap
        )
    except Exception as e:
        return {"valid": False, "errors": [_msg("datasets", f"Could not load the selected data: {e}")], "warnings": warnings}

    windowStep = next(
        (s for s in trainReq.selectedPipeline.steps if getCategory(s.name).type == StepType.PRE),
        None,
    )
    if windowStep is None:
        return {"valid": False, "errors": [_msg("windowing", "No windowing step is configured.")], "warnings": warnings}

    windower = getPipelineOption(windowStep.options.name)(windowStep.options.parameters)
    try:
        windowed = windower.fit_exec(PipelineContainer(datasets_processed, None, datasetMetaData))
    except Exception:
        # SampleWindower raises (e.g. IndexError on train_X[0]) when no windows survive.
        errors.append(_msg(
            "windowing",
            "No windows could be produced. The window size is likely larger than your "
            "recordings, or the sliding step is too large — reduce the window size or step.",
        ))
        return {"valid": False, "errors": errors, "warnings": warnings}

    labels_after = list(windowed.labels) if windowed.labels is not None else []
    n_windows = len(labels_after)
    n_unique = len({int(x) for x in labels_after}) if n_windows else 0

    if n_windows == 0:
        errors.append(_msg("windowing", "No labeled windows were produced for the selected data and window settings."))
    elif n_unique < 2:
        errors.append(_msg(
            "windowing",
            f"Only {n_unique} class has data after windowing; at least 2 are needed to train. "
            "Check that the selected datasets actually contain the enabled labels in the chosen window.",
        ))
    elif n_windows < 10:
        warnings.append(_msg(
            "windowing",
            f"Only {n_windows} training windows were produced — the model may train poorly. "
            "Consider a smaller window/step or more data.",
        ))

    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}
