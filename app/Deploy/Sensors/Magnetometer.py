from app.Deploy.Sensors.SensorComponent import SensorComponent

class Magnetometer():

    def get_name(self):
        return "Magnetometer"

    def get_components(self):
        return [
            SensorComponent("x", "short"),
            SensorComponent("y", "short"),
            SensorComponent("z", "short")
        ]
    
    def get_config(self):
        return {"name": self.get_name(), "components": [x.get_config() for x in self.get_components()]}

    def get_setup_code(self, samplingRate):
        return f"magnetometer.begin({samplingRate});"
    
    def get_before_setup_code(self):
        return "SensorXYZ magnetometer(SENSOR_ID_MAG);"

    def get_obtain_value_code(self, component):
        return f"{self.get_components()[component].dtype} mag_{self.get_components()[component].name} = magnetometer.{self.get_components()[component].name}();"