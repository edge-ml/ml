from app.ml.Pipelines.Categories.Windowing.BaseWindower import BaseWindower 
from app.ml.Pipelines.Categories.Windowing.SampleWindower import SampleWindower
from app.ml.Pipelines.Categories.Windowing.TimeWindower import TimeWindower
from app.ml.Pipelines.Abstract.AbstractPipelineStep import PipelineCategory, StepType
from typing import List



WINDOWER : List[BaseWindower] = [SampleWindower, TimeWindower]

def get_windower_by_name(name) -> BaseWindower:
    for cls in WINDOWER:
        if cls.get_name() == name:
            return cls
    raise Exception()

WIDNOWING_CONFIG = [x.get_train_config() for x in WINDOWER]

WINDOWING_CATEGORY = PipelineCategory("Windowing", "Defines how the training dataset is split into smaller segments", WIDNOWING_CONFIG, type=StepType.PRE)