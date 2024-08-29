from pydantic import BaseModel, EmailStr, SecretStr
from typing import Optional, Any, Annotated
from datetime import datetime


class LoginType(BaseModel):
    email: EmailStr
    password: str

class BaseUserType(BaseModel):
    first_name: str
    last_name: str
    middle_name: Optional[str] = None  # Make middle name optional
    email_address: str
    phone_number: str | None
    date_of_birth: datetime | str | None

class UserType(BaseUserType):
    id: str
    is_active: bool
    date_joined: datetime | str | None
    profile_picture: str | None


class UserSignUpType(BaseUserType):
    password: SecretStr