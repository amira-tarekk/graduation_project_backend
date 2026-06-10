from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from pathlib import Path

import joblib
import numpy as np

from app.database import get_db
from app.model import CreditCardPredictionLog



router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent

card_model = joblib.load(
    BASE_DIR / "ai_models" / "credit_card" / "credit_card_model.pkl"
)

card_emp_encoder = joblib.load(
    BASE_DIR / "ai_models" / "credit_card" / "employment_encoder.pkl"
)

card_scaler = joblib.load(
    BASE_DIR / "ai_models" / "credit_card" / "scaler.pkl"
)

card_target_encoder = joblib.load(
    BASE_DIR / "ai_models" / "credit_card" / "target_encoder.pkl"
)


class CreditCardRequest(BaseModel):
    employee_id: str
    income: float
    credit_score: float
    employment_status: str


def calculate_card_score(income, credit_score, employment_status):
    score = 0

    if credit_score >= 800:
        score += 45
    elif credit_score >= 720:
        score += 35
    elif credit_score >= 650:
        score += 25
    elif credit_score >= 580:
        score += 10

    if income >= 30000:
        score += 35
    elif income >= 15000:
        score += 25
    elif income >= 8000:
        score += 15
    elif income >= 5000:
        score += 5

    if employment_status == "employed":
        score += 20

    return min(score, 100)


def calculate_dynamic_interest_rate(base_rate, income, credit_score, employment_status):
    rate = base_rate

    if credit_score >= 800:
        rate -= 2.0
    elif credit_score >= 720:
        rate -= 1.2
    elif credit_score >= 650:
        rate -= 0.5
    elif credit_score < 600:
        rate += 1.5

    if income >= 30000:
        rate -= 1.0
    elif income >= 15000:
        rate -= 0.5
    elif income < 8000:
        rate += 1.0

    if employment_status != "employed":
        rate += 1.0

    rate = max(16.0, min(rate, 29.0))
    return round(rate, 1)


def build_card(card_name, label, income, interest_rate, limit_multiplier, apr_extra, reason=None):
    return {
        "label": label,
        "card_name": card_name,
        "interest_rate": f"{interest_rate}%",
        "monthly_credit_limit": f"{round(income * limit_multiplier, 2)} EGP",
        "annual_apr": f"{round(interest_rate + apr_extra, 1)}%",
        "reason": reason or ""
    }


def recommend_credit_card(income, credit_score, employment_status):
    score = calculate_card_score(income, credit_score, employment_status)

    platinum_rate = calculate_dynamic_interest_rate(
        18.5, income, credit_score, employment_status
    )
    standard_rate = calculate_dynamic_interest_rate(
        22.5, income, credit_score, employment_status
    )
    basic_rate = calculate_dynamic_interest_rate(
        26.0, income, credit_score, employment_status
    )

    if credit_score < 580 or income < 5000:
        return {
            "status": "Rejected",
            "approval_probability": max(5, min(score, 49)),
            "best_match": {
                "label": "NOT ELIGIBLE",
                "card_name": "N/A",
                "interest_rate": "0%",
                "monthly_credit_limit": "0 EGP",
                "annual_apr": "0%",
                "reason": "Application rejected due to low credit score or insufficient income."
            },
            "other_suitable_products": [],
            "button_text": "Application Not Eligible"
        }

    if score >= 85:
        best = build_card(
            card_name="Elite Cashback Platinum",
            label="BEST MATCH",
            income=income,
            interest_rate=platinum_rate,
            limit_multiplier=2.3,
            apr_extra=4.0,
            reason="Recommended due to high credit score and strong income. This card qualifies for premium cashback benefits and a competitive interest rate."
        )

        others = [
            build_card(
                card_name="Standard Rewards Card",
                label="OTHER SUITABLE PRODUCT",
                income=income,
                interest_rate=standard_rate,
                limit_multiplier=1.7,
                apr_extra=2.5
            ),
            build_card(
                card_name="Basic Credit Card",
                label="OTHER SUITABLE PRODUCT",
                income=income,
                interest_rate=basic_rate,
                limit_multiplier=1.1,
                apr_extra=2.0
            )
        ]

    elif score >= 60:
        best = build_card(
            card_name="Standard Rewards Card",
            label="BEST MATCH",
            income=income,
            interest_rate=standard_rate,
            limit_multiplier=1.7,
            apr_extra=2.5,
            reason="Recommended for applicants with a good financial profile and moderate credit risk."
        )

        others = [
            build_card(
                card_name="Basic Credit Card",
                label="OTHER SUITABLE PRODUCT",
                income=income,
                interest_rate=basic_rate,
                limit_multiplier=1.1,
                apr_extra=2.0
            )
        ]

    else:
        best = build_card(
            card_name="Basic Credit Card",
            label="BEST MATCH",
            income=income,
            interest_rate=basic_rate,
            limit_multiplier=1.1,
            apr_extra=2.0,
            reason="Recommended with a limited credit limit due to moderate income or credit score."
        )

        others = []

    return {
        "status": "Approved",
        "approval_probability": max(55, score),
        "best_match": best,
        "other_suitable_products": others,
        "button_text": f"Initiate Card Application for {best['card_name']}"
    }





@router.post("/predict/credit-card")
async def predict_credit_card(
    request: CreditCardRequest,
    db: Session = Depends(get_db)
):
    try:
        employment_status = request.employment_status.lower().strip()

        if employment_status not in list(card_emp_encoder.classes_):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid employment_status. Use one of: {list(card_emp_encoder.classes_)}"
            )

        emp_encoded = card_emp_encoder.transform([employment_status])[0]

        input_data = np.array([[
            request.income,
            request.credit_score,
            emp_encoded
        ]])

        input_scaled = card_scaler.transform(input_data)

        prediction_idx = card_model.predict(input_scaled)[0]
        _ = card_target_encoder.inverse_transform([prediction_idx])[0]

        recommendation = recommend_credit_card(
            income=request.income,
            credit_score=request.credit_score,
            employment_status=employment_status
        )

        approval_probability = recommendation["approval_probability"]
        rejection_probability = round(100 - approval_probability, 2)
        
        log = CreditCardPredictionLog(
    employee_id=request.employee_id,
    income=request.income,
    credit_score=request.credit_score,
    employment_status=employment_status,

    status=recommendation["status"],

    approval_probability=f"{approval_probability}%",
    rejection_probability=f"{rejection_probability}%",

    recommended_product=
        recommendation["best_match"]["card_name"]
)

        db.add(log)
        db.commit()
        
        

        return {
            "status": recommendation["status"],
            "approval_probability": f"{approval_probability}%",
            "rejection_probability": f"{rejection_probability}%",
            "client_profile": {
                "income": request.income,
                "credit_score": request.credit_score,
                "employment_status": employment_status
            },
            "ui_result": {
                "section_title": "AI Optimal Product Recommendation",
                "subtitle": "Based on the client's financial profile and creditworthiness",
                "best_match": recommendation["best_match"],
                "other_suitable_products": recommendation["other_suitable_products"],
                "button_text": recommendation["button_text"]
            }
        }

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))