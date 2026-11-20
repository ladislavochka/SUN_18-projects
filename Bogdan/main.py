from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from database.database import Base, engine, migrate_database
from author import router as author_router
from book import router as book_router
from genre import router as genre_router
from publisher import router as publisher_router
from reader import router as reader_router
from borrowing import router as borrowing_router
from admin import router as admin_router
from auth import router as auth_router
from images import router as images_router

Base.metadata.create_all(bind=engine)
migrate_database()

app = FastAPI(
    title="Система керування бібліотекою",
    description="API бібліотеки з реєстрацією, авторизацією та адмін-панеллю",
    version="1.1.0",
    docs_url="/admin/docs",
    redoc_url="/admin/redoc",
    openapi_url="/admin/openapi.json",
)

for router in [author_router, book_router, genre_router, publisher_router,
               reader_router, borrowing_router, auth_router, images_router]:
    app.include_router(router)
app.include_router(admin_router)
app.mount("/uploads", StaticFiles(directory="uploads", check_dir=False), name="uploads")

@app.get("/")
def home():
    return {"message": "Система керування бібліотекою працює"}
