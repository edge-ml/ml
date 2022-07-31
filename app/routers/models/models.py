import time
from typing import List, Optional
from uuid import uuid4
from fastapi import APIRouter, Depends
from app.codegen.inference.InferenceFormats import InferenceFormats
from app.db.models import get_project_models
from app.routers.dependencies import extract_project_id, validate_model, validate_user
from pydantic import BaseModel

from app.models.edge_model import EdgeModel
from app.models.kneighbours import KNeighbours
from app.models.mlp import MLP
from app.models.random_forest import RandomForest
from app.models.svc import SVC
from app.models.decision_tree import DecisionTree
from app.models.random_forest import RandomForest
from app.db.models import delete_model as db_delete_model

router = APIRouter()

edge_models = [
    # {
    #     "name": EdgeModel.get_name(),
    #     "description": EdgeModel.get_description(),
    #     "id": 0,
    #     "hyperparameters": EdgeModel.get_hyperparameters(),
    #     "model": EdgeModel(),
    # },
    {
        "name": RandomForest.get_name(),
        "description": RandomForest.get_description(),
        "id": 0,
        "hyperparameters": RandomForest.get_hyperparameters(),
        "model": RandomForest(),
        "platforms": RandomForest.get_platforms()
    },
    {
        "name": KNeighbours.get_name(),
        "description": KNeighbours.get_description(),
        "id": 1,
        "hyperparameters": KNeighbours.get_hyperparameters(),
        "model": KNeighbours(),
        "platforms": KNeighbours.get_platforms()
    },
    {
        "name": DecisionTree.get_name(),
        "description": DecisionTree.get_description(),
        "id": 2,
        "hyperparameters": DecisionTree.get_hyperparameters(),
        "model": DecisionTree(),
        "platforms": DecisionTree.get_platforms()
    },
    {
        "name": SVC.get_name(),
        "description": SVC.get_description(),
        "id": 3,
        "hyperparameters": SVC.get_hyperparameters(),
        "model": SVC(),
        "platforms": SVC.get_platforms()
    },
    # {
    #     "name": MLP.get_name(),
    #     "description": MLP.get_description(),
    #     "id": 4,
    #     "hyperparameters": MLP.get_hyperparameters(),
    #     "model": MLP(),
    # },
]

# Get list of models that can be trained
@router.get("/")
async def models():
    # print(type(EdgeModel).__name__)
    global edge_models

    return edge_models

class TrainedModel(BaseModel):
    id: str
    name: str
    creation_date: float
    classifier: str
    accuracy: float
    precision: float
    f1_score: float
    size: int

class ModelMetrics(TrainedModel):
    hyperparameters: dict
    window_size: int
    sliding_step: int
    windowing_mode: str
    labels: List[str]
    confusion_matrix: str
    classification_report: str
    platforms: List[InferenceFormats]

# Get a trained model
@router.get("/trained/{model_id}", response_model=ModelMetrics)
async def trained_model(model=Depends(validate_model)):
    return {
        'id':model.id, 
        'name':model.name, 
        'creation_date':model.creation_date,
        'classifier':model.edge_model.get_name(),
        'accuracy': model.accuracy_score,
        'precision': model.precision_score,
        'f1_score': model.f1_score,
        'size': model.size,
        'labels': model.labels if model.labels else [],
        'confusion_matrix': model.confusion_matrix,
        'classification_report': model.classification_report,
        'hyperparameters': model.edge_model.hyperparameters,
        'window_size': model.window_size,
        'sliding_step': model.sliding_step if model.sliding_step else -1,
        'windowing_mode': model.windowing_mode,
        'platforms': model.edge_model.get_platforms(),
    }

# Delete a trained model
@router.delete("/trained/{model_id}")
async def delete_model(user=Depends(validate_user), model=Depends(validate_model)):
    await db_delete_model(model.id)
    return True

# Get a list of trained models
@router.get("/trained", response_model=List[TrainedModel])
async def trained_models(project_id=Depends(extract_project_id), user=Depends(validate_user)):
    models = await get_project_models(project_id)
    if not models:
        return [] 
    return [
        {
            'id':model.id, 
            'name':model.name, 
            'creation_date':model.creation_date, 
            'classifier':model.edge_model.get_name(),
            'accuracy': model.accuracy_score,
            'precision': model.precision_score,
            'f1_score': model.f1_score,
            'size': model.size,
        } for model in models
    ]