from app.ml.Pipelines.Abstract.AbstractPipelineCategory import PipelineCategory
from app.ml.AutoML.AutoMLClassifier import AutoMLClassifier



AUTOMLCLASSIFIER_CATEGORY = PipelineCategory("Classifier", "Classification for time-series data", [AutoMLClassifier.get_train_config()])