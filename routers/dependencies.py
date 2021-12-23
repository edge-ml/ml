from dotenv.main import load_dotenv
from fastapi.param_functions import Depends
import jwt
import os
from bson.objectid import ObjectId
from fastapi import status, Header, HTTPException

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

async def validate_user(Authorization: str = Header(...)):
    try:
        token = Authorization.split(' ')[1]
        print(token)
        print(SECRET_KEY)
        decoded = jwt.decode(token, SECRET_KEY, algorithm="HS256")
        print(decoded)
        if 'exp' not in decoded:
            raise jwt.ExpiredSignatureError
        user_id = ObjectId(decoded['id'])
        return user_id
    except:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

async def validate_model(user_id = Depends(validate_user)):
    # TODO check with db 
    return True
