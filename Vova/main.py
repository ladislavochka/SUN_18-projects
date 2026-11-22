from fastapi import FastAPI
import models
from database import engine
from routers import auth_router, products_router, brands_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Products and Brands API",
    description="API для обліку продуктів та їхніх виробників",
    version="1.0.0",
)

app.include_router(auth_router.router)
app.include_router(brands_router.router)
app.include_router(products_router.router)

@app.get("/")
def root():
    return {"message": "Ласкаво просимо до API продуктів і виробників!"}
