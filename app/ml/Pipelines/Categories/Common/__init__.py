from app.ml.Pipelines.Abstract.AbstractPipelineStep import AbstractPipelineStep, StepType
from app.ml.Pipelines.Categories.Common.ModelMetadata import ModelMetadata


COMMON_CATEGORY = AbstractPipelineStep("Name", "Each model needs a name", [ModelMetadata], type=StepType.INFO)