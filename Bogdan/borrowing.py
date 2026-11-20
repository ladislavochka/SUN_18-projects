from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Borrowing, Book, Reader
from database.schemas import BorrowingCreate, BorrowingResponse

router = APIRouter(prefix="/borrowings", tags=["Видача книг"])

@router.post("/", response_model=BorrowingResponse)
def create_borrowing(data: BorrowingCreate, db: Session = Depends(get_db)):
    if not db.query(Book).filter_by(id=data.book_id).first():
        raise HTTPException(404, "Книгу не знайдено")
    if not db.query(Reader).filter_by(id=data.reader_id).first():
        raise HTTPException(404, "Читача не знайдено")
    active = db.query(Borrowing).filter_by(book_id=data.book_id, returned_at=None).first()
    if active:
        raise HTTPException(400, "Ця книга вже видана")
    obj = Borrowing(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/", response_model=list[BorrowingResponse])
def get_borrowings(db: Session = Depends(get_db)):
    return db.query(Borrowing).order_by(Borrowing.id).all()

@router.put("/{borrowing_id}/return", response_model=BorrowingResponse)
def return_book(borrowing_id: int, db: Session = Depends(get_db)):
    obj = db.query(Borrowing).filter_by(id=borrowing_id).first()
    if not obj:
        raise HTTPException(404, "Запис про видачу не знайдено")
    if obj.returned_at is not None:
        raise HTTPException(400, "Книгу вже повернули")
    obj.returned_at = datetime.utcnow()
    db.commit()
    db.refresh(obj)
    return obj
