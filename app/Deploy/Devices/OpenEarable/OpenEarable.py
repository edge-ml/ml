from app.Deploy.Devices.BaseDevice import BaseDevice
from app.Deploy.Devices.OpenEarable.Sensors.Accelerometer import Accelerometer
from typing import List
from jinja2 import Template


class OpenEarable(BaseDevice):

    def __init__(self) -> None:

        sensors = [Accelerometer()]

        super().__init__(sensors)

    @staticmethod
    def get_name():
        return "Open Earable v3"
    
    def getSensorParams(self,tsMap, parameters):


        before_setup = set()
        setup = set()
        before_obtain_values = set()
        obtain_values = []

        print("-" * 40)
        print(tsMap)
        print("-" * 40)

        for sensorConf in tsMap:
            sensor = self.sensors[sensorConf.sensor_id]
            before_setup.add("\n".join(sensor.get_before_setup_code()))
            setup.add("\n".join(sensor.get_setup_code(40)))
            before_obtain_values.add(sensor.get_before_obtain_values())
            print(sensorConf.component_id)
            obtain_values.append(sensor.get_obtain_value_code(sensorConf.component_id))

        return list(before_setup), list(setup), list(before_obtain_values), obtain_values
    
    def deploy(self, tsMap, parameters, additionalSettings, model):
        classification_frequency = [x for x in parameters if x.name == "classificationFrequency"][0].value
        before_setup, setup, before_obtain_values, obtain_values = self.getSensorParams(tsMap, parameters)

        data = {"before_setup": before_setup,
                "setup": setup,
                "before_obtain_values": before_obtain_values,
                "obtain_values": obtain_values,
                "classification_frequency": classification_frequency,
                "additionalSettings": additionalSettings}
        data["add_datapoint_vars"] = ",".join([x.split(" = ")[0].split(" ")[1] for x in obtain_values])
        data["sampling_rate"] = model.samplingRate

        with open("app/Deploy/Devices/OpenEarable/Base.cpp", "r") as f:
            base = f.read()
            print(base)

        template = Template(base)
        res = template.render(data)
        return res