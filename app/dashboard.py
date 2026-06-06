from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from datetime import date, timedelta

from app.database import get_db
from app.model import Employee


router = APIRouter()


@router.get("/dashboard/users-summary")
def users_summary(db: Session = Depends(get_db)):
    total_users = db.query(Employee).count()

    active_users = (
        db.query(Employee)
        .filter(Employee.status == "Active")
        .count()
    )

    return {
        "total_users": total_users,
        "active_users": active_users
    }


@router.get("/dashboard/daily-logins")
def daily_logins(db: Session = Depends(get_db)):
    today = date.today()
    start_date = today - timedelta(days=today.weekday())
    end_date = start_date + timedelta(days=6)
    rows = (
        db.query(
            cast(Employee.last_login, Date).label("login_day"),
            func.count(Employee.id).label("count")
        )
        .filter(Employee.last_login.isnot(None))
        .filter(cast(Employee.last_login, Date) >= start_date)
        .filter(cast(Employee.last_login, Date) <= end_date)
        .group_by(cast(Employee.last_login, Date))
        .all()
    )

    values = [0, 0, 0, 0, 0, 0, 0]

    for row in rows:
        index = (row.login_day - start_date).days
        if 0 <= index <= 6:
            values[index] = row.count

    return {
        "days": [
            (start_date + timedelta(days=i)).strftime("%a")
            for i in range(7)
        ],
        "logins": values
    }


@router.get("/dashboard/branch-distribution")
def branch_distribution(db: Session = Depends(get_db)):
    rows = (
        db.query(
            Employee.branch.label("branch"),
            func.count(Employee.id).label("count")
        )
        .group_by(Employee.branch)
        .all()
    )

    result = []

    for row in rows:
        result.append({
            "name": row.branch if row.branch else "Unknown",
            "value": row.count
        })

    return {
        "branches": result
    }
    
@router.get("/dashboard/users-summary")
def users_summary(db: Session = Depends(get_db)):

    total_users = db.query(Employee).count()

    active_users = db.query(Employee).filter(
        Employee.status == "Active"
    ).count()

   

    return {
        "total_users": total_users,
        "active_users": active_users
        
    }    