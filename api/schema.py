import strawberry
from strawberry.scalars import Dict
from .database.models import User as UserModel
from .utils import get_savan_data
from typing import NewType, Any
from strawberry.schema.config import StrawberryConfig
from strawberry.fastapi import BaseContext
from .auth.handler import decode_jwt
from functools import cached_property
from fastapi import HTTPException

JSON = strawberry.scalar(
    NewType("JSON", object),
    description="The `JSON` scalar type represents JSON values as specified by ECMA-404",
    serialize=lambda v: v,
    parse_value=lambda v: v,
)

@strawberry.type
class User:
    id: str
    first_name: str
    last_name: str
    middle_name: str | None
    email_address: str
    phone_number: str


class Context(BaseContext):
    @cached_property
    def user(self) -> User | None:
        if not self.request:
            return None
        authorization = self.request.headers.get("Authorization", None)
        if authorization:
            token = authorization.split(' ')
            if not token or len(token) != 2 or token.index('Bearer') != 0 or not decode_jwt(token[1]):
                raise HTTPException(status_code=403, detail="Invalid token")
            user_id = decode_jwt(token[1]).get("user_id", None)
            if user_id is None:
                raise HTTPException(status_code=403, detail="Invalid token")
            user = UserModel.objects(id=user_id).first()
            if user and user.is_active:
                return user
            return None
        else: return None


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

    @strawberry.field
    def me(self, info: strawberry.Info[Context]) -> User | None:
        return info.context.user

schema = strawberry.Schema(query=Query, config=StrawberryConfig(auto_camel_case=False))
# The schema is created using the strawberry.Schema class.