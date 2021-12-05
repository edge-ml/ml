from fastapi import APIRouter

from models.edge_model import EdgeModel
from models.random_forest import RandomForest

import json

router = APIRouter()

edge_models = [
    {
        'name': EdgeModel.get_name(),
        'description': EdgeModel.get_description(),
        'id': 1,
        'hyperparameters': EdgeModel.get_hyperparameters()
    },
    {
        'name': RandomForest.get_name(),
        'description': RandomForest.get_description(),
        'id': 2,
        'hyperparameters': RandomForest.get_hyperparameters()
    }
]

# Get list of models that can be trained
@router.get("/models/")
async def models():
    print(type(EdgeModel).__name__)
    global edge_models

    return edge_models

# Train a model based on the edge_model matching the model_id and given set of hyperparameters
@router.post("/models/{model_id}")
async def models_train():
    return "id of the model to train" #TODO return the trained model

# Return a list of models that were trained before by the user
@router.get("/models/userCreated") # userTrained / trained / created 
async def models_userCreated():
    return "List of models"

# Get the perfomance metrics of a trained model
@router.get("/models/{model_id}/metrics")
async def models_metrics():
    return "Performance metrics"

# Get a list of platforms the model is available to.
@router.get("/models/{model_id}/platforms")
async def models_platforms():
    return "Platforms the model is available to"

# Export a model
@router.get("/models/{model_id}/export")
async def models_export():
    return "Model export..."

