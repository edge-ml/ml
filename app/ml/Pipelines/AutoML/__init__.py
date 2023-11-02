from app.ml.Pipelines.Abstract.AbstractPipelineCategory import PipelineCategory, PipelineCategoryType
from app.ml.Pipelines.AutoML.AutoMLClassifier import AutoMLClassifier



AUTOMLCLASSIFIER_CATEGORY = PipelineCategory("AutoMLClassifier", "Classification for time-series data", [AutoMLClassifier.get_train_config()])