from Deploy.Devices.Nicla.Sensors.SensorComponent import SensorComponent
from Deploy.Devices.BaseSensor import BaseSensor

class IMU(BaseSensor):

    def get_name(self):
        return "IMU"

    def get_components(self):
        return [
            SensorComponent("ACC_x", "int"),
            SensorComponent("ACC_y", "int"),
            SensorComponent("ACC_z", "int"),
            
            SensorComponent("GYRO_x", "int"),
            SensorComponent("GYRO_y", "int"),
            SensorComponent("GYRO_z", "int"),
            
            SensorComponent("MAGN_x", "int"),
            SensorComponent("MAGN_y", "int"),
            SensorComponent("MAGN_z", "int")
        ]
    
    def get_include_code(self):
        return ["#include <DFRobot_BMX160.h>"]

    def get_config(self):
        return {"name": self.get_name(), "components": [x.get_config() for x in self.get_components()]}

    def get_setup_code(self, samplingRate):
        return ["Wire1.begin();" , "IMU = new DFRobot_BMX160(&Wire1);", "IMU->begin();"] 
    
    def get_before_setup_code(self):
        return ["DFRobot_BMX160 * IMU;",  "sBmx160SensorData_t MAGN;", "sBmx160SensorData_t GYRO;", "sBmx160SensorData_t ACC;"]

    def get_before_obtain_values(self):
        return "    IMU->getAllData(&MAGN, &GYRO, &ACC);"

    def get_obtain_value_code(self, component):
        comp = self.get_components()[component]
        direction = comp.name.split("_")[1]
        sign = "-" if comp.name.split('_')[1] == 'x' else ""
        return f"{comp.dtype} {comp.name} = {sign}{comp.name.split('_')[0]}.{direction};"

