from typing import List
from fastapi import APIRouter, Depends
from app.db.models import get_project_models
from app.routers.dependencies import extract_project_id, validate_model, validate_user
from pydantic import BaseModel

from app.models.edge_model import EdgeModel
from app.models.kneighbours import KNeighbours
from app.models.mlp import MLP
from app.models.random_forest import RandomForest

router = APIRouter()

edge_models = [
    {
        "name": EdgeModel.get_name(),
        "description": EdgeModel.get_description(),
        "id": 0,
        "hyperparameters": EdgeModel.get_hyperparameters(),
        "model": EdgeModel(),
    },
    {
        "name": RandomForest.get_name(),
        "description": RandomForest.get_description(),
        "id": 1,
        "hyperparameters": RandomForest.get_hyperparameters(),
        "model": RandomForest(),
    },
    {
        "name": KNeighbours.get_name(),
        "description": KNeighbours.get_description(),
        "id": 2,
        "hyperparameters": KNeighbours.get_hyperparameters(),
        "model": KNeighbours(),
    },
    # {
    #     "name": MLP.get_name(),
    #     "description": MLP.get_description(),
    #     "id": 3,
    #     "hyperparameters": MLP.get_hyperparameters(),
    #     "model": MLP(),
    # },
]

# Get list of models that can be trained
@router.get("/")
async def models():
    print(type(EdgeModel).__name__)
    global edge_models

    return edge_models


# Get a list of platforms the model is available to.
@router.get("/platforms")
async def models_platforms():
    return "Platforms the model is available to"

# Export a model
@router.get("/trained/{model_id}/export")
async def trained_model_export(platform: str, validation=Depends(validate_model)):
    return f"Model export to {platform}..."


# Get a trained model
@router.get("/trained/{model_id}")
async def trained_model(model=Depends(validate_model)):
    return model.name

class TrainedModel(BaseModel):
    id: str
    name: str
    creation_date: float
    classifier: str
    accuracy: float
    precision: float
    f1_score: float

# Get a list of trained models
@router.get("/trained", response_model=List[TrainedModel])
async def trained_models(project_id=Depends(extract_project_id), user=Depends(validate_user)):
    models = await get_project_models(project_id)
    if not models:
        return [] 
    classifier = type(models[0].edge_model).__name__.split('.')[-1]
    return [
        {
            'id':model.id, 
            'name':model.name, 
            'creation_date':model.creation_date, 
            'classifier':classifier, 
            'accuracy': model.accuracy_score,
            'precision': model.precision_score,
            'f1_score': model.f1_score
        } for model in models
    ]
