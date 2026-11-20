from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Genre
from database.schemas import GenreCreate, GenreResponse

router = APIRouter(prefix="/genres", tags=["Genres"])

@router.post("/", response_model=GenreResponse)
def create_genre(data: GenreCreate, db: Session = Depends(get_db)):
    if db.query(Genre).filter_by(name=data.name).first():
        raise HTTPException(400, "Genre already exists")
    obj = Genre(name=data.name); db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.get("/", response_model=list[GenreResponse])
def get_genres(db: Session = Depends(get_db)):
    return db.query(Genre).order_by(Genre.id).all()
