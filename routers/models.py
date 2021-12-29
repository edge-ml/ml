from fastapi import APIRouter, Depends
from numpy import empty
from pydantic import BaseModel
from typing import List

from requests.models import HTTPError
from internal.data_collection import fetch_dataset, fetch_project_datasets
from internal.data_preparation import concat_dataframes, extract_labels, create_dataframes, interpolate_values, merge_dataframes

from models.edge_model import EdgeModel
from models.kneighbours import KNeighbours
from models.mlp import MLP
from models.random_forest import RandomForest

from routers.dependencies import extract_project_id, validate_model, validate_user

router = APIRouter()

class TrainBody(BaseModel):
    selected_timeseries: List[str]
    window_size: int
    sliding_step: int

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
    },
    {
        'name': KNeighbours.get_name(),
        'description': KNeighbours.get_description(),
        'id': 3,
        'hyperparameters': KNeighbours.get_hyperparameters()
    },
    {
        'name': MLP.get_name(),
        'description': MLP.get_description(),
        'id': 4,
        'hyperparameters': MLP.get_hyperparameters()
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
async def models_train(model_id, user_id = Depends(validate_user), project_id = Depends(extract_project_id)):
    token = user_id[1]
    dataset_ids = fetch_project_datasets(project_id, token)
    if not dataset_ids:
        raise HTTPError("No dataset is available")
    datasets = [fetch_dataset(project_id, token, id) for id in dataset_ids]
    if any(hasattr(d, 'error') for d in datasets):
        raise HTTPError("Dataset not in requested project")
    # labels = [extract_labels(dataset, "61c9ff4008af2e55f32e4db0") for dataset in datasets]
    df_list_each_dataset = [create_dataframes(dataset, ["ACC_RAW_x", "ACC_RAW_y", "ACC_RAW_z", "GYRO_RAW_x", "GYRO_RAW_y", "GYRO_RAW_z"]) for dataset in datasets]
    df_merged_each_dataset = [merge_dataframes(df_list) for df_list in df_list_each_dataset]
    df_all = concat_dataframes(df_merged_each_dataset)
    interpolated = interpolate_values(df_all, 'linear', 'both')
    return True

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