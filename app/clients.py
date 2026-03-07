from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.model import Client

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/clients")
def get_clients(db: Session = Depends(get_db)):
    clients = db.query(Client).all()
    return clients