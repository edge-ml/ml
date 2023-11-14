from app.Deploy.Devices.Nicla.Sensors.SensorComponent import SensorComponent

class Humidity():

    def get_name(self):
        return "Humidity"

    def get_components(self):
        return [
            SensorComponent("value", "float"),
        ]
    
    def get_config(self):
        return {"name": self.get_name(), "components": [x.get_config() for x in self.get_components()]}

    def get_setup_code(self, samplingRate):
        return f"humidity.begin({samplingRate});"
    
    def get_before_setup_code(self):
        return "Sensor humidity(SENSOR_ID_HUM);"

    def get_obtain_value_code(self, component):
        return f"{self.get_components()[component].dtype} hum_{self.get_components()[component].name} = humidity.{self.get_components()[component].name}();"