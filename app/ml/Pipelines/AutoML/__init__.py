from app.ml.Pipelines.Abstract.AbstractPipelineStep import AbstractPipelineStep, StepType
from app.ml.Pipelines.AutoML.AutoMLClassifier import AutoMLClassifier



AUTOMLCLASSIFIER_CATEGORY = AbstractPipelineStep("AutoMLClassifier", "Classification for time-series data", [AutoMLClassifier])