# from fastapi import APIRouter, Depends, BackgroundTasks, Header
# from pydantic import BaseModel, Field
# from typing import List
# from fastapi import status, HTTPException, Response
# from starlette.requests import Request
# from routers.dependencies import extract_project_id, validate_user

# from routers.models.models import edge_models
# from validation import ValidationBody
# from utils.PyObjectId import PyObjectId

# import json
# import orjson
# from utils.jsonEncoder import JSONEncoder

# from ml.trainer import train

# router = APIRouter()

# class Training(BaseModel):
#     id: str
#     name: str
#     training_state: TrainingState
#     error_msg: str

# class ModelInfo(BaseModel):
#     hyperparameters: List
#     classifier: str

# class TrainDatasetModel(BaseModel):
#     id : PyObjectId = Field(alias="_id")
#     timeSeries: List[PyObjectId]

# class TrainRequest(BaseModel):
#     name: str
#     datasets: List[TrainDatasetModel]
#     labeling: PyObjectId
#     name: str
#     modelInfo: ModelInfo



# @router.post("/")
# async def models_train(body: TrainRequest, background_tasks: BackgroundTasks, project: str = Header(...), user_data=Depends(validate_user)):
#     id = await train(body, project=project, background_tasks = background_tasks)
#     return Response(json.dumps(id, cls=JSONEncoder), media_type="application/json")

# # Get an active training process
# @router.get("/ongoing/{train_id}", response_model=Training)
# async def trained_model(train_id: str, request: Request, user_data=Depends(validate_user), project_id=Depends(extract_project_id)):
#     tm: TrainingManager = request.app.state.training_manager
#     if not tm.has(train_id, project_id):
#         raise HTTPException(status_code=404, detail="No active training process with given id")
#     t = tm.get(train_id, project_id)
#     return Training(**t.__dict__)

# # Get all active training processes
# @router.get("/ongoing", response_model=List[Training])
# async def trained_model(request: Request, user_data=Depends(validate_user), project_id=Depends(extract_project_id)):
#     tm: TrainingManager = request.app.state.training_manager
#     return [ Training(**t.__dict__) for t in tm.all(project_id) ]


# Create an edge model with given model id and hyperparameters
# Return the created model('s id)
# @router.post("/")
# async def models_train(request: Request, body: TrainBody, background_tasks: BackgroundTasks, user_data=Depends(validate_user), project_id=Depends(extract_project_id)):
#     model_id = body.model_id
#     model_name = body.model_name
#     window_size = next((param for param in body.hyperparameters if param["parameter_name"] == "window_size"), None)["state"]
#     sliding_step = next((param for param in body.hyperparameters if param["parameter_name"] == "sliding_step"), None)["state"]
#     windowing_mode = next((param for param in body.hyperparameters if param["parameter_name"] == "windowing_mode"), None)["state"]["value"]
#     selected_model = next((model for model in edge_models if model["id"] == model_id), None)["model"]
#     use_unlabelled = body.use_unlabelled
#     unlabelled_name = body.unlabelled_name
#     target_labeling = body.target_labeling
#     labels = body.labels
#     selected_timeseries = body.selected_timeseries
#     token = user_data[1]
#     sub_level = user_data[2] if user_data[2] else "standard"
   
#     if not model_name:
#         raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="No name is given")

#     if not labels:
#         raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="No label is selected")

#     if not selected_timeseries:
#         raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="No timeseries is selected")
    
#     if not unlabelled_name and use_unlabelled:
#         raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="No name is provided for the other label")

#     if unlabelled_name in labels:
#         raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Cannot use id of a label as other label")
    
#     background_tasks.add_task(request.app.state.training_manager.initiate,
#                                 token, model_name, project_id, 
#                                 target_labeling, labels, selected_timeseries,
#                                 window_size, sliding_step, windowing_mode,
#                                 use_unlabelled, unlabelled_name, 
#                                 selected_model, body.hyperparameters, 
#                                 sub_level,
#                                 validation=body.validation)
#     return "success"
