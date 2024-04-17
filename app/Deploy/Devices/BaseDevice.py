from typing import List

class BaseDevice:

    def __init__(self, sensors: List) -> None:
        self.sensors = sensors

    def get_name(self):
        raise NotImplementedError()

    def get_sensor_config(self):
        return [x.get_config() for x in self.sensors]

    def get_ota_update(self):
        return False

    def get_config(self):
        return {"name": self.get_name(), "sensors": self.get_sensor_config(), "ota_update": self.get_ota_update(), "deploy_features": self.get_deploy_features()}