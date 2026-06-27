from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str
    group: Optional[str] = "user"

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    group: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    group: str
    created_at: datetime

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class AdvertisementCreate(BaseModel):
    title: str
    description: Optional[str] = None
    price: float

class AdvertisementUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None

class AdvertisementResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    price: float
    author_id: int
    created_at: datetime

    class Config:
        from_attributes = True