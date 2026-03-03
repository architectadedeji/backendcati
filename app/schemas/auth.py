from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, Literal


class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: Literal["admin", "interviewer", "contact"] = "interviewer"
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    user: UserResponse


class TokenData(BaseModel):
    user_id: int
    username: str
