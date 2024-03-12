from typing import List
from Deploy.Devices.Nicla.Sensors.SensorComponent import SensorComponent
from Deploy.Devices.BaseSensor import BaseSensor

class Baro(BaseSensor):

    def get_name(self):
        return "Baro"

    def get_components(self):
        return [
            SensorComponent("pressure", "int"),
            SensorComponent("temperature", "float")
        ]
    
    def get_include_code(self) -> List[str]:
        return ["#include <Adafruit_BMP280.h>"]

    def get_config(self):
        return {"name": self.get_name(), "components": [x.get_config() for x in self.get_components()]}

    def get_setup_code(self, samplingRate):
        return [
            "Wire1.begin();",
            "Baro = new Adafruit_BMP280(&Wire1);",
            "Baro->begin(BMP280_ADDRESS_ALT, BMP280_CHIPID);",
            "Baro->setSampling(Adafruit_BMP280::MODE_NORMAL, Adafruit_BMP280::SAMPLING_X2, Adafruit_BMP280::SAMPLING_X1, Adafruit_BMP280::FILTER_OFF, Adafruit_BMP280::STANDBY_MS_1);"] 
    
    def get_before_setup_code(self):
        return ["Adafruit_BMP280 *Baro;"]

    def get_before_obtain_values(self):
        return "    IMU->getAllData(&magn, &gyro, &accel);"

    def get_obtain_value_code(self, component: SensorComponent):
        if component == 0:
            return f"{self.get_components()[component].dtype} {self.get_components()[component].name} = Baro->readPressure();"
        if component == 1:
            return f"{self.get_components()[component].dtype} {self.get_components()[component].name} = Baro->readTemperature();"