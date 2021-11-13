from fastapi import APIRouter

from models.edge_model import EdgeModel
from models.random_forest import RandomForest

router = APIRouter()

# TODO this should be declared somewhere else
models = [
    {
        'name': type(EdgeModel).__name__,
        'id': 1,
        'hyperparameters': EdgeModel.get_hyperparameters()
    },
    {
        'name': type(RandomForest).__name__,
        'id': 2,
        'hyperparameters': RandomForest.get_hyperparameters()
    }
]

@router.get("/model/")
async def model():
    return 


@router.post("/model/{model_id}")
async def model_train():
    return "id of the model to train" #TODO return the trained model


@router.get("/model/trained")
async def model_trained():
    return "trained models list" #TODO returns the list of trained models

@router.get("/model/trained/{trained_model_id}")
async def model_trained():
    return "trained models" #TODO returns the trained model
