from Deploy.Devices.Nicla.Sensors.SensorComponent import SensorComponent

class Gyroscope():

    def get_name(self):
        return "Gyroscope"

    def get_components(self):
        return [
            SensorComponent("x", "short"),
            SensorComponent("y", "short"),
            SensorComponent("z", "short")
        ]
    
    def get_config(self):
        return {"name": self.get_name(), "components": [x.get_config() for x in self.get_components()]}

    def get_setup_code(self, samplingRate):
        return f"gyroscope.begin({samplingRate});"
    
    def get_before_setup_code(self):
        return "SensorXYZ gyroscope(SENSOR_ID_GYRO);"

    def get_obtain_value_code(self, component):
        return f"{self.get_components()[component].dtype} gyro_{self.get_components()[component].name} = gyroscope.{self.get_components()[component].name}();"