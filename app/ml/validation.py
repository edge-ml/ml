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
from app.units.resolve import UnitError, resolve_units


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

    # keep only the selected timeseries and recordings (mirrors trainer.init_train)
    for ds in datasets:
        reqDs = next(r for r in trainReq.datasets if r.id == ds.id)
        ds.timeSeries = [ts for ts in ds.timeSeries if ts.id in reqDs.timeSeries]
        ds.mediaSeries = [m for m in ds.mediaSeries if m.id in reqDs.mediaSeries]

    windowStep = next(
        (s for s in trainReq.selectedPipeline.steps if getCategory(s.name).type == StepType.PRE),
        None,
    )
    usesRecordings = windowStep is not None and getattr(
        getPipelineOption(windowStep.options.name), "consumes_recordings", False)

    if usesRecordings:
        if all(len(ds.timeSeries) == 0 and len(ds.mediaSeries) == 0 for ds in datasets):
            errors.append(_msg("datasets", "Select sensors, a recording, or both."))
    elif len(datasets[0].timeSeries) == 0:
        errors.append(_msg("datasets", "No timeseries are selected."))
    if not all(len(x.timeSeries) == len(datasets[0].timeSeries) for x in datasets):
        errors.append(_msg("datasets", "Selected datasets have a mismatching number of timeseries."))

    conversions = {}
    try:
        _, conversions = resolve_units(datasets)
    except UnitError as e:
        errors.append(_msg("datasets", str(e)))

    selectedLabels = [l for l in labeling.labels if l.id not in trainReq.labeling.disabledLabelIDs]
    n_classes = len(selectedLabels) + (1 if trainReq.labeling.useZeroClass else 0)
    if len(selectedLabels) == 0:
        errors.append(_msg("labeling", "Select at least one label."))
    elif n_classes < 2:
        errors.append(_msg("labeling", "At least two classes are required — enable another label or the zero-class."))

    # Classifiers that consume the raw window sequence must be paired with the raw
    # feature extractor; the aggregated SimpleFeatureExtractor would feed them the
    # wrong shape (silently poor training, or an error on short input).
    RAW_ONLY_CLASSIFIERS = {"WHAR Model", "PyTorch 1D Convolutional Neural Network"}
    RAW_EXTRACTOR = "Raw Time-Series (Sensors only)"
    optionNames = [s.options.name for s in trainReq.selectedPipeline.steps]
    rawOnly = next((n for n in optionNames if n in RAW_ONLY_CLASSIFIERS), None)
    if rawOnly is not None and RAW_EXTRACTOR not in optionNames:
        errors.append(_msg(
            "featureExtraction",
            f"'{rawOnly}' needs the '{RAW_EXTRACTOR}' feature extraction. Go back to the "
            f"Feature Extraction step and select it.",
        ))

    # A few WHAR architectures constrain the channel count: deepsense splits the
    # channels into an acc/gyro pair (needs an even count) and global_fusion needs
    # enough channels to fuse (>= 6). They're offered in the picker but only work
    # when the selected data fits; block early with a clear message instead of a
    # cryptic shape error at fit time. Channel count = selected timeseries.
    n_channels = len(datasets[0].timeSeries)
    wharStep = next((s for s in trainReq.selectedPipeline.steps if s.options.name == "WHAR Model"), None)
    if wharStep is not None:
        model_id = next(
            (p.value for p in wharStep.options.parameters if p.parameter_name == "model_id"),
            None,
        )
        if model_id == "deepsense" and n_channels % 2 != 0:
            errors.append(_msg(
                "classification",
                f"The 'deepsense' architecture needs an even number of channels (it pairs "
                f"acc/gyro), but the selected data has {n_channels}. Pick a different "
                f"architecture or adjust the selected sensors.",
            ))
        elif model_id == "global_fusion" and n_channels < 6:
            errors.append(_msg(
                "classification",
                f"The 'global_fusion' architecture needs at least 6 channels, but the "
                f"selected data has {n_channels}. Pick a different architecture or select "
                f"more sensors.",
            ))

    if errors:
        return {"valid": False, "errors": errors, "warnings": warnings}

    # --- run the deterministic prefix (load + windowing) on the real data ---
    labelMap = {str(x.id): i for i, x in enumerate(selectedLabels)}
    maxIdx = max(labelMap.values())
    if trainReq.labeling.useZeroClass:
        labelMap["Zero"] = maxIdx + 1

    if usesRecordings:
        return _preflight_recordings(trainReq, datasets, windowStep, labelMap, conversions, errors, warnings)

    try:
        datasets_processed, datasetMetaData, samplingRate = processDatasets(
            datasets, trainReq.labeling, labelMap, conversions
        )
    except Exception as e:
        return {"valid": False, "errors": [_msg("datasets", f"Could not load the selected data: {e}")], "warnings": warnings}

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
    _check_window_counts(labels_after, errors, warnings)
    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}


