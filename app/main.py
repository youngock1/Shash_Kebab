from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .database import Base, SessionLocal, engine
from .models import CafeInfo, Category, Product, User
from .routers import auth, info, products, users
from .security import hash_password

# --- Инициализация БД ---
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Шашлычное кафе — API",
    description="Сайт-приложение шашлычного кафе: информация, ассортимент, пользователи.",
    version="1.0.0",
)

# --- Роутеры ---
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(info.router)

# --- Шаблоны ---
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse, tags=["UI"])
def index(request: Request):
    """Главная страница — информация о кафе + превью ассортимента."""
    return templates.TemplateResponse(
        "index.html",
        {"request": request},
    )


# --- Сидирование при первом запуске ---
def seed_data() -> None:
    db = SessionLocal()
    try:
        # Администратор по умолчанию
        if not db.query(User).filter(User.is_admin.is_(True)).first():
            admin = User(
                phone="+70000000000",
                hashed_password=hash_password("admin123"),
                full_name="Администратор",
                is_admin=True,
            )
            db.add(admin)

        # Информация о кафе
        if not db.query(CafeInfo).first():
            db.add(
                CafeInfo(
                    phone="+7 (900) 000-00-00",
                    vk_group="https://vk.com/shashlik_cafe",
                    address="г. Малый, ул. Центральная, д. 1",
                    latitude=55.7558,
                    longitude=37.6176,
                    working_hours="Ежедневно с 10:00 до 22:00",
                    policy=(
                        "Мы работаем честно: только свежее мясо, маринуем сами, "
                        "готовим на живом угле. Бронируем столики по телефону. "
                        "Принимаем возвраты в течение 15 минут после подачи блюда."
                    ),
                    philosophy=(
                        "Шашлык — это не просто еда, а повод собраться. "
                        "Мы верим в простые вещи: хорошее мясо, правильный уголь "
                        "и тёплая компания. Наша кухня — душа города."
                    ),
                )
            )

        # Категории и товары
        if not db.query(Category).first():
            cats = {
                "Шашлыки": Category(name="Шашлыки"),
                "Гарниры": Category(name="Гарниры"),
                "Напитки": Category(name="Напитки"),
            }
            db.add_all(cats.values())
            db.flush()

            db.add_all(
                [
                    Product(
                        name="Шашлык из свиной шеи",
                        description="Сочная шея, маринад с луком и специями, подаём с лавашом.",
                        price=450.0,
                        weight=250,
                        is_available=True,
                        category_id=cats["Шашлыки"].id,
                    ),
                    Product(
                        name="Шашлык из курицы",
                        description="Куриное филе в йогуртовом маринаде.",
                        price=320.0,
                        weight=220,
                        is_available=True,
                        category_id=cats["Шашлыки"].id,
                    ),
                    Product(
                        name="Картофель по-деревенски",
                        description="Запечённый картофель с паприкой и чесноком.",
                        price=180.0,
                        weight=200,
                        is_available=True,
                        category_id=cats["Гарниры"].id,
                    ),
                    Product(
                        name="Морс клюквенный",
                        description="Домашний морс, без сахара.",
                        price=120.0,
                        weight=400,
                        is_available=True,
                        category_id=cats["Напитки"].id,
                    ),
                ]
            )

        db.commit()
    finally:
        db.close()


@app.on_event("startup")
def on_startup() -> None:
    seed_data()