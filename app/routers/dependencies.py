from fastapi.param_functions import Depends
import jwt
import os
from bson.objectid import ObjectId
from fastapi import status, Header, HTTPException
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
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


async def validate_model(user_id=Depends(validate_user)):
    # TODO check with db
    return True


async def extract_project_id(project: str = Header(...)):
    return project
