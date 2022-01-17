from fastapi import APIRouter, Depends
from numpy import empty
from pydantic import BaseModel
from typing import List

from requests.models import HTTPError
from internal.data_collection import fetch_dataset, fetch_project_datasets
from internal.data_preparation import (
    extract_labels,
    create_dataframes,
    format_hyperparameters,
    interpolate_values,
    label_dataset,
    merge_dataframes,
    roll_sliding_window,
)
from internal.training import train

from models.edge_model import EdgeModel
from models.kneighbours import KNeighbours
from models.mlp import MLP
from models.random_forest import RandomForest

from routers.dependencies import extract_project_id, validate_model, validate_user

router = APIRouter()


class TrainBody(BaseModel):
    model_id: int
    selected_timeseries: List[str]
    hyperparameters: List
    target_labeling: str


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
    {
        "name": MLP.get_name(),
        "description": MLP.get_description(),
        "id": 3,
        "hyperparameters": MLP.get_hyperparameters(),
        "model": MLP(),
    },
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
async def models_train(body: TrainBody, user_id=Depends(validate_user), project_id=Depends(extract_project_id)):
    model_id = body.model_id
    window_size = next((param for param in body.hyperparameters if param["parameter_name"] == "window_size"), None)["state"]
    sliding_step = next((param for param in body.hyperparameters if param["parameter_name"] == "sliding_step"), None)["state"]
    selected_model = next((model for model in edge_models if model["id"] == model_id), None)["model"]

    hyperparameters = format_hyperparameters(body.hyperparameters)
    target_labeling = body.target_labeling
    selected_timeseries = body.selected_timeseries
    token = user_id[1]
    if not selected_timeseries:
        raise HTTPError("No timeseries is selected")
    
    dataset_ids = fetch_project_datasets(project_id, token)
    if not dataset_ids:
        raise HTTPError("No dataset is available")
    
    datasets = [fetch_dataset(project_id, token, id) for id in dataset_ids]
    if any(hasattr(d, "error") for d in datasets):
        raise HTTPError("Dataset not in requested project")
    
    labels_with_intervals = [extract_labels(dataset, target_labeling) for dataset in datasets]
    labels = set([label["label_id"] for label in labels_with_intervals[0]])
    label_map = {label: idx for idx, label in enumerate(labels)}
    label_map["Other"] = len(label_map)
    df_list_each_dataset = [create_dataframes(dataset, selected_timeseries) for dataset in datasets]
    df_merged_each_dataset = [merge_dataframes(df_list) for df_list in df_list_each_dataset]
    df_interpolated_each_dataset = [interpolate_values(df, "linear", "both") for df in df_merged_each_dataset]
    
    df_labeled_each_dataset = [
        label_dataset(df, labels_with_intervals[idx], label_map)
        for idx, df in enumerate(df_interpolated_each_dataset)
    ]
    
    (df_sliding_window, data_y) = roll_sliding_window(
        df_labeled_each_dataset, window_size, sliding_step, len(selected_timeseries)
    )
    
    train(df_sliding_window, data_y, selected_model, hyperparameters)
    return True


# Return a list of models that were trained before by the user
@router.get("/userModels")  # userTrained / trained / created
async def models_user_created(user_id=Depends(validate_user)):
    return "List of models"


# Get a list of platforms the model is available to.
@router.get("/models/platforms")
async def models_platforms():
    return "Platforms the model is available to"


# Export a model
@router.get("/models/{model_id}/export")
async def models_export(platform: str, validation=Depends(validate_model)):
    return f"Model export to {platform}..."


# Get the perfomance metrics of a trained model
@router.get("/models/{model_id}/metrics")
async def models_metrics(validation=Depends(validate_model)):
    return "Performance metrics"
