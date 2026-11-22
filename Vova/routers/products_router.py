from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
import models
import schemas
import auth
from database import get_db

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("/", response_model=List[schemas.ProductResponse])
def get_all_products(db: Session = Depends(get_db)):
    """Публічний список продуктів разом із даними виробника."""
    return (
        db.query(models.Product)
        .options(joinedload(models.Product.brand))
        .order_by(models.Product.id)
        .all()
    )

@router.post("/", response_model=schemas.ProductResponse,
             status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Додати продукт може лише авторизований користувач."""
    brand = db.query(models.Brand).filter(
        models.Brand.id == product_data.brand_id
    ).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Виробника не знайдено")

    product = models.Product(
        **product_data.model_dump(),
        owner_id=current_user.id,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.get("/my", response_model=List[schemas.ProductResponse])
def get_my_products(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Показати продукти, додані поточним користувачем."""
    return (
        db.query(models.Product)
        .options(joinedload(models.Product.brand))
        .filter(models.Product.owner_id == current_user.id)
        .all()
    )

@router.get("/{product_id}", response_model=schemas.ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = (
        db.query(models.Product)
        .options(joinedload(models.Product.brand))
        .filter(models.Product.id == product_id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Продукт не знайдено")
    return product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    product = db.query(models.Product).filter(
        models.Product.id == product_id,
        models.Product.owner_id == current_user.id,
    ).first()
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Продукт не знайдено або він належить іншому користувачу",
        )
    db.delete(product)
    db.commit()
