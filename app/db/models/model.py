from dataclasses import dataclass
import string
from app.models.edge_model import EdgeModel
import pickle

@dataclass
class Model():
    name: string
    project_id: string
    edge_model: EdgeModel

    @staticmethod
    def marshal(that):
        return {
            'name': that.name,
            'project_id': that.project_id,
            'edge_model': pickle.dumps(that.edge_model)
        }

    @staticmethod
    def unmarshal(data):
        return Model(
            name=data['name'],
            project_id=data['project_id'],
            edge_model=pickle.loads(data['edge_model'])
        )
