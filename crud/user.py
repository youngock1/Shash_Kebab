from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import UserCreate
from models.user import UserModel
from utils import get_password_hash, verify_password


async def create_user(db: AsyncSession, user_data: UserCreate):
    hashed_passsword = get_password_hash(user_data.password)
    db_user = UserModel(
        username=user_data.username,
        hashed_password=hashed_passsword
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user_by_username(db: AsyncSession, username: str):
    query = select(UserModel).where(UserModel.username == username)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
