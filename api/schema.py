import strawberry
from strawberry.scalars import Dict
from .database.models import User as UserModel
from .utils import get_savan_data
from typing import NewType, Any


JSON = strawberry.scalar(
    NewType("JSON", object),
    description="The `JSON` scalar type represents JSON values as specified by ECMA-404",
    serialize=lambda v: v,
    parse_value=lambda v: v,
)


@strawberry.type
class User:
    id: str | None
    first_name: str
    last_name: str
    middle_name: str | None
    email_address: str
    phone_number: str

@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello World"

    @strawberry.field
    def user(self) -> User:
        return UserModel.objects().first()

    @strawberry.field
    def savan_data(self) -> JSON:
        return get_savan_data()

schema = strawberry.Schema(query=Query)
# The schema is created using the strawberry.Schema class.