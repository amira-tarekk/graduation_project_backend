from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from datetime import date, datetime, timedelta

from app.database import get_db
from app.model import DealApplication
from datetime import datetime, timedelta
from sqlalchemy import func
from app.model import DealApplication


router = APIRouter()



@router.get("/performance/deals-this-week/{employee_id}")
def deals_this_week(
    employee_id: str,
    db: Session = Depends(get_db)):

    week_start = datetime.now() - timedelta(days=7)

    deals_count = db.query(DealApplication).filter(
        DealApplication.employee_id == employee_id,
        DealApplication.created_at >= week_start
    ).count()

    return {
        "deals_this_week": deals_count
    }


def get_current_week_range():
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week, end_of_week


@router.get("/weekly-graph/{employee_id}")
def weekly_graph(
    employee_id: str,
    db: Session = Depends(get_db)):
    start_of_week, end_of_week = get_current_week_range()

    rows = (
        db.query(
            cast(DealApplication.created_at, Date).label("day"),
            func.count().label("product_count")
        )
        .filter(
    DealApplication.employee_id == employee_id
)
        .filter(cast(DealApplication.created_at, Date) >= start_of_week)
        .filter(cast(DealApplication.created_at, Date) <= end_of_week)
        .group_by(cast(DealApplication.created_at, Date))
        .all()
    )

    values = [0, 0, 0, 0, 0, 0, 0]

    for row in rows:
        day_index = row.day.weekday()
        values[day_index] = row.product_count

    return {
        "week_label": f"Week of {start_of_week.strftime('%b %d')} - {end_of_week.strftime('%b %d, %Y')}",
        "daily_deal_activity": values
    }


@router.get("/performance/daily-deals/{employee_id}")
def performance_daily_deals(
    employee_id: str,
    db: Session = Depends(get_db)
):
    start_of_week, end_of_week = get_current_week_range()

    rows = (
        db.query(
            cast(DealApplication.created_at, Date).label("day"),
            func.count().label("product_count")
        )
        .filter(
    DealApplication.employee_id == employee_id
)
        .filter(cast(DealApplication.created_at, Date) >= start_of_week)
        .filter(cast(DealApplication.created_at, Date) <= end_of_week)
        .group_by(cast(DealApplication.created_at, Date))
        .all()
    )

    values = [0, 0, 0, 0, 0, 0, 0]

    for row in rows:
        day_index = row.day.weekday()
        values[day_index] = row.product_count

    return {
        "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "deals": values
    }


@router.get("/performance/weekly-summary/{employee_id}")
def performance_weekly_summary(
    employee_id: str,
    db: Session = Depends(get_db)
):
    start_of_week, end_of_week = get_current_week_range()

    weekly_deals = (
        db.query(DealApplication)
        .filter(
        DealApplication.employee_id == employee_id
    )
        .filter(cast(DealApplication.created_at, Date) >= start_of_week)
        .filter(cast(DealApplication.created_at, Date) <= end_of_week)
        .all()
    )

    total_value_initiated = sum(
        float(deal.amount or 0)
        for deal in weekly_deals
    )

    top_product_row = (
        db.query(
            DealApplication.product_name,
            func.count().label("product_count")
        )
        .filter(DealApplication.employee_id == employee_id)
        .filter(cast(DealApplication.created_at, Date) >= start_of_week)
        .filter(cast(DealApplication.created_at, Date) <= end_of_week)
        .group_by(DealApplication.product_name)
        .order_by(func.count().desc())
        .first()
    )

    top_product = (
        top_product_row[0]
        if top_product_row
        else "No Deals Yet"
    )

    return {
        "week_label":
            f"Week of {start_of_week.strftime('%b %d')} - "
            f"{end_of_week.strftime('%b %d, %Y')}",

        "total_value_initiated": total_value_initiated,

        "conversion_rate": 0,

        "top_product": top_product
    }

@router.get("/performance/recent-deals/{employee_id}")
def performance_recent_deals(
    employee_id: str,
    db: Session = Depends(get_db)
):
    deals = (
        db.query(DealApplication)
        .filter(DealApplication.employee_id == employee_id)
        .order_by(DealApplication.created_at.desc())
        .limit(5)
        .all()
    )

    result = []

    for deal in deals:
        result.append({
            "client_name": deal.client_id,
            "client_id": deal.client_id,
            "product_name": deal.product_name,
            "amount": float(deal.amount or 0),
            "time": deal.created_at.strftime("%Y-%m-%d %H:%M")
        })

    return {
        "deals": result
    }
