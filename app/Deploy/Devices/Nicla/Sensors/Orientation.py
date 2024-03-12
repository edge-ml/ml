from Deploy.Devices.Nicla.Sensors.SensorComponent import SensorComponent

class Orientation():

    def get_name(self):
        return "Orientation"

    def get_components(self):
        return [
            SensorComponent("roll", "short"),
            SensorComponent("pitch", "short"),
            SensorComponent("heading", "short")
        ]
    
    def get_config(self):
        return {"name": self.get_name(), "components": [x.get_config() for x in self.get_components()]}

    def get_setup_code(self, samplingRate):
        return f"orientation.begin({samplingRate});"
    
    def get_before_setup_code(self):
        return "SensorOrientation orientation(SENSOR_ID_ORI);"

    def get_obtain_value_code(self, component):
        return f"{self.get_components()[component].dtype} ori_{self.get_components()[component].name} = orientation.{self.get_components()[component].name}();"