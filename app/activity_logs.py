from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, time

from app.database import SessionLocal
from app.model import AdminActivityLog

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/admin/activity-log")
@router.get("/admin/activity-logs")
def get_admin_activity_logs(
    start_date: str = "",
    end_date: str = "",
    db: Session = Depends(get_db)
):
    query = db.query(AdminActivityLog)

    if start_date:
        start_dt = datetime.combine(
            datetime.strptime(start_date, "%Y-%m-%d").date(),
            time.min
        )
        query = query.filter(AdminActivityLog.created_at >= start_dt)

    if end_date:
        end_dt = datetime.combine(
            datetime.strptime(end_date, "%Y-%m-%d").date(),
            time.max
        )
        query = query.filter(AdminActivityLog.created_at <= end_dt)

    logs = query.order_by(AdminActivityLog.created_at.desc()).all()

    return [
        {
            "id": log.id,
            "date": log.created_at.strftime("%Y-%m-%d") if log.created_at else "",
            "time": log.created_at.strftime("%H:%M") if log.created_at else "",
            "action": log.action,
            "target_type": log.target_type,
            "target_name": log.target_name,
            "admin_name": "John Administrator"
        }
        for log in logs
    ]