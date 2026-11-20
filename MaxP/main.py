from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import models
from config import BASE_DIR, CORS_ORIGINS
from database import engine, upgrade_schema
from routers import auth_router, books_router

STATIC_DIR = BASE_DIR / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=engine)
    upgrade_schema()
    yield


app = FastAPI(
    title="Полиця: Books API",
    description=(
        "Бібліотека книг із авторизацією через JWT.\n\n"
        "- Перегляд, пошук і статистика доступні всім.\n"
        "- Додавати, редагувати й видаляти книги можуть зареєстровані користувачі (лише свої).\n"
        "- Для кнопки **Authorize** вгорі вводь ім'я користувача (або email) і пароль."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(books_router.router)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health", tags=["Service"], summary="Перевірка стану")
def health():
    return {"status": "ok"}
