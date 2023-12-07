from app.Deploy.Devices.Nicla.Sensors.SensorComponent import SensorComponent

class Barometer():

    def get_name(self):
        return "Barometer"

    def get_components(self):
        return [
            SensorComponent("value", "float"),
        ]
    
    def get_config(self):
        return {"name": self.get_name(), "components": [x.get_config() for x in self.get_components()]}

    def get_setup_code(self, samplingRate):
        return f"barometer.begin({samplingRate});"
    
    def get_before_setup_code(self):
        return "Sensor barometer(SENSOR_ID_BARO);"

    def get_obtain_value_code(self, component):
        return f"{self.get_components()[component].dtype} baro_{self.get_components()[component].name} = barometer.{self.get_components()[component].name}();"