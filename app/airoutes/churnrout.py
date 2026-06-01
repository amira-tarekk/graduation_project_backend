from fastapi import APIRouter, Depends
from pydantic import BaseModel
import pandas as pd
import joblib
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.model import ChurnPredictionLog

router = APIRouter()

# =========================
# DATABASE
# =========================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# LOAD MODEL FILES - OLD WAY
# =========================

model = joblib.load(r"C:\Users\aamir\Desktop\myapp\app\ai_models\churn\model (1).pkl")
scaler = joblib.load(r"C:\Users\aamir\Desktop\myapp\app\ai_models\churn\scaler (1).pkl")
selector = joblib.load(r"C:\Users\aamir\Desktop\myapp\app\ai_models\churn\selector.pkl")
columns = joblib.load(r"C:\Users\aamir\Desktop\myapp\app\ai_models\churn\columns (2).pkl")


# =========================
# REQUEST SCHEMA
# =========================

class ChurnRequest(BaseModel):
    credit_score: int
    age: int
    tenure: int
    balance: float
    num_of_products: int
    has_credit_card: int
    is_active_member: int
    estimated_salary: float


# =========================
# HELPER FUNCTIONS
# =========================

def get_age_group(age: int):
    if age < 30:
        return "<30"
    elif age < 40:
        return "30-40"
    elif age < 50:
        return "40-50"
    elif age < 60:
        return "50-60"
    else:
        return "60+"


def get_risk_level(churn_percentage: float):
    if churn_percentage >= 70:
        return "High Risk"
    elif churn_percentage >= 40:
        return "Medium Risk"
    else:
        return "Low Risk"


# =========================
# CHURN PREDICTION API
# =========================

@router.post("/churn-predict")
def predict_churn(data: ChurnRequest, db: Session = Depends(get_db)):

    # Default values because UI does not send these fields
    geography = "Egypt"
    gender = "Male"

    age_group = get_age_group(data.age)

    input_df = pd.DataFrame([{
        "CreditScore": data.credit_score,
        "Geography": geography,
        "Gender": gender,
        "Age": data.age,
        "Tenure": data.tenure,
        "Balance": data.balance,
        "NumOfProducts": data.num_of_products,
        "HasCrCard": data.has_credit_card,
        "IsActiveMember": data.is_active_member,
        "EstimatedSalary": data.estimated_salary,
        "AgeGroup": age_group
    }])

    # Same encoding used during training
    input_df = pd.get_dummies(
        input_df,
        columns=["Geography", "Gender", "AgeGroup"],
        drop_first=True
    )

    # Match training columns exactly
    input_df = input_df.reindex(columns=columns, fill_value=0)

    # Same selector and scaler used during training
    selected_input = selector.transform(input_df)
    scaled_input = scaler.transform(selected_input)

    # Real model prediction probability
    probability = model.predict_proba(scaled_input)[0][1]

    churn_percentage = round(float(probability) * 100, 2)
    risk_level = get_risk_level(churn_percentage)

    # Save prediction in database
    log = ChurnPredictionLog(
        credit_score=data.credit_score,
        age=data.age,
        tenure=data.tenure,
        balance=data.balance,
        num_of_products=data.num_of_products,
        has_credit_card=data.has_credit_card,
        is_active_member=data.is_active_member,
        estimated_salary=data.estimated_salary,
        churn_percentage=churn_percentage,
        risk_level=risk_level
    )

    db.add(log)
    db.commit()

    # Flutter expected response
    return {
        "churn_percentage": churn_percentage,
        "risk_level": risk_level
    }