def _check_window_counts(labels_after, errors, warnings):
    """Errors and warnings about the windows that survive windowing."""
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
    else:
        # The evaluator does a stratified train/test split, which needs at
        # least 2 windows per class. Catch the under-populated class here
        # instead of letting training fail with a cryptic sklearn error.
        from collections import Counter

        counts = Counter(int(x) for x in labels_after)
        min_count = min(counts.values())
        if min_count < 2:
            errors.append(_msg(
                "windowing",
                f"At least one class has only {min_count} window after windowing; the "
                "train/test split needs at least 2 per class. Use a smaller window size / "
                "sliding step, or add more labeled data.",
            ))
        elif n_windows < 10:
            warnings.append(_msg(
                "windowing",
                f"Only {n_windows} training windows were produced — the model may train poorly. "
                "Consider a smaller window/step or more data.",
            ))


def _preflight_recordings(trainReq, datasets, windowStep, labelMap, conversions, errors, warnings):
    """The audio pipeline's checks. Only the recordings' metadata is read:
    nothing is decoded, so this stays fast."""
    from app.DataProcessor.DataLoader.recordings import RecordingsError, align_sources, build_sources
    from app.internal.config import AUDIO_MAX_TOTAL_SECONDS, MAX_TRAIN_WINDOWS

    for ds in datasets:
        if len(ds.mediaSeries) > 1:
            errors.append(_msg("datasets", f"Dataset '{ds.name}': select one recording; the model takes one sound input."))
        for m in ds.mediaSeries:
            if not m.has_sound:
                errors.append(_msg("datasets", f"The recording '{m.name}' in '{ds.name}' has no sound track."))
            elif m.status not in (None, "ready"):
                errors.append(_msg("datasets", f"The recording '{m.name}' in '{ds.name}' is still being processed. Try again in a moment."))
            rate = (m.meta or {}).get("sampleRate")
            if rate and int(rate) < 16000:
                warnings.append(_msg("datasets", f"'{m.name}' in '{ds.name}' was recorded at {int(rate)} Hz; "
                                                 "sounds above half that rate are missing from it."))
    names = {m.name for ds in datasets for m in ds.mediaSeries}
    if len(names) > 1:
        warnings.append(_msg("datasets", "The selected recordings have different names (" + ", ".join(sorted(names)) +
                             "). They are used as the same input; make sure they were recorded the same way."))
    if errors:
        return {"valid": False, "errors": errors, "warnings": warnings}

    try:
        sources = align_sources(build_sources(datasets, trainReq.labeling, labelMap, conversions))
    except RecordingsError as e:
        return {"valid": False, "errors": [_msg("datasets", str(e))], "warnings": warnings}

    windower = getPipelineOption(windowStep.options.name)(windowStep.options.parameters)
    try:
        plans = windower.plan(sources)
    except Exception as e:
        return {"valid": False, "errors": [_msg("windowing", str(e))], "warnings": warnings}

    seconds = windower.audio_seconds(sources) if windower.audio_rate else 0
    if seconds > AUDIO_MAX_TOTAL_SECONDS:
        errors.append(_msg("datasets", f"The selected recordings are {seconds / 3600:.1f} h long; this server trains on at "
                                       f"most {AUDIO_MAX_TOTAL_SECONDS / 3600:.1f} h of audio. Select fewer datasets."))
    total = sum(len(starts) for starts, _ in plans)
    if total > MAX_TRAIN_WINDOWS:
        errors.append(_msg("windowing", f"The settings give {total} windows; this server trains on at most "
                                        f"{MAX_TRAIN_WINDOWS}. Use a larger window step or fewer datasets."))
    for source, ds, (starts, _) in zip(sources, datasets, plans):
        if source.span() is None:
            warnings.append(_msg("datasets", f"In '{ds.name}' the selected sensors and recording do not overlap in time; "
                                             "it gives no windows."))
        elif len(starts) == 0 and len(source.labels.starts):
            warnings.append(_msg("windowing", f"No labeled window fits into '{ds.name}'. Check that its labels lie "
                                              "where the recording and sensors are."))

    labels_after = [int(x) for _, labels in plans for x in labels]
    _check_window_counts(labels_after, errors, warnings)
    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}
