from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Publisher
from database.schemas import PublisherCreate, PublisherResponse

router = APIRouter(prefix="/publishers", tags=["Publishers"])

@router.post("/", response_model=PublisherResponse)
def create_publisher(data: PublisherCreate, db: Session = Depends(get_db)):
    if db.query(Publisher).filter_by(name=data.name).first():
        raise HTTPException(400, "Publisher already exists")
    obj = Publisher(**data.model_dump()); db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.get("/", response_model=list[PublisherResponse])
def get_publishers(db: Session = Depends(get_db)):
    return db.query(Publisher).order_by(Publisher.id).all()
