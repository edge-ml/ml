from app.Deploy.Devices.BaseDevice import BaseDevice
from app.Deploy.Devices.Nicla.Nicla import Nicla

from typing import List

DEPLOY_DEVICES : List[BaseDevice] = [Nicla()]