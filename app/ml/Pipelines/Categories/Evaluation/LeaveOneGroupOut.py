from typing import Any, Dict, List

import numpy as np

from app.ml.Pipeline import Pipeline
from app.ml.Pipelines.Abstract.StepType import StepType
from app.ml.Pipelines.Categories.Evaluation.BaseEvaluation import BaseEvaluation
from app.ml.Pipelines.Categories.Evaluation.utils import calculateMetrics
from app.ml.Pipelines.PipelineContainer import PipelineContainer
from app.utils.parameter_builder import ParameterBuilder


def _group_value(meta, field):
    """The grouping value a window contributes, or None when its dataset does not
    carry the field. Windows are only groupable if the windower preserved the
    per-dataset metadata dict."""
    if not isinstance(meta, dict):
        return None
    value = meta.get(field)
    if value is None:
        return None
    value = str(value).strip()
    return value or None


class LeaveOneGroupOut(BaseEvaluation):
    """Leave-one-out cross validation over a dataset metadata field.

    Each distinct value of the field is held out in turn while the model trains on
    every other value, so the reported performance is always measured on a
    value the model never saw (typically a subject). Datasets that do not carry
    the field cannot be placed in any group and are excluded from the run; the
    counts are reported back so the UI can say so.
    """

    # Options are always constructed with a single positional argument, both by
    # getEvaluator and by Pipeline.clone (`x.__class__(x.parameters)`), so the
    # signature has to stay exactly this.
    def __init__(self, parameters=...):
        super().__init__(parameters)
        self.metrics = None

    @staticmethod
    def get_name():
        return "LeaveOneGroupOut"

    @staticmethod
    def get_description():
        return (
            "Leave-one-out cross validation over a dataset metadata field. Each value of "
            "the field is held out in turn. Datasets without the field are excluded."
        )

    @staticmethod
    def get_parameters():
        pb = ParameterBuilder()
        pb.parameters = []
        # A selection with no options: the available keys are project specific, so
        # the frontend fills them in from the selected datasets' metadata keys and
        # sends the chosen one back. Selection values are not checked against the
        # options server side, so an empty list here is fine.
        pb.add_selection(
            "group_field",
            "Leave-one-out field",
            "Dataset metadata field to split on, e.g. subject. Datasets without it are excluded.",
            [],
            "",
            multi_select=False,
            required=True,
            is_advanced=False,
        )
        return pb.parameters

    def eval(self, pipeline: Pipeline, datasets, labelNames):
        field = str(self.get_param_value_by_name("group_field") or "").strip()
        if not field:
            raise ValueError(
                "Leave-one-out cross validation needs a metadata field to split on."
            )

        # Dataset level first, so the excluded count is reported in datasets (what
        # the user picked) rather than in windows.
        dataset_metas = list(getattr(datasets, "meta", None) or [])
        datasets_total = len(dataset_metas)
        datasets_excluded = sorted(
            {
                str(index)
                for index, meta in enumerate(dataset_metas)
                if _group_value(meta, field) is None
            }
        )

        data: PipelineContainer = pipeline.exec(datasets, StepType.PRE)

        metas = list(data.meta or [])
        if len(metas) != len(data.data):
            raise ValueError(
                "The selected windowing step does not preserve dataset metadata, so "
                "leave-one-out cross validation cannot group the windows. Use the "
                "sample windower."
            )

        groups: List[str] = []
        keep: List[int] = []
        for index, meta in enumerate(metas):
            value = _group_value(meta, field)
            if value is None:
                continue
            keep.append(index)
            groups.append(value)

        distinct = sorted(set(groups))
        if len(distinct) < 2:
            raise ValueError(
                f"Leave-one-out cross validation needs at least 2 distinct values of "
                f"'{field}' across the selected datasets, found {len(distinct)}. "
                f"{len(datasets_excluded)} of {datasets_total} datasets do not carry "
                f"'{field}' and were excluded."
            )

        X = data.data[keep]
        Y = data.labels[keep]
        kept_metas = [metas[index] for index in keep]
        group_array = np.array(groups)

        folds: List[Dict[str, Any]] = []
        pooled_true: List[Any] = []
        pooled_pred: List[Any] = []

        for held_out in distinct:
            test_mask = group_array == held_out
            train_mask = ~test_mask

            if not train_mask.any() or not test_mask.any():
                continue

            train_labels = Y[train_mask]
            if len(np.unique(train_labels)) < 2:
                # Nothing can be learned from a single class; skip the fold rather
                # than failing the whole run, and say so in the result.
                folds.append(
                    {
                        "group": held_out,
                        "windows": int(test_mask.sum()),
                        "skipped": "only one class present in the training folds",
                    }
                )
                continue

            # A fresh pipeline per fold, so no fitted state leaks between folds.
            fold_pipeline = pipeline.clone()
            fold_pipeline.fit_exec(
                PipelineContainer(
                    X[train_mask],
                    train_labels,
                    [m for m, keep_it in zip(kept_metas, train_mask) if keep_it],
                ),
                StepType.CORE,
            )
            predicted: PipelineContainer = fold_pipeline.exec(
                PipelineContainer(
                    X[test_mask],
                    Y[test_mask],
                    [m for m, keep_it in zip(kept_metas, test_mask) if keep_it],
                ),
                StepType.CORE,
            )

            fold_true = Y[test_mask]
            fold_pred = predicted.data
            pooled_true.extend(np.asarray(fold_true).tolist())
            pooled_pred.extend(np.asarray(fold_pred).tolist())

            fold_metrics = calculateMetrics(fold_true, fold_pred, labelNames)
            folds.append(
                {
                    "group": held_out,
                    "windows": int(test_mask.sum()),
                    "metrics": fold_metrics["metrics"],
                }
            )

        if not pooled_true:
            raise ValueError(
                f"No fold of '{field}' could be evaluated; every fold had fewer than "
                "2 classes in its training data."
            )

        # Every kept window is predicted exactly once, when its own group is held
        # out, so the pooled predictions give one honest confusion matrix over all
        # of the data. Averaging per-fold matrices would not.
        self.metrics = calculateMetrics(
            np.array(pooled_true), np.array(pooled_pred), labelNames
        )
        self.metrics["cross_validation"] = {
            "method": self.get_name(),
            "field": field,
            "groups": distinct,
            "folds": folds,
            "datasets_total": datasets_total,
            "datasets_excluded": len(datasets_excluded),
            "windows_total": len(metas),
            "windows_excluded": len(metas) - len(keep),
        }

        # Cross validation only measures; the model that gets persisted has to be
        # trained on everything that took part, so fit the real pipeline last.
        pipeline.fit_exec(PipelineContainer(X, Y, kept_metas), StepType.CORE)

        return self.metrics

    def persist(self):
        return {
            "name": self.get_name(),
            "description": self.get_description(),
            "parameters": self.parameters,
            "metrics": self.metrics,
        }
