from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.model import DealApplication


router = APIRouter()


class DealRecordRequest(BaseModel):
    employee_id: str
    customer_name: Optional[str] = "Unknown Customer"
    product_name: Optional[str] = "Unknown Product"
    amount: Optional[float] = 0
    model_type: Optional[str] = None
    risk_level: Optional[str] = None


@router.post("/deals/record")
def record_new_deal(
    data: DealRecordRequest,
    db: Session = Depends(get_db)
):
    deal = DealApplication(
        employee_id=data.employee_id,
        customer_name=data.customer_name,
        product_name=data.product_name,
        amount=data.amount,
        model_type=data.model_type,
        risk_level=data.risk_level,
        status="Initiated"
    )

    db.add(deal)
    db.commit()
    db.refresh(deal)

    return {
        "message": "Deal recorded",
        "deal_id": deal.id
    }