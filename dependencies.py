from typing import Optional
from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from utils import decode_token
from database import get_db
import crud.user as crud


async def get_current_user(
    access_token: Optional[str] = Cookie(None),
    db: AsyncSession = Depends(get_db)
):
    exception_e = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials'
    )
    if not access_token:
        raise exception_e
    payload = decode_token(access_token)
    if not payload:
        raise exception_e
    username = payload.get('sub')
    if not username:
        raise exception_e
    user = await crud.get_user_by_username(db, username)
    if not user:
        raise exception_e
    return user
