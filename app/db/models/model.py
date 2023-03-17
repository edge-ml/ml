from dataclasses import dataclass, field
from typing import List
from app.internal.consts import SAMPLE_BASED_WINDOWING
from app.models.edge_model import EdgeModel
import pickle
from pydantic import BaseModel, Field
from app.utils.PyObjectId import PyObjectId
from bson.objectid import ObjectId
from app.DataModels.model import Model
from app.db.models import _models


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
    labels: List[str]
    timeseries: List[str]
    window_size: int
    sliding_step: int
    windowing_mode: str
    confusion_matrix: str
    classification_report: str
    edge_model: EdgeModel
    scaler: dict
    cross_validation: dict

    size: int = field(default=None)
    pickled_edge_model: bytes = field(default=None)

    def __post_init__(self):
        self.pickled_edge_model = self.pickled_edge_model or pickle.dumps(self.edge_model)
        self.size = self.size or len(self.pickled_edge_model)

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
            'labels': that.labels,
            'timeseries': that.timeseries,
            'window_size': that.window_size,
            'sliding_step': that.sliding_step,
            'windowing_mode': that.windowing_mode,
            'confusion_matrix': that.confusion_matrix,
            'classification_report': that.classification_report,
            'edge_model': pickle.dumps(that.edge_model),
            'scaler': that.scaler,
            'cross_validation': that.cross_validation
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
            labels=data.get('labels'),
            timeseries=data.get('timeseries'),
            window_size=data.get('window_size'),
            sliding_step=data.get('sliding_step'),
            windowing_mode=data.get('windowing_mode') if data.get('windowing_mode') else SAMPLE_BASED_WINDOWING, # Backwards compability: sample based windowing was the first and only mode before this parameter
            confusion_matrix=data['confusion_matrix'],
            classification_report=data['classification_report'],
            edge_model=pickle.loads(data['edge_model']),

            size=len(data['edge_model']),
            pickled_edge_model=data['edge_model'],
            scaler=data['scaler'] if "scaler" in data else None,
            cross_validation=data['cross_validation'] if "cross_validation" in data else [],
        )
