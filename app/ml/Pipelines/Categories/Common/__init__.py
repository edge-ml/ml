from app.ml.Pipelines.Abstract.AbstractPipelineStep import PipelineCategory, StepType
from app.ml.Pipelines.Categories.Common.ModelMetadata import ModelMetadata


COMMON_CATEGORY = PipelineCategory("Name", "Each model needs a name", [ModelMetadata.get_train_config()], type=StepType.INFO)