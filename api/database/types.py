from pydantic import BaseModel, EmailStr, SecretStr
from typing import Optional, Any, Annotated
from datetime import datetime


class LoginType(BaseModel):
    email: EmailStr
    password: str

class BaseUserType(BaseModel):
    first_name: str
    last_name: str | None
    middle_name: Optional[str] = None  # Make middle name optional
    email: EmailStr
    phone_number: Optional[str] = None
    date_of_birth: datetime | str | None
    gender: str | None

class UserType(BaseUserType):
    id: str
    is_active: bool
    date_joined: datetime | str | None = None
    profile_picture: str | None = None


class UserSignUpType(BaseUserType):
    password: str
    updates: bool | None = False