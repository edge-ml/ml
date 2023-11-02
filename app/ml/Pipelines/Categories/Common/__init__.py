from app.ml.Pipelines.Abstract.AbstractPipelineCategory import PipelineCategory, PipelineCategoryType
from app.ml.Pipelines.Categories.Common.ModelMetadata import ModelMetadata


COMMON_CATEGORY = PipelineCategory("Name", "Each model needs a name", [ModelMetadata.get_train_config()], type=PipelineCategoryType.INFO)