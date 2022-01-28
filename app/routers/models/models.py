from fastapi import APIRouter, Depends
from app.routers.dependencies import validate_model

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
@router.get("/{model_id}/export")
async def models_export(platform: str, validation=Depends(validate_model)):
    return f"Model export to {platform}..."


# Get the perfomance metrics of a trained model
@router.get("/{model_id}/metrics")
async def models_metrics(validation=Depends(validate_model)):
    return "Performance metrics"
