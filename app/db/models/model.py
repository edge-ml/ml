from dataclasses import dataclass
from app.models.edge_model import EdgeModel
import pickle

@dataclass
class Model():
    name: str
    id: str
    project_id: str
    creation_date: float
    accuracy_score: float
    precision_score: float
    recall_score: float
    f1_score: float
    confusion_matrix: str
    classification_report: str
    edge_model: EdgeModel

    @staticmethod
    def marshal(that):
        return {
            'name': that.name,
            'project_id': that.project_id,
            'creation_date': that.creation_date,
            'accuracy_score': that.accuracy_score,
            'precision_score': that.precision_score,
            'recall_score': that.recall_score,
            'f1_score': that.f1_score,
            'confusion_matrix': that.confusion_matrix,
            'classification_report': that.classification_report,
            'edge_model': pickle.dumps(that.edge_model)
        }

    @staticmethod
    def unmarshal(data):
        return Model(
            name=data['name'],
            id=str(data['_id']),
            project_id=data['project_id'],
            creation_date=data['creation_date'],
            accuracy_score=data['accuracy_score'],
            precision_score=data['precision_score'],
            recall_score=data['recall_score'],
            f1_score=data['f1_score'],
            confusion_matrix=data['confusion_matrix'],
            classification_report=data['classification_report'],
            edge_model=pickle.loads(data['edge_model'])
        )
