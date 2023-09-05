from app.Deploy.Devices.BaseDevice import BaseDevice
from app.Deploy.Devices.Nicla.Nicla import Nicla
from app.Deploy.Devices.OpenEarable.OpenEarable import OpenEarable
from typing import List

DEVICES : List[BaseDevice] = [Nicla(), OpenEarable()]

def get_device_by_name(name: str):
    for device in DEVICES:
        if device.get_name() == name:
            return device
    raise KeyError()