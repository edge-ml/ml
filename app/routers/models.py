from fastapi import APIRouter, Header, Response
from app.utils.jsonEncoder import JSONEncoder
from app.db.models import get_project_models, delete_model

import json

router = APIRouter()


@router.get("/")
async def get_models(project: str = Header(...)):
    res = await get_project_models(project)
    return Response(json.dumps(res, cls=JSONEncoder), media_type="application/json")


@router.delete("/{model_id}")
async def deleteModel(model_id, project: str = Header(...)):
    await delete_model(model_id, project)
    return Response(status_code=200)