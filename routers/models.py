from fastapi import APIRouter, Depends

from models.edge_model import EdgeModel
from models.random_forest import RandomForest

from routers.dependencies import validate_model, validate_user

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
@router.get("/models")
async def models():
    print(type(EdgeModel).__name__)
    global edge_models

    return edge_models

# Create an edge model with given model id and hyperparameters
# Return the created model('s id)
@router.post("/train")
async def models_train(model_id, user_id = Depends(validate_user)):
    return "Created model('s id)" #TODO return the trained model

# Return a list of models that were trained before by the user
@router.get("/userModels") # userTrained / trained / created 
async def models_user_created(user_id = Depends(validate_user)):
    return "List of models"

# Get a list of platforms the model is available to.
@router.get("/models/platforms")
async def models_platforms():
    return "Platforms the model is available to"

# Export a model
@router.get("/models/{model_id}/export")
async def models_export(platform: str, validation = Depends(validate_model)):
    return f"Model export to {platform}..."

# Get the perfomance metrics of a trained model
@router.get("/models/{model_id}/metrics")
async def models_metrics(validation = Depends(validate_model)):
    return "Performance metrics"