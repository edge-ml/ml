from app.Deploy.Devices.BaseDevice import BaseDevice
from app.Deploy.Devices.Nano33Rev1.Sensors.IMU_ACC import IMU
from typing import List
from jinja2 import Template


class Nano33Rev1(BaseDevice):

    def __init__(self) -> None:

        sensors = [IMU()]

        super().__init__(sensors)

    @staticmethod
    def get_name():
        return "Arduino Nano33 Rev1"
    
    def getSensorParams(self,tsMap, parameters):


        before_setup = set()
        setup = set()
        before_obtain_values = set()
        obtain_values = []
        incldues = set()

        print("-" * 40)
        print(tsMap)
        print("-" * 40)

        for sensorConf in tsMap:
            sensor = self.sensors[sensorConf.sensor_id]
            before_setup.add("\n".join(sensor.get_before_setup_code()))
            setup.add("\n".join(sensor.get_setup_code(40)))
            incldues.add("\n".join(sensor.get_include_code()))
            for val in sensor.get_before_obtain_values():
                before_obtain_values.add(val)
            print(sensorConf.component_id)
            obtain_values.append(sensor.get_obtain_value_code(sensorConf.component_id))

        return list(before_setup), list(setup), list(before_obtain_values), list(incldues), obtain_values
    
    def deploy(self, tsMap, parameters, additionalSettings, model):
        classification_frequency = [x for x in parameters if x.name == "classificationFrequency"][0].value
        before_setup, setup, before_obtain_values, includes, obtain_values = self.getSensorParams(tsMap, parameters)

        data = {"before_setup": before_setup,
                "setup": setup,
                "before_obtain_values": before_obtain_values,
                "obtain_values": obtain_values,
                "includes": includes,
                "classification_frequency": classification_frequency,
                "additionalSettings": additionalSettings}
        data["add_datapoint_vars"] = ",".join([x.split(" = ")[0].split(" ")[1] for x in obtain_values])
        data["sampling_rate"] = model.samplingRate

        with open("app/Deploy/Devices/OpenEarable/Base.cpp", "r") as f:
            base = f.read()
            print(base)

        template = Template(base)
        res = template.render(data)
        print("*" * 50)
        print(res)
        print("*" * 50)
        return res