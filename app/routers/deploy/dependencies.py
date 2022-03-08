from fastapi.param_functions import Depends
from fastapi import status, HTTPException
from app.db.deployments import get_deployment

from app.routers.dependencies import validate_user, extract_project_id

async def deployment_authorized(deployment_key: str, user_id=Depends(validate_user), project_id=Depends(extract_project_id)):
    # print('authorized deployment')
    # print(deployment_key)
    try:
        deployment = await get_deployment(deployment_key)
        if deployment.project_id != project_id:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access to the deployment")
        return deployment
    except Exception as e:
        print("exception is:")
        print(e)
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Deployment not found")

async def deployment_unauthorized(deployment_key: str):
    # print('unauthorized deployment')
    # print(deployment_key)
    try:
        deployment = await get_deployment(deployment_key)
        return deployment
    except Exception as e:
        print("exception is:")
        print(e)
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Deployment not found")