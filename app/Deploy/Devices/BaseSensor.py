from app.Deploy.Devices.Nicla.Sensors.SensorComponent import SensorComponent

from typing import List, Dict

class BaseSensor:

    def get_name(self) -> str:
        raise NotImplementedError("Each sensor needs a name")

    def get_components(self) -> List[SensorComponent]:
        raise NotImplementedError("Every Sensor needs components")
    
    def get_include_code(self) -> List[str]:
        return []

    def get_config(self) -> Dict:
        return {"name": self.get_name(), "components": [x.get_config() for x in self.get_components()]}

    def get_setup_code(self, samplingRate) -> List[str]:
        return []
    
    def get_before_setup_code(self) -> List[str]:
        return []

    def get_before_obtain_values(self) -> List[str]:
        return ""

    def get_obtain_value_code(self, component: int) -> str:
        raise NotImplementedError()