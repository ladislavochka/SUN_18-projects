from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Author
from database.schemas import AuthorCreate, AuthorResponse

router = APIRouter(prefix="/authors", tags=["Автори"])

@router.post("/", response_model=AuthorResponse)
def create_author(data: AuthorCreate, db: Session = Depends(get_db)):
    if db.query(Author).filter_by(name=data.name).first():
        raise HTTPException(400, "Автор уже існує")
    obj = Author(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/", response_model=list[AuthorResponse])
def get_authors(db: Session = Depends(get_db)):
    return db.query(Author).order_by(Author.id).all()

@router.get("/{author_id}", response_model=AuthorResponse)
def get_author(author_id: int, db: Session = Depends(get_db)):
    obj = db.query(Author).filter_by(id=author_id).first()
    if not obj:
        raise HTTPException(404, "Автора не знайдено")
    return obj

@router.put("/{author_id}", response_model=AuthorResponse)
def update_author(author_id: int, data: AuthorCreate, db: Session = Depends(get_db)):
    obj = db.query(Author).filter_by(id=author_id).first()
    if not obj:
        raise HTTPException(404, "Автора не знайдено")
    for key, value in data.model_dump().items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{author_id}")
def delete_author(author_id: int, db: Session = Depends(get_db)):
    obj = db.query(Author).filter_by(id=author_id).first()
    if not obj:
        raise HTTPException(404, "Автора не знайдено")
    if obj.books:
        raise HTTPException(400, "Не можна видалити автора, у якого є книги")
    db.delete(obj)
    db.commit()
    return {"message": "Автора видалено"}
