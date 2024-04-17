from app.Deploy.Devices.Nicla.Sensors.SensorComponent import SensorComponent
from app.Deploy.Devices.BaseSensor import BaseSensor

class IMU_MAGN(BaseSensor):

    def get_name(self):
        return "IMU"

    def get_components(self):
        return [           
            SensorComponent("MAGN_x", "float"),
            SensorComponent("MAGN_y", "float"),
            SensorComponent("MAGN_z", "float")
        ]
    
    def get_include_code(self):
        return ["#include <Arduino_LSM9DS1.h>"]

    def get_config(self):
        return {"name": self.get_name(), "components": [x.get_config() for x in self.get_components()]}

    def get_setup_code(self, samplingRate):
        return ["IMU.begin();"] 
    
    def get_before_setup_code(self):
        return ["float x, y ,z;"]

    def get_before_obtain_values(self):
        return [f"IMU.readMagneticField(x, y, z);"]

    def get_obtain_value_code(self, component):
        component = self.get_components()[component]
        return f"float {component.name} = x;"

