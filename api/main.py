from typing import Union, Optional, Annotated
from fastapi import FastAPI, HTTPException, Depends, UploadFile
from strawberry.fastapi import GraphQLRouter
from pydantic import EmailStr
from mongoengine import connect, disconnect
import cloudinary
import os
from dotenv import load_dotenv

from .database.types import UserType, LoginType, UserSignUpType
from .schema import schema , Context
from .database.models import User as UserModel
from .utils import get_savan_data, password_hasher, password_checker
from .auth.handler import JWTBearer, encode_jwt, decode_jwt
from .uploader import upload_image

load_dotenv()

async def get_context() -> Context:
    return Context()

graphql_app = GraphQLRouter(schema, context_getter=get_context)
graphql_dev_app = GraphQLRouter(schema, debug=True, context_getter=get_context, graphql_ide="apollo-sandbox")

app = FastAPI(title="Beatify API", version="0.1.0")
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME", default="duqwlbo9s"),
    api_key=os.getenv("CLOUDINARY_API_KEY", default="852443822948814"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET", default="Y8BLlObJoLCU_wcTnVm0AmoeJ9U")
)
connect(host="mongodb+srv://raviblog:Ravisaini12beatify@beatify.8c3uw.mongodb.net/beatify?retryWrites=true&w=majority&appName=Beatify")
app.include_router(graphql_app, prefix="/graphql", include_in_schema=False)
app.include_router(graphql_dev_app, prefix="/dev/graphql", include_in_schema=False)

@app.get("/")
def root():
    return {"message": "Welcome to the Beatify API!", "version": "0.1.0", "status": "running"}

@app.post("/login")
def user_login(data: LoginType):
    user = UserModel.objects(email_address=data.email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not password_checker(data.password, user.password):
        raise HTTPException(status_code=403, detail="Invalid password")
    return {**encode_jwt(user.id), "user": UserType(**user.to_mongo().to_dict(), id=str(user.id))}

@app.post("/sign_up")
def user_sign_up(user: UserSignUpType):
    _user = UserModel.objects(email_address=user.email_address).first()
    if _user is not None:
        raise HTTPException(status_code=409, detail="User already exists")
    user_data = user.dict()
    user_data["password"] = password_hasher(user_data["password"])
    user = UserModel(**user_data).save()
    return {**encode_jwt(user.id), "user": UserType(**user.to_mongo().to_dict(), id=str(user.id))}


async def get_current_user(token: Annotated[str, Depends(JWTBearer())]):
    user_id = decode_jwt(token).get("user_id", None)
    if user_id is None:
        raise HTTPException(status_code=403, detail="Invalid token")
    user = UserModel.objects(id=user_id).first()
    return user

@app.get("/user/me", dependencies=[Depends(JWTBearer())], response_model=UserType)
async def read_user_me(current_user: UserModel | None = Depends(get_current_user)):
    return UserType(**current_user.to_mongo().to_dict(), id=str(current_user.id))

@app.get("/users/{email_address}")
async def read_user_me(email_address: EmailStr):
    user = UserModel.objects(email_address=email_address).first()
    print(user.to_mongo())
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserType(**user.to_mongo().to_dict())

@app.post("/user/{id}/upload", dependencies=[Depends(JWTBearer())])
async def upload_profile_picture(id: str, file: UploadFile):
    user = UserModel.objects(id=id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    url = await upload_image(file)
    user.profile_picture = url
    user.save()
    return UserType(**user.to_mongo().to_dict(), id=str(user.id))

@app.post("/users/", dependencies=[Depends(JWTBearer())])
async def create_user(user: UserType):
    inserted_user = UserModel(**user.dict()).save()
    return UserType(**inserted_user.to_mongo().to_dict())

@app.get("/savan_data")
async def read_savan_data():
    return get_savan_data()
