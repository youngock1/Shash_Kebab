from fastapi import APIRouter, status, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from schemas.user import UserCreate
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
import crud.user as crud
from utils import create_access_token, COOKIE_NAME, ACCESS_TOKEN_EXPIRE_MINUTES
from dependencies import get_current_user


router = APIRouter(
    prefix='/auth',
    tags=['Users'],
    responses={404: {'description': 'Not found'}},
)


@router.post('/register', status_code=status.HTTP_201_CREATED)
async def user_registration(user_s: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await crud.get_user_by_username(db, user_s.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    user = await crud.create_user(db, user_s)
    return user


@router.post('/login')
async def login(
    response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    user = await crud.authenticate_user(db, form_data.username, form_data.password)
    if user == None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = create_access_token(data={'sub': user.username})
    response.set_cookie(
        key=COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=False,
        samesite='lax',
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES*60
    )
    return {'message': 'Login successful'}


@router.post('/logout')
def logout(response: Response, current_user: dict = Depends(get_current_user)):
    response.delete_cookie(COOKIE_NAME)
    return {'message': 'Logged out'}
