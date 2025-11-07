from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
import uuid

class UserBase(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: str
    team: str
    role: str
    address: str
    is_active: Optional[bool] = True

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    password: str

    class Config:
        from_attributes = True
    

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: uuid.UUID
    created_at: date
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str