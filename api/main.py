from typing import Union, Optional, Annotated
from fastapi import FastAPI, HTTPException, Depends
from strawberry.fastapi import GraphQLRouter
from pydantic import EmailStr
from mongoengine import connect, disconnect

from .database.types import UserType, LoginType, UserSignUpType
from .schema import schema , Context
from .database.models import User as UserModel
from .utils import get_savan_data
from .auth.handler import JWTBearer, encode_jwt, decode_jwt

async def get_context() -> Context:
    return Context()

graphql_app = GraphQLRouter(schema, debug=True, context_getter=get_context)

app = FastAPI(title="Beatify API", version="0.1.0")
connect(host="mongodb+srv://raviblog:Ravisaini12beatify@beatify.8c3uw.mongodb.net/beatify?retryWrites=true&w=majority&appName=Beatify")
app.include_router(graphql_app, prefix="/graphql", include_in_schema=False)

@app.get("/")
def root():
    return {"message": "Api is running"}

@app.post("/login")
def user_login(data: LoginType):
    user = UserModel.objects(email_address=data.email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    # if user.password != data.password:
    #     raise HTTPException(status_code=403, detail="Invalid password")
    return encode_jwt(str(user.id))

@app.post("/sign_up")
def user_sign_up(user: UserSignUpType):
    user = UserModel(**user.dict()).save()
    return encode_jwt(str(user.id))

async def get_current_user(token: Annotated[str, Depends(JWTBearer())]):
    user_id = decode_jwt(token).get("user_id", None)
    if user_id is None:
        raise HTTPException(status_code=403, detail="Invalid token")
    user = UserModel.objects(id=user_id).first()
    return user

@app.get("/user/me", dependencies=[Depends(JWTBearer())])
async def read_user_me(current_user: UserModel | None = Depends(get_current_user)):
    print(current_user.to_mongo().to_dict())
    return {**current_user.to_mongo().to_dict(), "id": current_user.pk}

@app.get("/users/{email_address}")
async def read_user_me(email_address: EmailStr):
    user = UserModel.objects(email_address=email_address).first()
    print(user.to_mongo())
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserType(**user.to_mongo())

@app.post("/users/", dependencies=[Depends(JWTBearer())])
async def create_user(user: UserType):
    inserted_user = UserModel(**user.dict()).save()
    return UserType(**inserted_user.to_mongo())

@app.get("/savan_data")
async def read_savan_data():
    return get_savan_data()