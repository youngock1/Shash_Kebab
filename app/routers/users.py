from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_admin, get_current_user
from ..models import User
from ..schemas import AdminUserUpdate, UserRead, UserUpdate
from ..security import hash_password

router = APIRouter(prefix="/api/users", tags=["Пользователи"])


# ---------- Личный кабинет ----------
@router.get("/me", response_model=UserRead)
def get_me(user: User = Depends(get_current_user)):
    return user


@router.patch("/me", response_model=UserRead)
def update_me(
    data: UserUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if data.full_name is not None:
        user.full_name = data.full_name
    if data.password:
        user.hashed_password = hash_password(data.password)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/me", status_code=204)
def delete_me(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db.delete(user)
    db.commit()


# ---------- Админ-панель ----------
@router.get("", response_model=list[UserRead])
def list_users(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return db.query(User).order_by(User.id).all()


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Пользователь не найден")
    return user


@router.patch("/{user_id}", response_model=UserRead)
def admin_update_user(
    user_id: int,
    data: AdminUserUpdate,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Пользователь не найден")

    if data.full_name is not None:
        user.full_name = data.full_name
    if data.password:
        user.hashed_password = hash_password(data.password)
    if data.is_admin is not None:
        user.is_admin = data.is_admin

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=204)
def admin_delete_user(
    user_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Пользователь не найден")
    if user.id == admin.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Нельзя удалить собственный аккаунт")
    db.delete(user)
    db.commit()