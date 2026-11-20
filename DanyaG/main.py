from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

import models
from database import engine, SessionLocal, get_db
from routers import auth_router, products_router

def seed_initial_products():
    db = SessionLocal()
    try:
        if db.query(models.Product).count() == 0:
            initial_products = [
                models.Product(
                    title="Хлеб пшеничный",
                    category="Выпечка",
                    price=25.0,
                    in_stock=True,
                    description="Свежий ароматный хлеб из пекарни"
                ),
                models.Product(
                    title="Мясо (свинина / говядина)",
                    category="Мясной отдел",
                    price=210.0,
                    in_stock=True,
                    description="Охлажденное фермерское мясо, 1 кг"
                ),
                models.Product(
                    title="Яйца куриные (10 шт.)",
                    category="Фермерские продукты",
                    price=65.0,
                    in_stock=True,
                    description="Домашние отборные яйца категории С0"
                ),
            ]
            db.add_all(initial_products)
            db.commit()
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=engine)
    seed_initial_products()
    yield

app = FastAPI(
    title="Store API (SAT_18)",
    description="Магазин основных продуктов питания",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(auth_router.router)
app.include_router(products_router.router)

def render_store_html(products):
    cards_html = ""
    for p in products:
        cards_html += f"""
        <div style="border: 1px solid #e0e0e0; border-radius: 12px; padding: 18px; width: 250px; background: #fff; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
            <div style="font-size: 12px; color: #777; margin-bottom: 6px;">{p.category}</div>
            <h3 style="margin: 0 0 8px 0; color: #222;">{p.title}</h3>
            <p style="color: #555; font-size: 14px; min-height: 38px;">{p.description or ''}</p>
            <p style="font-weight: bold; font-size: 20px; color: #111; margin: 12px 0;">{p.price} грн</p>
            <span style="background: #e6f4ea; color: #137333; padding: 5px 10px; border-radius: 6px; font-size: 12px; font-weight: bold;">
                ● В наличии
            </span>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Магазин продуктов — В наличии</title>
    </head>
    <body style="font-family: 'Segoe UI', Arial, sans-serif; background: #f8f9fa; max-width: 920px; margin: 40px auto; padding: 0 20px;">
        <h1 style="color: #202124;">Основные товары в наличии</h1>
        <div style="display: flex; gap: 20px; flex-wrap: wrap; margin-top: 24px;">
            {cards_html}
        </div>
        <p style="margin-top: 32px; color: #666; font-size: 14px;">
            Swagger UI: <a href="/docs">/docs</a> | API товаров (JSON): <a href="/products/">/products/</a>
        </p>
    </body>
    </html>
    """

@app.get("/", response_class=HTMLResponse)
@app.get("/admin", response_class=HTMLResponse)
def root(db: Session = Depends(get_db)):
    products = db.query(models.Product).filter(models.Product.in_stock == True).all()
    return render_store_html(products)
