from dataclasses import dataclass
import string
from app.models.edge_model import EdgeModel
import pickle

@dataclass
class Model():
    name: string
    edge_model: EdgeModel

    @staticmethod
    def marshal(that):
        return {
            'name': that.name,
            'edge_model': pickle.dumps(that.edge_model)
        }

    @staticmethod
    def unmarshal(data):
        return Model(
            name=data.name,
            edge_model=pickle.loads(data.edge_model)
        )
