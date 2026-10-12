from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_admin
from ..models import CafeInfo, User
from ..schemas import CafeInfoRead, CafeInfoUpdate

router = APIRouter(prefix="/api/info", tags=["Информация о кафе"])


def _get_or_create(db: Session) -> CafeInfo:
    info = db.query(CafeInfo).first()
    if not info:
        info = CafeInfo()
        db.add(info)
        db.commit()
        db.refresh(info)
    return info


@router.get("", response_model=CafeInfoRead)
def get_info(db: Session = Depends(get_db)):
    """Публичное чтение: контакты, адрес, политика, философия."""
    return _get_or_create(db)


@router.patch("", response_model=CafeInfoRead)
def update_info(
    data: CafeInfoUpdate,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    info = _get_or_create(db)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(info, key, value)
    db.commit()
    db.refresh(info)
    return info