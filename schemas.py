from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6)
    roles: List[str] = ["user"]

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    password: Optional[str] = Field(None, min_length=6)
    roles: Optional[List[str]] = None

class UserResponse(BaseModel):
    id: int
    username: str
    roles: List[str]
    created_at: datetime

    class Config:
        from_attributes = True

class RoleCreate(BaseModel):
    name: str

class RoleResponse(BaseModel):
    id: int
    name: str

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class AdvertisementCreate(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    price: float = Field(..., gt=0)

class AdvertisementUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)

class AdvertisementResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    price: float
    author_id: int
    created_at: datetime

    class Config:
        from_attributes = True
