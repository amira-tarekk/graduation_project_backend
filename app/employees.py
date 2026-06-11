from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from fastapi import HTTPException
from app.activity_logger import record_admin_activity
from app.database import SessionLocal
from app.model import Admin, AdminActivityLog, Employee
from app.schema import EmployeeCreate
from app.schema import EmployeeUpdate
from app.schema import ResetPasswordRequest
import secrets
import string

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/employees")
def get_employees(search: str = "", db: Session = Depends(get_db)):

    query = db.query(Employee)

    if search:
     query = query.filter(
        or_(
            Employee.full_name.ilike(f"%{search}%"),
            Employee.employee_id.ilike(f"%{search}%")
        )
    )

    employees = query.order_by(Employee.id.desc()).all()

    return [
        {
            "id": emp.id,
            "employee_id": emp.employee_id,
            "full_name": emp.full_name,
            "email": emp.email,
            "branch": emp.branch,
            "status": emp.status,
        }
        for emp in employees
    ]


@router.post("/employees")
def create_employee(data: EmployeeCreate, db: Session = Depends(get_db)):

    new_employee = Employee(
        employee_id=data.employee_id,
        password_hash=data.password_hash,
        status="Inactive",
        branch=data.branch,
        full_name=data.full_name,
        email=data.email
    )

    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    record_admin_activity(
    db=db,
    action="Account Created",
    target_type="Employee",
    target_name=data.full_name,
    employee_id=data.employee_id
)

    return {
        "message": "Employee created",
        "employee": {
            "id": new_employee.id,
            "employee_id": new_employee.employee_id,
            "full_name": new_employee.full_name,
            "email": new_employee.email,
            "branch": new_employee.branch,
            "status": new_employee.status,
        }
    }
    
@router.get("/employees/{employee_id}/activity-log")
def get_employee_activity_log(employee_id: str, db: Session = Depends(get_db)):
    logs = db.query(AdminActivityLog).filter(
        AdminActivityLog.employee_id == employee_id
    ).order_by(
        AdminActivityLog.created_at.desc()
    ).all()

    return [
        {
            "id": log.id,
            "action": log.action,
            "admin_name": log.admin_name or "John Administrator",
            "target_name": log.target_name,
            "employee_id": log.employee_id,
            "created_at": log.created_at.strftime("%b %d, %Y") if log.created_at else ""
        }
        for log in logs
    ]    


@router.put("/employees/{employee_id}")
def update_employee(employee_id: str, data: EmployeeUpdate, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()

    if not emp:
        return {"error": "Employee not found"}

    old_full_name = emp.full_name
    old_email = emp.email
    old_branch = emp.branch
    old_status = emp.status

    emp.full_name = data.full_name
    emp.email = data.email
    emp.branch = data.branch
    emp.status = data.status

    db.commit()

    if old_status != data.status:
        if data.status == "Inactive":
            action_name = "Account Deactivated"
        elif data.status == "Active":
            action_name = "Account Activated"
        else:
            action_name = "Account Status Updated"
    elif old_full_name != data.full_name:
        action_name = "Employee Name Updated"
    elif old_email != data.email:
        action_name = "Employee Email Updated"
    elif old_branch != data.branch:
        action_name = "Employee Branch Updated"
    else:
        action_name = "Employee Details Updated"

    record_admin_activity(
        db=db,
        action=action_name,
        target_type="Employee",
        target_name=emp.full_name,
        employee_id=emp.employee_id
    )

    return {"message": "Employee updated"}

@router.delete("/employees/{employee_id}")
def delete_employee(employee_id: str, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()

    if not emp:
        return {"error": "Employee not found"}

    emp_name = emp.full_name

    db.delete(emp)
    db.commit()

    record_admin_activity(
    db=db,
    action="Account Deleted",
    target_type="Employee",
    target_name=emp_name,
    employee_id=employee_id
)

    return {"message": "Employee deleted permanently"}


@router.put("/employees/{employee_id}/reset-password")
def reset_password(employee_id: str, data: ResetPasswordRequest, db: Session = Depends(get_db)):

    admin = db.query(Admin).first()

    if not admin or admin.password != data.admin_password:
     raise HTTPException(
        status_code=401,
        detail="Invalid admin password"
    )

    emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()

    if not emp:
        return {"error": "Employee not found"}

    emp.password_hash = data.new_password
    db.commit()
    
    record_admin_activity(
    db=db,
    action="Password Reset",
    target_type="Employee",
    target_name=emp.full_name,
    employee_id=emp.employee_id
)

    return {"message": "Password updated successfully"}


@router.get("/employees/distribution")
def employee_distribution(db: Session = Depends(get_db)):
    result = db.query(
        Employee.branch,
        func.count(Employee.id)
    ).group_by(Employee.branch).all()

    return [
        {"branch": r[0], "count": r[1]}
        for r in result
    ]


@router.get("/employees/login-stats")
def login_stats(db: Session = Depends(get_db)):

    last_7_days = datetime.now() - timedelta(days=7)

    result = db.query(
        func.date(Employee.last_login),
        func.count(Employee.id)
    ).filter(
        Employee.last_login >= last_7_days
    ).group_by(
        func.date(Employee.last_login)
    ).all()

    return [
        {"date": str(r[0]), "count": r[1]}
        for r in result
    ]
    
@router.get("/employees/password/generate")
def generate_password():

    alphabet = string.ascii_letters + string.digits

    password = ''.join(
        secrets.choice(alphabet)
        for _ in range(10)
    )

    return {
        "password": password
    }    
    
@router.get("/employees/{employee_id}")
def get_employee_details(employee_id: str, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()

    if not emp:
        return {"error": "Employee not found"}

    return {
        "id": emp.id,
        "employee_id": emp.employee_id,
        "full_name": emp.full_name,
        "email": emp.email,
        "branch": emp.branch,
        "status": emp.status,
    }

@router.put("/employees/{employee_id}/deactivate")
def deactivate_employee(employee_id: str, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()

    if not emp:
        return {"error": "Employee not found"}

    emp.status = "Inactive"
    db.commit()
    db.refresh(emp)

    record_admin_activity(
        db=db,
        action="Account Deactivated",
        target_type="Employee",
        target_name="John Administrator"
    )

    return {
        "message": "Employee deactivated",
        "employee": {
            "id": emp.id,
            "employee_id": emp.employee_id,
            "full_name": emp.full_name,
            "email": emp.email,
            "branch": emp.branch,
            "status": emp.status,
        }
    }
    
@router.get("/employees/{employee_id}/activity")
def get_employee_activity(employee_id: str, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()

    if not emp:
        return {"error": "Employee not found"}

    logs = db.query(AdminActivityLog).filter(
        AdminActivityLog.target_type == "Employee"
    ).order_by(AdminActivityLog.created_at.desc()).all()

    return [
        {
            "id": log.id,
            "action": log.action,
            "target_type": log.target_type,
            "target_name": log.target_name,
            "created_at": log.created_at,
        }
        for log in logs
    ]
    
    
    
    
              