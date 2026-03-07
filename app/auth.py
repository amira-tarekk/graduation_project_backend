from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.database import SessionLocal
from app.model import Employee
from app.schema import Login

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login")
def login(data: Login, db: Session = Depends(get_db)):

    employee = db.query(Employee).filter(
        Employee.employee_id == data.employee_id
    ).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    if data.password_hash != employee.password_hash:
     raise HTTPException(status_code=401, detail="Wrong password")

    return {"message": "Login successful"}