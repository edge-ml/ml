from typing import List
from enum import Enum

class QuantizationLevels(Enum):
    NO_QUANT = "No Quantization"
    DYN_RANGE = "Dynamic Range"
    INT8 = "Int8 Quantization"

class BaseDevice:

    def __init__(self, sensors: List) -> None:
        self.sensors = sensors

    def get_name(self):
        raise NotImplementedError()

    def get_sensor_config(self):
        return [x.get_config() for x in self.sensors]

    def get_config(self):
        return {"name": self.get_name(), "sensors": self.get_sensor_config()}