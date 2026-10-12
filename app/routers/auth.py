from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import Token, UserCreate, UserRead
from ..security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["Авторизация"])


@router.post("/register", response_model=UserRead, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    """
    Регистрация по номеру телефона и паролю.
    Проверка корректности номера пока не выполняется (по ТЗ), но поле валидируется по длине.
    """
    exists = db.query(User).filter(User.phone == data.phone).first()
    if exists:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Этот номер телефона уже зарегистрирован")

    user = User(
        phone=data.phone,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Вход: в поле `username` нужно передать номер телефона, в `password` — пароль.
    Совместимо со Swagger UI и любым OAuth2-клиентом.
    """
    user = db.query(User).filter(User.phone == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Неверный номер телефона или пароль")

    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token)