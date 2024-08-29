from typing import Union, Optional
from fastapi import FastAPI, HTTPException
from strawberry.fastapi import GraphQLRouter
from .schema import schema  
from pydantic import BaseModel
from contextlib import asynccontextmanager
from logging import info
from motor.motor_asyncio import AsyncIOMotorClient

from mongoengine import connect, disconnect
from .database.models import User as UserModel

from .utils import get_savan_data

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     app.mongodb_client = AsyncIOMotorClient("mongodb+srv://raviblog:Ravisaini12beatify@beatify.8c3uw.mongodb.net/?retryWrites=true&w=majority&appName=Beatify")
#     app.database = app.mongodb_client.get_database("beatify")
#     ping_response = await app.database.command("ping")
#     if int(ping_response["ok"]) != 1:
#         raise Exception("Problem connecting to database cluster.")
#     else:
#         info("Connected to database cluster.")
#     yield
#     app.mongodb_client.close()

graphql_app = GraphQLRouter(schema)

app = FastAPI(title="Beatify API", version="0.1.0")
connect(host="mongodb+srv://raviblog:Ravisaini12beatify@beatify.8c3uw.mongodb.net/beatify?retryWrites=true&w=majority&appName=Beatify")
app.include_router(graphql_app, prefix="/graphql", include_in_schema=False)

class User(BaseModel):
    first_name: str
    last_name: str
    middle_name: Optional[str] = None  # Make middle name optional
    email_address: str
    phone_number: str

@app.get("/")
def root():
    return {"message": "Api is running"}

@app.get("/users/{email_address}")
async def read_user_me(email_address: str):
    user = UserModel.objects(email_address=email_address).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    print(user.to_mongo())
    return User(**user.to_mongo())

@app.post("/users/")
async def create_user(user: User):
    inserted_user = UserModel(**user.dict()).save()
    return User(**inserted_user.to_mongo())

@app.get("/savan_data")
async def read_savan_data():
    return get_savan_data()