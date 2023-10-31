from app.ml.Pipelines.Abstract.AbstractPipelineCategory import PipelineCategory
from app.ml.Pipelines.Categories.Common.NameCategory import NameCategory


COMMON_NAME_CATEGORY = PipelineCategory("Name", "Each model needs a name", [NameCategory.get_train_config()])