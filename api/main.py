from typing import Union
import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello World"

schema = strawberry.Schema(query=Query)

graphql_app = GraphQLRouter(schema)

app = FastAPI(title="Beatify API", version="0.1.0")

app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}