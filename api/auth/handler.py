from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from time import time
import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False

        try:
            payload = decode_jwt(jwtoken)
        except:
            payload = None
        if payload:
            isTokenValid = True

        return isTokenValid


def get_secret_key() -> str:
    load_dotenv()
    key = os.getenv("SECRET_KEY")
    if not key: raise HTTPException(status_code=500, detail="Internal Server Error - No JWT secret key found.")
    return key

def encode_jwt(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "expires": (datetime.now() + timedelta(weeks=3)).isoformat()
    }
    token = jwt.encode(payload, get_secret_key(), algorithm="HS256")
    return {
        "token": token,
        "expires": payload["expires"]
    }

def decode_jwt(token: str) -> dict:
    try:
        payload = jwt.decode(token, get_secret_key(), algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        payload = None
    except jwt.InvalidTokenError:
        payload = None
    return payload