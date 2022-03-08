from dataclasses import dataclass
from uuid import UUID

@dataclass
class Deployment():
    name: str
    key: str
    project_id: str
    model_id: str
    creation_date: float

    @staticmethod
    def marshal(that):
        return {
            'name': that.name,
            '_id': UUID(that.key),
            'project_id': that.project_id,
            'model_id': that.model_id,
            'creation_date': that.creation_date,
        }

    @staticmethod
    def unmarshal(data):
        return Deployment(
            name=data['name'],
            key=str(data['_id']),
            project_id=data['project_id'],
            model_id=data['model_id'],
            creation_date=data['creation_date'],
        )
