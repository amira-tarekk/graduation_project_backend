from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.model import DealApplication
from app.model import Client
from app.model import ClientFollowUp

from app.schema import FollowUpRequest

router = APIRouter()


@router.get("/contact-client/{deal_id}")
def get_contact_client(
    deal_id: int,
    db: Session = Depends(get_db)
):
    deal = db.query(DealApplication).filter(
        DealApplication.id == deal_id
    ).first()

    if not deal:
        return {"error": "Deal not found"}

    client = db.query(Client).filter(
        Client.client_id == deal.client_id
    ).first()

    if not client:
     return {
        "deal_id": deal.id,
        "client_name": "New Client",
        "client_id": "",
        "phone": "",
        "email": "",
        "product_name": deal.product_name,
        "status": deal.status,
        "employee_id": deal.employee_id
    }

    return {
        "deal_id": deal.id,
        "client_name": client.name,
        "client_id": client.client_id,
        "phone": client.phone,
        "email": client.email,
        "product_name": deal.product_name,
        "status": deal.status,
        "employee_id": deal.employee_id
    }
    
    
    
@router.post("/followup/save")
def save_followup(
    data: FollowUpRequest,
    db: Session = Depends(get_db)
):

    deal = db.query(DealApplication).filter(
        DealApplication.id == data.deal_id
    ).first()

    if not deal:
        return {"error": "Deal not found"}

    followup = ClientFollowUp(
        deal_id=data.deal_id,
        employee_id=data.employee_id,
        client_id=deal.client_id,
        contact_method=data.contact_method,
        contact_outcome=data.contact_outcome,
        application_status=data.application_status,
        notes=data.notes
    )

    db.add(followup)

    deal.status = data.application_status

    db.commit()

    return {
        "message": "Follow-up saved successfully"
    }   
    
    
@router.get("/client-history/{client_id}")
def get_client_history(
    client_id: str,
    db: Session = Depends(get_db)
):
    history = db.query(ClientFollowUp).filter(
        ClientFollowUp.client_id == client_id
    ).order_by(
        ClientFollowUp.created_at.desc()
    ).all()

    return history    
