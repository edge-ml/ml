from app.ml.Windowing.BaseWindower import BasicWindower 
from app.ml.Windowing.SampleWindower import SampleWindower
from app.ml.Windowing.TimeWindower import TimeWindower



WINDOWER = [SampleWindower, TimeWindower]

def get_windower_by_name(name) -> BasicWindower:
    for cls in WINDOWER:
        if cls.get_name() == name:
            return cls
    raise Exception()

WIDNOWING_CONFIG = [x.config() for x in WINDOWER]