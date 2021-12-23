from fastapi import APIRouter, Depends

from models.edge_model import EdgeModel
from models.random_forest import RandomForest

from routers.dependencies import validateUser

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

# Create an edge model with given model id and hyperparameters
# Return the created model('s id)
@router.post("/models/{model_id}")
async def models_train(user_id = Depends(validateUser)):
    return "Created model('s id)" #TODO return the trained model

# Export a model
@router.get("/models/export")
async def models_export(platform: str):
    return f"Model export to {platform}..."

# Return a list of models that were trained before by the user
@router.get("/models/{user_id}") # userTrained / trained / created 
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