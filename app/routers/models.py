from fastapi import APIRouter, Header, Response
from utils.jsonEncoder import JSONEncoder
from db.models import get_project_models, delete_model
from ml.Exporter import download_model
from utils.PyObjectId import PyObjectId
from controller.modelController import get_models

import json

router = APIRouter()


# Typing
from pydantic import BaseModel

class ReturnModel(BaseModel):
    pass



@router.get("/")
async def get_models_in_project(project: str = Header(...)):
    models = await get_models(project)
    return models

@router.delete("/{model_id}")
async def deleteModel(model_id, project: str = Header(...)):
    await delete_model(model_id, project)
    return Response(status_code=200)

@router.get("/download/{project}/{model_id}/{language}")
async def download_pipeline(project: str, model_id: PyObjectId, language: str):
    res = await download_model(model_id, project, language)
    return res