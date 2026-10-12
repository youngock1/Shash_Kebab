from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# ---------- USERS ----------
class UserCreate(BaseModel):
    phone: str = Field(..., min_length=5, max_length=20)
    password: str = Field(..., min_length=6)
    full_name: str | None = None


class UserLogin(BaseModel):
    phone: str
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    phone: str
    full_name: str | None
    is_admin: bool
    created_at: datetime


class UserUpdate(BaseModel):
    full_name: str | None = None
    password: str | None = Field(None, min_length=6)


class AdminUserUpdate(UserUpdate):
    is_admin: bool | None = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- CATEGORIES ----------
class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


# ---------- PRODUCTS ----------
class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    price: float = Field(..., ge=0)
    weight: int | None = Field(None, ge=0)
    image_url: str | None = None
    is_available: bool = True
    category_id: int | None = None


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = Field(None, ge=0)
    weight: int | None = Field(None, ge=0)
    image_url: str | None = None
    is_available: bool | None = None
    category_id: int | None = None


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str
    price: float
    weight: int | None
    image_url: str | None
    is_available: bool
    category_id: int | None
    created_at: datetime


# ---------- CAFE INFO ----------
class CafeInfoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    phone: str
    vk_group: str
    address: str
    latitude: float | None
    longitude: float | None
    working_hours: str
    policy: str
    philosophy: str


class CafeInfoUpdate(BaseModel):
    phone: str | None = None
    vk_group: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    working_hours: str | None = None
    policy: str | None = None
    philosophy: str | None = None