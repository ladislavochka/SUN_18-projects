from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Book, Author, Publisher, Genre
from database.schemas import BookCreate, BookResponse
from auth import get_current_user

router = APIRouter(prefix="/books", tags=["Книги"])

@router.post("/", response_model=BookResponse)
def create_book(data: BookCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if not db.query(Author).filter_by(id=data.author_id).first():
        raise HTTPException(404, "Автора не знайдено")
    if data.publisher_id and not db.query(Publisher).filter_by(id=data.publisher_id).first():
        raise HTTPException(404, "Видавництво не знайдено")
    genres = db.query(Genre).filter(Genre.id.in_(data.genre_ids)).all() if data.genre_ids else []
    if len(genres) != len(set(data.genre_ids)):
        raise HTTPException(404, "Жанр не знайдено")
    values = data.model_dump(exclude={"genre_ids"})
    obj = Book(**values, genres=genres)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/", response_model=list[BookResponse])
def get_books(db: Session = Depends(get_db)):
    return db.query(Book).order_by(Book.id).all()

@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    obj = db.query(Book).filter_by(id=book_id).first()
    if not obj:
        raise HTTPException(404, "Книгу не знайдено")
    return obj

@router.put("/{book_id}", response_model=BookResponse)
def update_book(book_id: int, data: BookCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = db.query(Book).filter_by(id=book_id).first()
    if not obj:
        raise HTTPException(404, "Книгу не знайдено")
    if not db.query(Author).filter_by(id=data.author_id).first():
        raise HTTPException(404, "Автора не знайдено")
    if data.publisher_id and not db.query(Publisher).filter_by(id=data.publisher_id).first():
        raise HTTPException(404, "Видавництво не знайдено")
    genres = db.query(Genre).filter(Genre.id.in_(data.genre_ids)).all() if data.genre_ids else []
    if len(genres) != len(set(data.genre_ids)):
        raise HTTPException(404, "Жанр не знайдено")
    for key, value in data.model_dump(exclude={"genre_ids"}).items():
        setattr(obj, key, value)
    obj.genres = genres
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = db.query(Book).filter_by(id=book_id).first()
    if not obj:
        raise HTTPException(404, "Книгу не знайдено")
    if obj.borrowings:
        raise HTTPException(400, "Не можна видалити книгу, для якої є записи про видачу")
    db.delete(obj)
    db.commit()
    return {"message": "Книгу видалено"}
