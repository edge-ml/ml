from Deploy.Devices.BaseDevice import BaseDevice
from Deploy.Devices.Nicla.Nicla import Nicla

from typing import List

DEPLOY_DEVICES : List[BaseDevice] = [Nicla()]