from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import List
from fastapi import status, HTTPException
from starlette.requests import Request
from app.ml.trainer import Trainer
import asyncio
from app.routers.dependencies import extract_project_id, validate_user

from app.internal.data_collection import fetch_dataset, fetch_project_datasets
from app.internal.data_preparation import format_hyperparameters

from app.routers.models.models import edge_models

router = APIRouter()

class TrainBody(BaseModel):
    model_id: int
    model_name: str
    selected_timeseries: List[str]
    hyperparameters: List
    target_labeling: str

# Create an edge model with given model id and hyperparameters
# Return the created model('s id)
@router.post("/")
async def models_train(request: Request, body: TrainBody, background_tasks: BackgroundTasks, user_id=Depends(validate_user), project_id=Depends(extract_project_id)):
    model_id = body.model_id
    model_name = body.model_name
    if not model_name:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="No name is given")
    window_size = next((param for param in body.hyperparameters if param["parameter_name"] == "window_size"), None)["state"]
    sliding_step = next((param for param in body.hyperparameters if param["parameter_name"] == "sliding_step"), None)["state"]
    selected_model = next((model for model in edge_models if model["id"] == model_id), None)["model"]
    hyperparameters = format_hyperparameters(body.hyperparameters)
    target_labeling = body.target_labeling
    selected_timeseries = body.selected_timeseries
    token = user_id[1]
    if not selected_timeseries:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="No timeseries is selected")
    
    dataset_ids = await fetch_project_datasets(project_id, token)
    if not dataset_ids:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="No dataset is available")
    
    datasets = await asyncio.gather(*[fetch_dataset(project_id, token, id) for id in dataset_ids])
    if any(hasattr(d, "error") for d in datasets):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Dataset not in requested project")

    t = Trainer(model_name, project_id, target_labeling, datasets, selected_timeseries, window_size, sliding_step, selected_model, hyperparameters)
    
    request.app.state.training_manager.add(t)
    background_tasks.add_task(request.app.state.training_manager.start, t.id)

    return t.id