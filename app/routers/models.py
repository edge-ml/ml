from fastapi import APIRouter, Header, Response, Depends, Request
from app.utils.jsonEncoder import JSONEncoder
from app.db.models import get_project_models, delete_model, get_model
from app.ml.Exporter import download_model
from app.utils.PyObjectId import PyObjectId
from app.routers.dependencies import validate_user
from app.controller.ModelController import ModelController

import json

router = APIRouter()

model_controller = ModelController()

@router.get("/{model_id}")
async def get_model_by_id(model_id, project: str = Header(...), user=Depends(validate_user)):
    res = await model_controller.get_model_by_id(project, model_id)
    return Response(json.dumps(res, cls=JSONEncoder), media_type="application/json")

@router.get("/")
async def get_models(project: str = Header(...)):
    res = await model_controller.get_models(project)
    return Response(json.dumps(res, cls=JSONEncoder), media_type="application/json")

@router.delete("/{model_id}")
async def deleteModel(model_id, project: str = Header(...), user=Depends(validate_user)):
    res = await model_controller.delete_model(project, model_id)
    return Response(status_code=200)

@router.put("/{model_id}")
async def update_model(model_id, body: Request, project: str = Header(...), user=Depends(validate_user)):
    model = await body.json()
    res = await model_controller.update_model(project, model_id, model)
    return Response(json.dumps(res, cls=JSONEncoder), media_type="application/json")

# @router.get("/download/{model_id}/{language}")
# async def download_pipeline(model_id: PyObjectId, language: str, project: str = Header(...),  user=Depends(validate_user)):
#     res = await download_model(model_id, project, language)
#     return res