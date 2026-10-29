from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from models.user import Base as UserBase, UserModel
from routers import auth
from dependencies import get_current_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(UserBase.metadata.create_all)
    yield


app = FastAPI(title='Shash-Kebab API', version='1.0', lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:5501",
        "http://localhost:5501",
        "http://127.0.0.1:8888",
        "http://localhost:8888",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(auth.router)


@app.get('/users/me')
async def current_user_information(current_user: UserModel = Depends(get_current_user)):
    return {
        'id': current_user.id,
        'username': current_user.username,
        'created_at': current_user.created_at,
    }
