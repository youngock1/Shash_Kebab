from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_admin
from ..models import Category, Product, User
from ..schemas import (
    CategoryCreate,
    CategoryRead,
    ProductCreate,
    ProductRead,
    ProductUpdate,
)

router = APIRouter(prefix="/api", tags=["Ассортимент"])


# ---------- Публичное чтение ----------
@router.get("/products", response_model=list[ProductRead])
def list_products(
    category_id: int | None = Query(None, description="Фильтр по категории"),
    only_available: bool = Query(True, description="Показывать только в наличии"),
    search: str | None = Query(None, description="Поиск по названию"),
    db: Session = Depends(get_db),
):
    q = db.query(Product)
    if only_available:
        q = q.filter(Product.is_available.is_(True))
    if category_id is not None:
        q = q.filter(Product.category_id == category_id)
    if search:
        q = q.filter(Product.name.ilike(f"%{search}%"))
    return q.order_by(Product.id).all()


@router.get("/products/{product_id}", response_model=ProductRead)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Товар не найден")
    return product


@router.get("/categories", response_model=list[CategoryRead])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).order_by(Category.id).all()


# ---------- Admin CRUD ----------
@router.post("/categories", response_model=CategoryRead, status_code=201)
def create_category(
    data: CategoryCreate,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if db.query(Category).filter(Category.name == data.name).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Категория уже существует")
    cat = Category(name=data.name)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.delete("/categories/{category_id}", status_code=204)
def delete_category(
    category_id: int,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    cat = db.get(Category, category_id)
    if not cat:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Категория не найдена")
    db.delete(cat)
    db.commit()


@router.post("/products", response_model=ProductRead, status_code=201)
def create_product(
    data: ProductCreate,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if data.category_id is not None and not db.get(Category, data.category_id):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Указанная категория не существует")

    product = Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.patch("/products/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int,
    data: ProductUpdate,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Товар не найден")

    payload = data.model_dump(exclude_unset=True)
    if "category_id" in payload and payload["category_id"] is not None:
        if not db.get(Category, payload["category_id"]):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Указанная категория не существует")

    for key, value in payload.items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product


@router.delete("/products/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Товар не найден")
    db.delete(product)
    db.commit()