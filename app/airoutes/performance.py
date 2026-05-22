from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from datetime import date, timedelta

from app.database import get_db
from app.model import DealApplication


router = APIRouter()


def get_current_week_range():
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week, end_of_week


@router.get("/weekly-graph")
def weekly_graph(db: Session = Depends(get_db)):
    start_of_week, end_of_week = get_current_week_range()

    rows = (
        db.query(
            cast(DealApplication.created_at, Date).label("day"),
            func.count(DealApplication.id).label("count")
        )
        .filter(cast(DealApplication.created_at, Date) >= start_of_week)
        .filter(cast(DealApplication.created_at, Date) <= end_of_week)
        .group_by(cast(DealApplication.created_at, Date))
        .all()
    )

    values = [0, 0, 0, 0, 0, 0, 0]

    for row in rows:
        day_index = row.day.weekday()
        values[day_index] = row.count

    return {
        "week_label": f"Week of {start_of_week.strftime('%b %d')} - {end_of_week.strftime('%b %d, %Y')}",
        "daily_deal_activity": values
    }


@router.get("/performance/daily-deals")
def performance_daily_deals(db: Session = Depends(get_db)):
    start_of_week, end_of_week = get_current_week_range()

    rows = (
        db.query(
            cast(DealApplication.created_at, Date).label("day"),
            func.count(DealApplication.id).label("count")
        )
        .filter(cast(DealApplication.created_at, Date) >= start_of_week)
        .filter(cast(DealApplication.created_at, Date) <= end_of_week)
        .group_by(cast(DealApplication.created_at, Date))
        .all()
    )

    values = [0, 0, 0, 0, 0, 0, 0]

    for row in rows:
        day_index = row.day.weekday()
        values[day_index] = row.count

    return {
        "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "deals": values
    }


@router.get("/performance/weekly-summary")
def performance_weekly_summary(db: Session = Depends(get_db)):
    start_of_week, end_of_week = get_current_week_range()

    weekly_deals = (
        db.query(DealApplication)
        .filter(cast(DealApplication.created_at, Date) >= start_of_week)
        .filter(cast(DealApplication.created_at, Date) <= end_of_week)
        .all()
    )

    total_deals = len(weekly_deals)

    total_value_initiated = sum(
        float(deal.amount or 0)
        for deal in weekly_deals
    )

    converted_deals = [
        deal for deal in weekly_deals
        if str(deal.status).lower() == "converted"
    ]

    if total_deals > 0:
        conversion_rate = round((len(converted_deals) / total_deals) * 100)
    else:
        conversion_rate = 0

    top_product_row = (
        db.query(
            DealApplication.product_name,
            func.count(DealApplication.id).label("product_count")
        )
        .filter(cast(DealApplication.created_at, Date) >= start_of_week)
        .filter(cast(DealApplication.created_at, Date) <= end_of_week)
        .group_by(DealApplication.product_name)
        .order_by(func.count(DealApplication.id).desc())
        .first()
    )

    top_product = top_product_row[0] if top_product_row else "No Deals Yet"

    return {
        "week_label": f"Week of {start_of_week.strftime('%b %d')} - {end_of_week.strftime('%b %d, %Y')}",
        "total_value_initiated": total_value_initiated,
        "conversion_rate": conversion_rate,
        "top_product": top_product
    }


@router.get("/performance/recent-deals")
def performance_recent_deals(db: Session = Depends(get_db)):
    deals = (
        db.query(DealApplication)
        .order_by(DealApplication.created_at.desc())
        .limit(5)
        .all()
    )

    result = []

    for deal in deals:
        result.append({
            "client_name": deal.customer_name,
            "client_id": f"DEAL-{deal.id}",
            "product_name": deal.product_name,
            "amount": deal.amount,
            "model_type": deal.model_type,
            "risk_level": deal.risk_level,
            "status": deal.status,
            "time": deal.created_at.strftime("%Y-%m-%d %H:%M")
        })

    return {
        "deals": result
    }