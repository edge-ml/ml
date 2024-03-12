from Deploy.Devices.Nicla.Sensors.SensorComponent import SensorComponent

class Gas():

    def get_name(self):
        return "Gas"

    def get_components(self):
        return [
            SensorComponent("value", "float"),
        ]
    
    def get_config(self):
        return {"name": self.get_name(), "components": [x.get_config() for x in self.get_components()]}

    def get_setup_code(self, samplingRate):
        return f"gas.begin({samplingRate});"
    
    def get_before_setup_code(self):
        return "Sensor gas(SENSOR_ID_GAS);"

    def get_obtain_value_code(self, component):
        return f"{self.get_components()[component].dtype} gas_{self.get_components()[component].name} = gas.{self.get_components()[component].name}();"