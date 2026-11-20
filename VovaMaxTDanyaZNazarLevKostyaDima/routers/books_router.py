from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
import auth
from database import get_db

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("/", response_model=List[schemas.BookResponse])
def get_all_books(db: Session = Depends(get_db)):
    """Публічний ендпоінт: отримати список усіх книг."""
    return db.query(models.Book).all()


@router.post("/", response_model=schemas.BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(
    book_data: schemas.BookCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Захищений ендпоінт: додати нову книгу від імені авторизованого користувача."""
    new_book = models.Book(**book_data.model_dump(), owner_id=current_user.id)
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book


@router.get("/my", response_model=List[schemas.BookResponse])
def get_my_books(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Захищений ендпоінт: переглянути тільки власні додані книги."""
    return db.query(models.Book).filter(models.Book.owner_id == current_user.id).all()