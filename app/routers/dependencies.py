from fastapi.param_functions import Depends
import jwt
from bson.objectid import ObjectId
from fastapi import status, Header, HTTPException
from app.db.models import get_model
from app.db.projects import get_project
from app.internal.config import SECRET_KEY

async def extract_project_id(project: str = Header(...)):
    return project

async def validate_user(Authorization: str = Header(...), project_id=Depends(extract_project_id)):
    try:
        token = Authorization.split(" ")[1]
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if "exp" not in decoded:
            raise jwt.ExpiredSignatureError
        user_id = ObjectId(decoded["id"])
        project = await get_project(project_id)
        # print("AUTH is:", Authorization)
        # print(user_id)
        # print(project)
        # print(project.admin)
        # print(project.users)
        if project.admin != user_id and user_id not in project.users:
            print('not in db')
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="User unauthorized on project")
        return (user_id, token)
    except jwt.ExpiredSignatureError:
       raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")

async def validate_model(model_id: str, user_id=Depends(validate_user), project_id=Depends(extract_project_id)):
    # print('validate model')
    # print(model_id)
    try:
        model = await get_model(model_id)
        if model.project_id != project_id:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access to the model")
        return model
    except Exception as e:
        print("exception is:")
        print(e)
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Model not found")