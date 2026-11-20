from math import ceil
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

import auth
import models
import schemas
from database import get_db

router = APIRouter(prefix="/books", tags=["Books"])

SortKey = Literal["newest", "oldest", "title", "author", "rating"]

SORTS = {
    "newest": (models.Book.id.desc(),),
    "oldest": (models.Book.id.asc(),),
    "title": (func.lower(models.Book.title), models.Book.id),
    "author": (func.lower(models.Book.author), func.lower(models.Book.title)),
    "rating": (models.Book.rating.desc().nulls_last(), models.Book.id.desc()),
}


class BookFilters:
    """Спільні параметри для списків: пошук, фільтри, сортування, пагінація."""

    def __init__(
        self,
        q: Optional[str] = Query(None, max_length=100, description="Пошук за назвою, автором або описом"),
        genre: Optional[str] = Query(None, max_length=50),
        author: Optional[str] = Query(None, max_length=120),
        sort: SortKey = "newest",
        page: int = Query(1, ge=1),
        size: int = Query(12, ge=1, le=50),
    ):
        self.q, self.genre, self.author = q, genre, author
        self.sort, self.page, self.size = sort, page, size


def _escape_like(text: str) -> str:
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _paginated(db: Session, f: BookFilters, owner_id: Optional[int] = None) -> dict:
    conditions = []
    if owner_id is not None:
        conditions.append(models.Book.owner_id == owner_id)
    if f.genre:
        conditions.append(func.lower(models.Book.genre) == f.genre.lower())
    if f.author:
        pattern = f"%{_escape_like(f.author.strip())}%"
        conditions.append(models.Book.author.ilike(pattern, escape="\\"))
    if f.q and f.q.strip():
        pattern = f"%{_escape_like(f.q.strip())}%"
        conditions.append(
            models.Book.title.ilike(pattern, escape="\\")
            | models.Book.author.ilike(pattern, escape="\\")
            | models.Book.description.ilike(pattern, escape="\\")
        )

    total = db.scalar(select(func.count(models.Book.id)).where(*conditions)) or 0
    items = db.scalars(
        select(models.Book)
        .where(*conditions)
        .order_by(*SORTS[f.sort])
        .offset((f.page - 1) * f.size)
        .limit(f.size)
    ).all()
    return {
        "items": items,
        "total": total,
        "page": f.page,
        "size": f.size,
        "pages": max(1, ceil(total / f.size)),
    }


def _get_owned_book(db: Session, book_id: int, user: models.User) -> models.Book:
    book = db.get(models.Book, book_id)
    if book is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Книгу не знайдено")
    if book.owner_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Це не твоя книга")
    return book


@router.get("/", response_model=schemas.BookPage, summary="Усі книги (публічно)")
def get_all_books(filters: BookFilters = Depends(), db: Session = Depends(get_db)):
    return _paginated(db, filters)


@router.get("/my", response_model=schemas.BookPage, summary="Мої книги")
def get_my_books(
    filters: BookFilters = Depends(),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return _paginated(db, filters, owner_id=current_user.id)


@router.get("/genres", response_model=List[str], summary="Список жанрів")
def get_genres(db: Session = Depends(get_db)):
    rows = db.scalars(
        select(models.Book.genre)
        .where(models.Book.genre.is_not(None))
        .distinct()
        .order_by(models.Book.genre)
    )
    return list(rows)


@router.get("/stats", response_model=schemas.Stats, summary="Статистика бібліотеки")
def get_stats(db: Session = Depends(get_db)):
    top = db.execute(
        select(models.Book.author, func.count(models.Book.id))
        .group_by(models.Book.author)
        .order_by(func.count(models.Book.id).desc(), models.Book.author)
        .limit(5)
    ).all()
    avg = db.scalar(select(func.avg(models.Book.rating)))
    return {
        "books": db.scalar(select(func.count(models.Book.id))) or 0,
        "authors": db.scalar(select(func.count(func.distinct(func.lower(models.Book.author))))) or 0,
        "users": db.scalar(select(func.count(models.User.id))) or 0,
        "avg_rating": round(avg, 2) if avg is not None else None,
        "top_authors": [{"author": a, "books": n} for a, n in top],
    }


@router.post(
    "/",
    response_model=schemas.BookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Додати книгу",
)
def create_book(
    book_data: schemas.BookCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    new_book = models.Book(**book_data.model_dump(), owner_id=current_user.id)
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book


@router.get("/{book_id}", response_model=schemas.BookResponse, summary="Одна книга")
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.get(models.Book, book_id)
    if book is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Книгу не знайдено")
    return book


@router.patch("/{book_id}", response_model=schemas.BookResponse, summary="Редагувати свою книгу")
def update_book(
    book_id: int,
    changes: schemas.BookUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    book = _get_owned_book(db, book_id, current_user)
    for field, value in changes.model_dump(exclude_unset=True).items():
        setattr(book, field, value)
    db.commit()
    db.refresh(book)
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Видалити свою книгу")
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    book = _get_owned_book(db, book_id, current_user)
    db.delete(book)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
