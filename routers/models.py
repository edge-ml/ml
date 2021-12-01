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

@router.get("/models/")
async def models():
    print(type(EdgeModel).__name__)
    global edge_models

    return edge_models


@router.post("/models/{model_id}")
async def models_train():
    return "id of the model to train" #TODO return the trained model