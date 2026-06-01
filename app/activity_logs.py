from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, time
from fastapi.responses import FileResponse
import csv

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

    if start_date and start_date.strip():
        start_dt = datetime.combine(
            datetime.strptime(start_date, "%Y-%m-%d"),
            time.min
        )

        query = query.filter(
            AdminActivityLog.created_at >= start_dt
        )

    if end_date and end_date.strip():
        end_dt = datetime.combine(
            datetime.strptime(end_date, "%Y-%m-%d").date(),
            time.max
        )

        query = query.filter(
            AdminActivityLog.created_at <= end_dt
        )

    logs = query.order_by(
        AdminActivityLog.created_at.desc()
    ).all()

    result = []

    for log in logs:
        result.append({
            "id": log.id,
            "created_at": log.created_at.isoformat()
                if log.created_at else "",
            "action": log.action,
            "target_type": log.target_type,
            "target_name": log.target_name,
            "admin_name": "John Administrator"
        })

    return {
        "logs": result
    }


@router.get("/admin/export-activity-logs")
def export_activity_logs(
    start_date: str = "",
    end_date: str = "",
    db: Session = Depends(get_db)
):

    print("START DATE =", start_date)
    print("END DATE =", end_date)

    query = db.query(AdminActivityLog)

    if start_date and start_date.strip():

        start_dt = datetime.combine(
            datetime.strptime(start_date, "%Y-%m-%d").date(),
            time.min
        )

        query = query.filter(
            AdminActivityLog.created_at >= start_dt
        )

    if end_date and end_date.strip():

        end_dt = datetime.combine(
            datetime.strptime(end_date, "%Y-%m-%d").date(),
            time.max
        )

        query = query.filter(
            AdminActivityLog.created_at <= end_dt
        )

    logs = query.order_by(
        AdminActivityLog.created_at.desc()
    ).all()

    file_path = "activity_logs.csv"

    with open(
        file_path,
        mode="w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Action",
            "Target Type",
            "Target Name",
            "Admin",
            "Date",
            "Time"
        ])

        for log in logs:

            writer.writerow([
                log.action,
                log.target_type,
                log.target_name,
                "John Administrator",
                log.created_at.strftime("%d/%m/%Y")
                    if log.created_at else "",
                log.created_at.strftime("%H:%M")
                    if log.created_at else "",
            ])

    return FileResponse(
        path=file_path,
        media_type="text/csv",
        filename="activity_logs.csv"
    )