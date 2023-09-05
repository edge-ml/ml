from app.Deploy.Sensors.SensorComponent import SensorComponent
from app.Deploy.Sensors.BaseSensor import BaseSensor

class Accelerometer(BaseSensor):

    def get_name(self):
        return "Accelerometer"

    def get_components(self):
        return [
            SensorComponent("x", "int"),
            SensorComponent("y", "int"),
            SensorComponent("z", "int")
        ]
    
    def get_config(self):
        return {"name": self.get_name(), "components": [x.get_config() for x in self.get_components()]}

    def get_setup_code(self, samplingRate):
        return ["Wire1.begin();" , "IMU = new DFRobot_BMX160(&Wire1);", "IMU->begin();"] 
    
    def get_before_setup_code(self):
        return ["DFRobot_BMX160 * IMU;",  "sBmx160SensorData_t magn;", "sBmx160SensorData_t gyro;", "sBmx160SensorData_t accel;"]

    def get_before_obtain_values(self):
        return "    IMU->getAllData(&magn, &gyro, &accel);"

    def get_obtain_value_code(self, component):
        return f"{self.get_components()[component].dtype} acc_{self.get_components()[component].name} = accel.{self.get_components()[component].name};"