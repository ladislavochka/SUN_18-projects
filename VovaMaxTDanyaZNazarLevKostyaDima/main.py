from fastapi import FastAPI
import models
from database import engine
from routers import auth_router, books_router

models.Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="Books storeAPI",
    description="Books",
    version="1.0.0",
)
app.include_router(auth_router.router)
app.include_router(books_router.router)
@app.get("/")
def root():
    return {"message": "Welcome"}