from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from datetime import date, timedelta
from app.model import EmployeeLogin
from app.database import get_db
from app.model import Employee



router = APIRouter()


@router.get("/admin/total-users")
def total_users(db: Session = Depends(get_db)):
    total = db.query(Employee).count()

    active = (
        db.query(Employee)
        .filter(Employee.status == "Active")
        .count()
    )

    return {
        "total_users": total,
        "active_users": active
    }


@router.get("/admin/daily-logins")
def daily_logins(db: Session = Depends(get_db)):
    today = date.today()
    start_day = today - timedelta(days=6)

    rows = (
        db.query(
            cast(EmployeeLogin.login_time, Date).label("day"),
            func.count(EmployeeLogin.id).label("count")
        )
        .filter(cast(EmployeeLogin.login_time, Date) >= start_day)
        .filter(cast(EmployeeLogin.login_time, Date) <= today)
        .group_by(cast(EmployeeLogin.login_time, Date))
        .all()
    )

    values = [0, 0, 0, 0, 0, 0, 0]

    for row in rows:
        index = (row.day - start_day).days
        values[index] = row.count

    return {
        "days": [
            start_day.strftime("%a"),
            (start_day + timedelta(days=1)).strftime("%a"),
            (start_day + timedelta(days=2)).strftime("%a"),
            (start_day + timedelta(days=3)).strftime("%a"),
            (start_day + timedelta(days=4)).strftime("%a"),
            (start_day + timedelta(days=5)).strftime("%a"),
            today.strftime("%a"),
        ],
        "daily_login_count": values
    }


@router.get("/admin/branch-distribution")
def branch_distribution(db: Session = Depends(get_db)):
    rows = (
        db.query(
            Employee.branch,
            func.count(Employee.id).label("count")
        )
        .group_by(Employee.branch)
        .all()
    )

    result = []

    for row in rows:
        result.append({
            "branch": row.branch,
            "count": row.count
        })

    return {
        "branches": result
    }