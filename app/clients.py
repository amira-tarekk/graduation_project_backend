from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import SessionLocal
from app.model import Client
from app.schema import ClientCreate

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
@router.post("/clients")
def create_client(
    data: ClientCreate,
    db: Session = Depends(get_db)
):
    print("CLIENT ID:", data.client_id)
    print("NAME:", data.name)
    print("PHONE:", data.phone)
    print("EMAIL:", data.email)

    existing_client = db.query(Client).filter(
        Client.client_id == data.client_id
    ).first()

    if existing_client:
        return {
            "message": "Client already exists",
            "client_id": existing_client.client_id
        }

    client = Client(
        client_id=data.client_id,
        name=data.name,
        phone=data.phone,
        email=data.email,
        branch="Cairo",
        status="Active"
    )

    db.add(client)
    db.commit()
    db.refresh(client)

    return {
        "message": "Client created",
        "client_id": client.client_id
    }     
        


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