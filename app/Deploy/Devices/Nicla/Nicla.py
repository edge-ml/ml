from app.Deploy.Devices.BaseDevice import BaseDevice
from app.Deploy.Sensors.Accelerometer import Accelerometer
from typing import List
from jinja2 import Template


class Nicla(BaseDevice):

    def __init__(self) -> None:

        sensors = [Accelerometer()]

        super().__init__(sensors)

    @staticmethod
    def get_name():
        return "Nicla Sense ME"
    
    def get_ota_update(self):
        return True
    
    def getSensorParams(self,tsMap, parameters):


        before_setup = set()
        setup = set()
        obtain_values = set()

        for sensorConf in tsMap:
            sensor = self.sensors[sensorConf.sensor_id]
            before_setup.add(sensor.get_before_setup_code())
            setup.add(sensor.get_setup_code(40))
            obtain_values.add(sensor.get_obtain_value_code(sensorConf.component_id))

        return list(before_setup), list(setup), list(obtain_values)
    
    def deploy(self, tsMap, parameters, additionalSettings, model):
        before_setup, setup, obtain_values = self.getSensorParams(tsMap, parameters)

        data = {"before_setup": before_setup, "setup": setup, "obtain_values": obtain_values}
        data["add_datapoint_vars"] = ",".join([x.split(" = ")[0].split(" ")[1] for x in obtain_values])
        data["sampling_rate"] = parameters[0].value

        with open("app/Deploy/Devices/Nicla/Base.cpp", "r") as f:
            base = f.read()
            print(base)

        template = Template(base)
        res = template.render(data)
        return res