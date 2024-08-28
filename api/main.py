from typing import Union, Optional
from fastapi import FastAPI, HTTPException
from strawberry.fastapi import GraphQLRouter
from .schema import schema  
from pydantic import BaseModel
from contextlib import asynccontextmanager
from logging import info
from motor.motor_asyncio import AsyncIOMotorClient

@asynccontextmanager
async def db_lifespan(app: FastAPI):
    # Startup
    app.mongodb_client = AsyncIOMotorClient("mongodb+srv://raviblog:Ravisaini12beatify@beatify.8c3uw.mongodb.net/?retryWrites=true&w=majority&appName=Beatify")
    app.database = app.mongodb_client.get_database("beatify")
    ping_response = await app.database.command("ping")
    if int(ping_response["ok"]) != 1:
        raise Exception("Problem connecting to database cluster.")
    else:
        info("Connected to database cluster.")
    yield

    # Shutdown
    app.mongodb_client.close()


graphql_app = GraphQLRouter(schema)

app = FastAPI(title="Beatify API", version="0.1.0", lifespan=db_lifespan)

app.include_router(graphql_app, prefix="/graphql", include_in_schema=False)

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


class User(BaseModel):
    first_name: str
    last_name: str
    middle_name: Optional[str] = None  # Make middle name optional
    email_address: str
    phone_number: str


@app.get("/users/{email_address}", response_model=User)
async def read_user_me(email_address: str):
    user = await app.database["users"].find_one({"email_address": email_address})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/users/")
async def create_user(user: User):
    result = await app.database["users"].insert_one(user.dict())
    inserted_user = await app.database["users"].find_one({"_id": result.inserted_id})
    return User(**inserted_user)