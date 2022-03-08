from typing import List
from fastapi import APIRouter, Depends, Request, Response

from ml.app.db.models import get_model
from .dependencies import deployment_authorized, deployment_unauthorized
from app.db.deployments import delete_deployment as db_delete_deployment, rename_deployment as db_rename_deployment

router = APIRouter()

##### Unauthorized

@router.get("/{deployment_key}")
async def deployment(deployment=Depends(deployment_unauthorized)):
    return {
        'name': deployment.name,
        'key': deployment.key,
        'creation_date': deployment.creation_date,
    }

# TODO: how to deal with platform??
@router.get("/{deployment_key}/export/{platform}")
async def download_deployment_model(platform: str, deployment=Depends(deployment_unauthorized)):
    model = await get_model(deployment.model_id)
    return Response(content=model.pickled_edge_model, media_type="application/octet-stream")

##### Authorized

@router.delete("/{deployment_key}")
async def delete_deployment(deployment=Depends(deployment_authorized)):
    return await db_delete_deployment(deployment.key)

@router.put("/{deployment_key}/name")
async def rename_deployment(request: Request, deployment=Depends(deployment_authorized)):
    return await db_rename_deployment(deployment.key, await request.body())
