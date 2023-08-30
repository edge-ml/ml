from app.Deploy.Sensors.SensorComponent import SensorComponent

class Temperature():

    def get_name(self):
        return "Temperature"

    def get_components(self):
        return [
            SensorComponent("value", "float"),
        ]
    
    def get_config(self):
        return {"name": self.get_name(), "components": [x.get_config() for x in self.get_components()]}

    def get_setup_code(self, samplingRate):
        return f"temperature.begin({samplingRate});"
    
    def get_before_setup_code(self):
        return "Sensor temperature(SENSOR_ID_TEMP);"

    def get_obtain_value_code(self, component):
        return f"{self.get_components()[component].dtype} temp_{self.get_components()[component].name} = temperature.{self.get_components()[component].name}();"