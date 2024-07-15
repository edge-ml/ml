from fastapi import APIRouter, Header, Response, Depends, Request
from app.utils.jsonEncoder import JSONEncoder
from app.routers.dependencies import validate_user
from app.controller.ModelController import ModelController
from pydantic.v1.json import ENCODERS_BY_TYPE
from bson.objectid import ObjectId

import json


ENCODERS_BY_TYPE[ObjectId] = str


router = APIRouter()

model_controller = ModelController()

@router.get("/{model_id}")
async def get_model_by_id(model_id, project: str = Header(...)):
    res = model_controller.get_model_by_id(project, model_id)
    return Response(json.dumps(res, cls=JSONEncoder), media_type="application/json")

@router.get("/")
async def get_models(project: str = Header(...)):
    res = model_controller.get_models(project)
    res = [res.dict(by_alias=True) for res in res]
    return Response(json.dumps(res, cls=JSONEncoder), media_type="application/json")

@router.delete("/{model_id}")
async def deleteModel(model_id, project: str = Header(...)):
    success = model_controller.delete_model(project, model_id)
    if success:
        return Response(status_code=200)
    return Response(status_code=400)

@router.put("/{model_id}")
async def update_model(model_id, body: Request, project: str = Header(...)):
    model = await body.json()
    success = model_controller.update_model(project, model_id, model)
    if success:
        return Response(status_code=200)
    return Response(status_code=400)

# @router.get("/download/{model_id}/{language}")
# async def download_pipeline(model_id: PyObjectId, language: str, project: str = Header(...),  user=Depends(validate_user)):
#     res = await download_model(model_id, project, language)
#     return res