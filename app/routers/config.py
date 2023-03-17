from fastapi import APIRouter, Request, Header, Response
from fastapi.param_functions import Depends
from app.routers.dependencies import validate_user
from app.models import EDGE_MODELS

import traceback
import json
import orjson

router = APIRouter()

@router.get("/")
async def models():
    return [x.config() for x in EDGE_MODELS]