from fastapi import APIRouter, Header, Response
from app.utils.jsonEncoder import JSONEncoder
from app.db.models import get_project_models, delete_model, get_model
from app.ml.Exporter import download_model
from app.utils.PyObjectId import PyObjectId

import json

router = APIRouter()


@router.get("/{model_id}")
async def get_model_by_id(model_id, project: str = Header(...)):
    res = await get_model(model_id, project)
    res = res.dict(by_alias=True)
    return Response(json.dumps(res, cls=JSONEncoder), media_type="application/json")

@router.get("/")
async def get_models(project: str = Header(...)):
    res = await get_project_models(project)
    return Response(json.dumps(res, cls=JSONEncoder), media_type="application/json")


@router.delete("/{model_id}")
async def deleteModel(model_id, project: str = Header(...)):
    await delete_model(model_id, project)
    return Response(status_code=200)

@router.get("/download/{project}/{model_id}/{language}")
async def download_pipeline(project: str, model_id: PyObjectId, language: str):
    res = await download_model(model_id, project, language)
    print(res)
    return res