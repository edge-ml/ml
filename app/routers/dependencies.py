from fastapi.param_functions import Depends
import jwt
from bson.objectid import ObjectId
from fastapi import status, Header, HTTPException
from app.db.models import get_model
from app.internal.config import SECRET_KEY

async def validate_user(Authorization: str = Header(...)):
    try:
        token = Authorization.split(" ")[1]
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if "exp" not in decoded:
            raise jwt.ExpiredSignatureError
        user_id = ObjectId(decoded["id"])
        return (user_id, token)
    except:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

async def extract_project_id(project: str = Header(...)):
    return project

async def validate_model(model_id: str, user_id=Depends(validate_user), project_id=Depends(extract_project_id)):
    print('validate model')
    print(model_id)
    try:
        model = await get_model(model_id)
        if model.project_id != project_id:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access to the model")
        return model
    except Exception as e:
        print(e)
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Model not found")


