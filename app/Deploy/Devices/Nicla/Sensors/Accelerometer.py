from Deploy.Devices.Nicla.Sensors.SensorComponent import SensorComponent

class Accelerometer():

    def get_name(self):
        return "Accelerometer"

    def get_components(self):
        return [
            SensorComponent("x", "short"),
            SensorComponent("y", "short"),
            SensorComponent("z", "short")
        ]
    
    def get_config(self):
        return {"name": self.get_name(), "components": [x.get_config() for x in self.get_components()]}

    def get_setup_code(self, samplingRate):
        return f"accelerometer.begin({samplingRate});"
    
    def get_before_setup_code(self):
        return "SensorXYZ accelerometer(SENSOR_ID_ACC);"

    def get_obtain_value_code(self, component):
        return f"{self.get_components()[component].dtype} acc_{self.get_components()[component].name} = accelerometer.{self.get_components()[component].name}();"