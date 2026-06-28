from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models import User, Role, Advertisement
from app.schemas import UserCreate, UserUpdate, AdvertisementCreate, AdvertisementUpdate
from app.auth import hash_password

async def create_user(db: AsyncSession, user_data: UserCreate):
    hashed_password = hash_password(user_data.password)
    db_user = User(
        username=user_data.username,
        password_hash=hashed_password
    )

    for role_name in user_data.roles:
        result = await db.execute(select(Role).where(Role.name == role_name))
        role = result.scalar_one_or_none()
        if role:
            db_user.roles.append(role)
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.roles))
    )
    return result.scalar_one_or_none()

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(
        select(User)
        .where(User.username == username)
        .options(selectinload(User.roles))
    )
    return result.scalar_one_or_none()

async def get_all_users(db: AsyncSession):
    result = await db.execute(
        select(User).options(selectinload(User.roles))
    )
    return result.scalars().all()

async def update_user(db: AsyncSession, user_id: int, user_data: UserUpdate):
    user = await get_user_by_id(db, user_id)
    if not user:
        return None
    
    if user_data.username is not None:
        user.username = user_data.username
    if user_data.password is not None:
        user.password_hash = hash_password(user_data.password)
    if user_data.roles is not None:
        user.roles = []
        for role_name in user_data.roles:
            result = await db.execute(select(Role).where(Role.name == role_name))
            role = result.scalar_one_or_none()
            if role:
                user.roles.append(role)
    
    await db.commit()
    await db.refresh(user)
    return user

async def delete_user(db: AsyncSession, user_id: int):
    user = await get_user_by_id(db, user_id)
    if not user:
        return False
    await db.delete(user)
    await db.commit()
    return True

async def create_default_roles(db: AsyncSession):
    roles = ["user", "admin"]
    for role_name in roles:
        result = await db.execute(select(Role).where(Role.name == role_name))
        if not result.scalar_one_or_none():
            db.add(Role(name=role_name))
    await db.commit()

async def create_advertisement(db: AsyncSession, ad_data: AdvertisementCreate, author_id: int):
    db_ad = Advertisement(
        title=ad_data.title,
        description=ad_data.description,
        price=ad_data.price,
        author_id=author_id
    )
    db.add(db_ad)
    await db.commit()
    await db.refresh(db_ad)
    return db_ad

async def get_advertisement(db: AsyncSession, ad_id: int):
    result = await db.execute(select(Advertisement).where(Advertisement.id == ad_id))
    return result.scalar_one_or_none()

async def get_advertisements(db: AsyncSession, filters: dict):
    query = select(Advertisement)
    
    if filters.get("title"):
        query = query.where(Advertisement.title.ilike(f"%{filters['title']}%"))
    if filters.get("description"):
        query = query.where(Advertisement.description.ilike(f"%{filters['description']}%"))
    if filters.get("price_min"):
        query = query.where(Advertisement.price >= filters["price_min"])
    if filters.get("price_max"):
        query = query.where(Advertisement.price <= filters["price_max"])
    if filters.get("author_id"):
        query = query.where(Advertisement.author_id == filters["author_id"])
    
    result = await db.execute(query)
    return result.scalars().all()

async def update_advertisement(db: AsyncSession, ad_id: int, ad_data: AdvertisementUpdate):
    ad = await get_advertisement(db, ad_id)
    if not ad:
        return None
    
    if ad_data.title is not None:
        ad.title = ad_data.title
    if ad_data.description is not None:
        ad.description = ad_data.description
    if ad_data.price is not None:
        ad.price = ad_data.price
    
    await db.commit()
    await db.refresh(ad)
    return ad

async def delete_advertisement(db: AsyncSession, ad_id: int):
    ad = await get_advertisement(db, ad_id)
    if not ad:
        return False
    await db.delete(ad)
    await db.commit()
    return True
