from app.ml.Pipelines.Abstract.AbstractPipelineStep import PipelineCategory, StepType
from app.ml.Pipelines.AutoML.AutoMLClassifier import AutoMLClassifier



AUTOMLCLASSIFIER_CATEGORY = PipelineCategory("AutoMLClassifier", "Classification for time-series data", [AutoMLClassifier.get_train_config()])