from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_

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
def get_clients(search: str = "", db: Session = Depends(get_db)):

    query = db.query(Client)

    if search:
        query = query.filter(
            or_(
                Client.name.ilike(f"%{search}%"),
                Client.client_id.ilike(f"%{search}%")
            )
        )

    clients = query.order_by(Client.id.desc()).all()

    return [
        {
            "id": client.id,
            "client_id": client.client_id,
            "name": client.name,
            "branch": client.branch,
            "status": client.status,
        }
        for client in clients
    ]