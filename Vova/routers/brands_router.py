from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models
import schemas
import auth
from database import get_db

router = APIRouter(prefix="/brands", tags=["Brands"])

@router.get("/", response_model=List[schemas.BrandResponse])
def get_all_brands(db: Session = Depends(get_db)):
    """Публічний список усіх виробників."""
    return db.query(models.Brand).order_by(models.Brand.name).all()

@router.post("/", response_model=schemas.BrandResponse,
             status_code=status.HTTP_201_CREATED)
def create_brand(
    brand_data: schemas.BrandCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Додати виробника може лише авторизований користувач."""
    existing = db.query(models.Brand).filter(
        models.Brand.name == brand_data.name
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Такий виробник уже існує",
        )
    brand = models.Brand(**brand_data.model_dump())
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return brand

@router.get("/{brand_id}", response_model=schemas.BrandResponse)
def get_brand(brand_id: int, db: Session = Depends(get_db)):
    brand = db.query(models.Brand).filter(
        models.Brand.id == brand_id
    ).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Виробника не знайдено")
    return brand
