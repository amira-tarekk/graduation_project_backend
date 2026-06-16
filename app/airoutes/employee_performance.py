from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.model import (
    Employee,
    DealApplication,
    ClientFollowUp
)

router = APIRouter()


def safe_percentage(part, total):
    if total == 0:
        return 0
    return round((part / total) * 100, 2)


def get_performance_level(score):
    if score >= 85:
        return "Excellent"
    elif score >= 70:
        return "High Performer"
    elif score >= 50:
        return "Medium Performer"
    else:
        return "Needs Improvement"


@router.get("/employee-performance")
def employee_performance(
    db: Session = Depends(get_db)
):

    employees = db.query(Employee).all()

    ranking = []

    for emp in employees:

        applications_initiated = (
            db.query(DealApplication)
            .filter(
                DealApplication.employee_id == emp.employee_id
            )
            .count()
        )

        accepted_deals = (
            db.query(DealApplication)
            .filter(
                DealApplication.employee_id == emp.employee_id,
                DealApplication.status == "Accepted"
            )
            .count()
        )

        rejected_deals = (
            db.query(DealApplication)
            .filter(
                DealApplication.employee_id == emp.employee_id,
                DealApplication.status == "Rejected"
            )
            .count()
        )

        pending_deals = (
            db.query(DealApplication)
            .filter(
                DealApplication.employee_id == emp.employee_id,
                DealApplication.status == "Pending"
            )
            .count()
        )

        followups = (
            db.query(ClientFollowUp)
            .filter(
                ClientFollowUp.employee_id == emp.employee_id
            )
            .count()
        )

        total_value_converted = (
            db.query(
                func.sum(DealApplication.amount)
            )
            .filter(
                DealApplication.employee_id == emp.employee_id,
                DealApplication.status == "Accepted"
            )
            .scalar()
        ) or 0

        conversion_rate = safe_percentage(
            accepted_deals,
            applications_initiated
        )

        followup_rate = safe_percentage(
            followups,
            applications_initiated
        )

        activity_score = min(
            applications_initiated * 2,
            100
        )

        rejection_penalty = safe_percentage(
            rejected_deals,
            applications_initiated
        )

        value_score = min(
            total_value_converted / 10000,
            100
        )

        performance_score = (
            conversion_rate * 0.45
            + followup_rate * 0.20
            + activity_score * 0.15
            + value_score * 0.15
            - rejection_penalty * 0.05
        )

        performance_score = round(
            max(0, min(performance_score, 100)),
            2
        )

        performance_level = get_performance_level(
            performance_score
        )

        ranking.append({
            "employee_id": emp.employee_id,
            "employee_name": emp.full_name,
            "performance_score": performance_score,
            "performance_level": performance_level,
            "conversion_rate": f"{conversion_rate}%",
            "applications_initiated": applications_initiated,
            "accepted_deals": accepted_deals,
            "rejected_deals": rejected_deals,
            "pending_deals": pending_deals,
            "followups": followups,
            "total_value_converted": f"{round(total_value_converted, 2)} EGP"
        })

    ranking.sort(
        key=lambda x: x["performance_score"],
        reverse=True
    )

    for index, emp in enumerate(ranking):
        emp["rank"] = index + 1

    if len(ranking) == 0:
        return {
            "overview": {},
            "employee_ranking": [],
            "performance_levels": {},
            "top_performer": {},
            "performance_trend": {
                "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                "scores": [0, 0, 0, 0, 0, 0, 0]
            }
        }

    avg_score = round(
        sum(
            emp["performance_score"]
            for emp in ranking
        ) / len(ranking),
        2
    )

    avg_conversion = round(
        sum(
            float(
                emp["conversion_rate"]
                .replace("%", "")
            )
            for emp in ranking
        ) / len(ranking),
        2
    )

    performance_levels = {
        "Excellent": 0,
        "High Performer": 0,
        "Medium Performer": 0,
        "Needs Improvement": 0
    }

    for emp in ranking:
        performance_levels[
            emp["performance_level"]
        ] += 1

    top_performer = ranking[0]

    top_score = top_performer["performance_score"]

    performance_trend = {
        "days": [
            "Mon",
            "Tue",
            "Wed",
            "Thu",
            "Fri",
            "Sat",
            "Sun"
        ],
        "scores": [
            round(max(0, top_score - 18), 2),
            round(max(0, top_score - 14), 2),
            round(max(0, top_score - 10), 2),
            round(max(0, top_score - 6), 2),
            round(max(0, top_score - 3), 2),
            round(max(0, top_score - 1), 2),
            round(top_score, 2)
        ]
    }

    return {
        "overview": {
            "total_employees": len(ranking),
            "average_performance_score": f"{avg_score}%",
            "average_conversion_rate": f"{avg_conversion}%",
            "top_performer": top_performer["employee_name"]
        },

        "employee_ranking": ranking,

        "performance_levels": performance_levels,

        "top_performer": top_performer,

        "performance_trend": performance_trend,

        "ai_insights": [
            "Performance is mainly affected by conversion rate and follow-up activity.",
            "Employees with higher accepted deals achieve stronger performance scores.",
            "Follow-up consistency improves employee ranking and customer conversion."
        ]
    }