<<<<<<< HEAD
# Shash_Kebab
Internet shop for cafe.
=======
# Шашлычное кафе — FastAPI

Сайт-приложение для шашлычного кафе: информация о кафе, работа с пользователями и управление ассортиментом.

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

После первого запуска автоматически создаются:
- SQLite-база `shashlik.db`
- администратор по умолчанию: **логин** `+70000000000`, **пароль** `admin123` (смените в проде!)
- демо-данные: категории, товары, информация о кафе

## Куда идти

| Что                        | URL                                   |
|----------------------------|---------------------------------------|
| Главная страница           | http://localhost:8000/                |
| Swagger UI (документация)  | http://localhost:8000/docs            |
| ReDoc                      | http://localhost:8000/redoc           |

## Основные эндпоинты

### Информация о кафе
- `GET  /api/info` — публичное чтение
- `PATCH /api/info` — обновление (только админ)

### Пользователи
- `POST /api/auth/register` — регистрация (phone + password)
- `POST /api/auth/login` — вход (OAuth2 password flow, `username = phone`)
- `GET/PATCH/DELETE /api/users/me` — личный кабинет
- `GET /api/users`, `GET/PATCH/DELETE /api/users/{id}` — админ-панель

### Ассортимент
- `GET /api/products`, `GET /api/products/{id}` — публичное чтение
- `GET /api/categories` — категории
- `POST/PATCH/DELETE /api/products` — CRUD (админ)
- `POST/DELETE /api/categories` — управление категориями (админ)

## Авторизация в Swagger

1. `POST /api/auth/login` — ввести `username = телефон`, `password = пароль`.
2. Скопировать `access_token`.
3. Нажать **Authorize** → вставить токен.

## Что можно улучшить (следующие шаги по ТЗ)

- Валидация номера телефона (regex / SMS-подтверждение).
- Система онлайн-заказов.
- Загрузка изображений блюд (S3 / локально).
- Роли и права (не только `is_admin`, но и модераторы).
- Миграции (Alembic) вместо `create_all`.
- Настройка CORS и вынос `SECRET_KEY` в `.env`.
>>>>>>> 2e368a2 (Add project)
