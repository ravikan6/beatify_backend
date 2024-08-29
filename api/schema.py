import strawberry
from .database.models import User as UserModel

@strawberry.type
class User:
    id: str | None
    first_name: str
    last_name: str
    middle_name: str
    email_address: str
    phone_number: str

@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello World"
    def user(self) -> User:
        return UserModel.objects().first()

schema = strawberry.Schema(query=Query)
# The schema is created using the strawberry.Schema class.