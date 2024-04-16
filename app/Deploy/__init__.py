from app.Deploy.Devices.BaseDevice import BaseDevice
from app.Deploy.Devices.Nicla.Nicla import Nicla
from app.Deploy.Devices.Nano33Rev1 import Nano33Rev1

from typing import List

DEPLOY_DEVICES : List[BaseDevice] = [Nicla()]