from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Reader
from database.schemas import ReaderCreate, ReaderResponse

router = APIRouter(prefix="/readers", tags=["Readers"])

@router.post("/", response_model=ReaderResponse)
def create_reader(data: ReaderCreate, db: Session = Depends(get_db)):
    if db.query(Reader).filter_by(email=str(data.email)).first():
        raise HTTPException(400, "Reader email already exists")
    obj = Reader(**data.model_dump()); db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.get("/", response_model=list[ReaderResponse])
def get_readers(db: Session = Depends(get_db)):
    return db.query(Reader).order_by(Reader.id).all()
