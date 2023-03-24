from app.ml.Windowing.BaseWindower import BaseWindower 
from app.ml.Windowing.SampleWindower import SampleWindower
from app.ml.Windowing.TimeWindower import TimeWindower
from typing import List



WINDOWER : List[BaseWindower] = [SampleWindower, TimeWindower]

def get_windower_by_name(name) -> BaseWindower:
    for cls in WINDOWER:
        if cls.get_name() == name:
            return cls
    raise Exception()

WIDNOWING_CONFIG = [x.get_train_config() for x in WINDOWER]