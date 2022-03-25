import time
from typing import List, Optional
from uuid import uuid4
from fastapi import APIRouter, Depends
from app.db.models import get_project_models
from app.routers.dependencies import extract_project_id, validate_model, validate_user
from pydantic import BaseModel

from app.models.edge_model import EdgeModel
from app.models.kneighbours import KNeighbours
from app.models.mlp import MLP
from app.models.random_forest import RandomForest
from app.db.models import delete_model as db_delete_model
from app.db.deployments import add_deployment, get_model_deployments
from app.db.deployments.deployment import Deployment

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
        "platforms": RandomForest.get_platforms()
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
    # print(type(EdgeModel).__name__)
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
    labels: List[str]
    confusion_matrix: str
    classification_report: str

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

class NewDeploymentBody(BaseModel):
    name: str = "New deployment"

# Create a new deployment from trained model
@router.post("/trained/{model_id}/deploy")
async def trained_deploy(body: NewDeploymentBody, user=Depends(validate_user), model=Depends(validate_model)):
    key = await add_deployment(Deployment(
        name=body.name,
        model_id=model.id,
        project_id=model.project_id,
        creation_date=time.time(),
        key=str(uuid4())
    ))
    return key

# Get model deployments
@router.get("/trained/{model_id}/deployments")
async def trained_deploy(user=Depends(validate_user), model=Depends(validate_model)):
    deployments = await get_model_deployments(project_id=model.project_id, model_id=model.id)
    if not deployments:
        return []
    return [
        {
            'name': dep.name,
            'key': str(dep.key),
            'creation_date': dep.creation_date,
        } for dep in deployments
    ]