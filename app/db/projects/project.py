from dataclasses import dataclass
from typing import List

@dataclass
class Project():
    admin: str
    name: str
    users: List[str]
    datasets: List[str]
    experiments: List[str]
    labelDefinitions: List[str]
    labelTypes: List[str]
    devices: List[str]
    services: List[str]
    sensors: List[str]
    firmware: List[str]
    enableDeviceApi: bool

    @staticmethod
    def marshal(that):
        return {
            'admin': that.admin,
            'name': that.name,
            'users': that.users,
            'datasets': that.datasets,
            'experiments': that.experiments,
            'labelDefinitions': that.labelDefinitions,
            'labelTypes': that.labelTypes,
            'devices': that.devices,
            'services': that.services,
            'sensors': that.sensors,
            'firmware': that.firmware,
            'enableDeviceApi': that.enableDeviceApi,
        }

    @staticmethod
    def unmarshal(data):
        return Project(
            admin = data['admin'],
            name = data['name'],
            users = data['users'],
            datasets = data['datasets'],
            experiments = data['experiments'],
            labelDefinitions = data['labelDefinitions'],
            labelTypes = data['labelTypes'],
            devices = data['devices'],
            services = data['services'],
            sensors = data['sensors'],
            firmware = data['firmware'],
            enableDeviceApi = data['enableDeviceApi'],
        )