from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.database import get_db, engine, Base
from app import crud
from app.schemas import (
    UserCreate, UserUpdate, UserResponse,
    LoginRequest, LoginResponse,
    AdvertisementCreate, AdvertisementUpdate, AdvertisementResponse
)
from app.auth import verify_password, create_token
from app.dependencies import get_current_user, get_current_user_optional, require_admin
from app.models import User
from app.rbac import has_permission, can_manage_user, can_manage_advertisement

app = FastAPI(title="Advertisement Service", version="2.0.0")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with get_db() as db:
        await crud.create_default_roles(db)

@app.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await crud.get_user_by_username(db, login_data.username)
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    access_token = create_token(user.id)
    return LoginResponse(access_token=access_token)

@app.post("/user", response_model=UserResponse, status_code=201)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    existing_user = await crud.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    if "admin" in user_data.roles:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can create users with admin role"
        )
    
    return await crud.create_user(db, user_data)

@app.get("/user", response_model=list[UserResponse])
async def get_all_users(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    users = await crud.get_all_users(db)
    return [UserResponse(
        id=user.id,
        username=user.username,
        roles=[role.name for role in user.roles],
        created_at=user.created_at
    ) for user in users]

@app.get("/user/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):

    user = await crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=user.id,
        username=user.username,
        roles=[role.name for role in user.roles],
        created_at=user.created_at
    )

@app.patch("/user/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    if not can_manage_user(current_user, user_id):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    if user_data.roles is not None and not has_permission(current_user, "user:change_role"):
        raise HTTPException(status_code=403, detail="Only admin can change roles")
    
    user = await crud.update_user(db, user_id, user_data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=user.id,
        username=user.username,
        roles=[role.name for role in user.roles],
        created_at=user.created_at
    )

@app.delete("/user/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Удаление пользователя (только свои данные или admin)"""
    if not can_manage_user(current_user, user_id):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    deleted = await crud.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"ok": True}

@app.post("/advertisement", response_model=AdvertisementResponse, status_code=201)
async def create_advertisement(
    ad_data: AdvertisementCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await crud.create_advertisement(db, ad_data, current_user.id)

@app.get("/advertisement/{advertisement_id}", response_model=AdvertisementResponse)
async def get_advertisement(
    advertisement_id: int,
    db: AsyncSession = Depends(get_db)
):
    ad = await crud.get_advertisement(db, advertisement_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return ad

@app.get("/advertisement", response_model=list[AdvertisementResponse])
async def search_advertisements(
    title: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
    price_min: Optional[float] = Query(None),
    price_max: Optional[float] = Query(None),
    author_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    filters = {
        "title": title,
        "description": description,
        "price_min": price_min,
        "price_max": price_max,
        "author_id": author_id
    }
    filters = {k: v for k, v in filters.items() if v is not None}
    return await crud.get_advertisements(db, filters)

@app.patch("/advertisement/{advertisement_id}", response_model=AdvertisementResponse)
async def update_advertisement(
    advertisement_id: int,
    ad_data: AdvertisementUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    ad = await crud.get_advertisement(db, advertisement_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    
    if not can_manage_advertisement(current_user, ad.author_id):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    updated = await crud.update_advertisement(db, advertisement_id, ad_data)
    return updated

@app.delete("/advertisement/{advertisement_id}")
async def delete_advertisement(
    advertisement_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    ad = await crud.get_advertisement(db, advertisement_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    
    if not can_manage_advertisement(current_user, ad.author_id):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    deleted = await crud.delete_advertisement(db, advertisement_id)
    return {"ok": True}
