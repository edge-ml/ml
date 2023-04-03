from fastapi import APIRouter, Request, Header, Response, BackgroundTasks
from fastapi.param_functions import Depends
from app.routers.dependencies import validate_user
from app.models import EDGE_MODELS
from app.utils.PyObjectId import PyObjectId
from typing import List
from pydantic import BaseModel, Field
from app.utils.jsonEncoder import JSONEncoder
from app.ml.trainer import train
from app.models import EDGE_MODELS
from app.db.models import get_project_models

import traceback
import json
import orjson

router = APIRouter()


@router.get("/")
async def get_models(project: str = Header(...)):
    res= await get_project_models(project)
    return Response(json.dumps(res, cls=JSONEncoder), media_type="application/json")


@router.delete("/")
async def delete_model():
    pass