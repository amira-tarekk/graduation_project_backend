from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
import pandas as pd
import joblib
import numpy as np

from app.database import get_db
from app.model import CreditCardPredictionLog


router = APIRouter()


# =========================
# LOAD MODEL FILES - OLD WAY
# =========================

model = joblib.load("app/ai_models/credit_card/credit_card_model.pkl")
scaler = joblib.load("app/ai_models/credit_card/scaler.pkl")
employment_encoder = joblib.load("app/ai_models/credit_card/employment_encoder.pkl")


# =========================
# REQUEST SCHEMA
# =========================

class CreditCardRequest(BaseModel):
    income: float
    credit_score: int
    employment_status: str


# =========================
# HELPER
# =========================

def clean_json_value(value):
    if isinstance(value, np.generic):
        return value.item()
    return value


# =========================
# PREDICT API
# =========================

@router.post("/predict-credit-card")
def predict_credit_card(
    data: CreditCardRequest,
    db: Session = Depends(get_db)
):
    # Encode employment status
    employment_encoded = employment_encoder.transform([data.employment_status])[0]

    # Exact model features
    features = pd.DataFrame([{
        "Income": data.income,
        "Credit_Score": data.credit_score,
        "Employment_Status": employment_encoded
    }])

    # Scale features
    scaled_features = scaler.transform(features)

    # Call model
    model_output = model.predict(scaled_features)[0]

    # If model returns dict, use it directly
    if isinstance(model_output, dict):
        result = {
            key: clean_json_value(value)
            for key, value in model_output.items()
        }
    else:
        # fallback only if model returns class label
        result = {
            "status": "Approved",
            "approval_probability": 100.0,
            "card_name": str(model_output),
            "interest_rate": "",
            "credit_limit": "",
            "annual_apr": "",
            "recommendation_reason": "Recommended by the AI model."
        }

    # Save in database
    log = CreditCardPredictionLog(
        income=data.income,
        credit_score=data.credit_score,
        employment_status=data.employment_status,
        status=result.get("status"),
        approval_probability=float(result.get("approval_probability", 0)),
        card_name=result.get("card_name"),
        interest_rate=result.get("interest_rate"),
        credit_limit=result.get("credit_limit"),
        annual_apr=result.get("annual_apr"),
        recommendation_reason=result.get("recommendation_reason"),
        created_at=datetime.now()
    )

    db.add(log)
    db.commit()

    return result