from dotenv.main import load_dotenv
import jwt
import os
from bson.objectid import ObjectId
from fastapi import status, Header, HTTPException

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

async def validateUser(Authorization: str = Header(...)):
    try:
        token = Authorization.split(' ')[1]
        print(token)
        print(SECRET_KEY)
        decoded = jwt.decode(token, SECRET_KEY, algorithm="HS256")
        print(decoded)
        if 'exp' not in decoded:
            raise jwt.ExpiredSignatureError
        userId = ObjectId(decoded['id'])
        return userId
    except:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    