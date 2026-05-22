from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime
from app.activity_logger import record_admin_activity
from app.database import SessionLocal
from app.model import Employee
from app.model import EmployeeLogin
from app.model import Admin
from app.schema import Login
from app.schema import AdminLogin


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

    employee.last_login = datetime.now()

    login_record = EmployeeLogin(
        employee_id=employee.employee_id
    )

    db.add(login_record)
    db.commit()

    return {"message": "Login successful"}


@router.post("/admin-login")
def admin_login(data: AdminLogin, db: Session = Depends(get_db)):

    admin_id = db.query(Admin).filter(
        Admin.admin_id == data.admin_id
    ).first()

    if not admin_id:
        raise HTTPException(status_code=404, detail="Admin not found")

    if admin_id.password != data.password:
        raise HTTPException(status_code=401, detail="Wrong password")
    
    record_admin_activity(
    db=db,
    admin_id=data.admin_id,
    action="Admin Logged In",
    target_type="Admin",
    target_name=data.admin_id
)

    return {"message": "Admin login successful"}