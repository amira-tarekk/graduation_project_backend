from fastapi import APIRouter
from pydantic import BaseModel
import joblib
import pandas as pd
from pathlib import Path

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "ai_models" / "loan"

model = joblib.load(MODEL_DIR / "loan_model.pkl")
scaler = joblib.load(MODEL_DIR / "scaler.pkl")
emp_encoder = joblib.load(MODEL_DIR / "emp_encoder.pkl")
approval_encoder = joblib.load(MODEL_DIR / "approval_encoder.pkl")


class LoanRequest(BaseModel):
    monthly_income: float
    credit_score: int
    requested_loan_amount: float
    dti_ratio: float
    employment_status: str


def calculate_monthly_payment(loan_amount: float, interest_rate: float):
    return round((loan_amount * (1 + interest_rate)) / 12, 2)


@router.post("/loan-recommendation")
def loan_recommendation(data: LoanRequest):
    try:
        employment_encoded = emp_encoder.transform([data.employment_status])[0]
    except Exception:
        return {
            "error": "Invalid employment_status",
            "allowed_values": list(emp_encoder.classes_)
        }

    features = pd.DataFrame([{
        "Income": data.monthly_income,
        "Credit_Score": data.credit_score,
        "Loan_Amount": data.requested_loan_amount,
        "DTI_Ratio": data.dti_ratio,
        "Employment_Status": employment_encoded
    }])

    scaled_features = scaler.transform(features)

    prediction = model.predict(scaled_features)[0]
    probabilities = model.predict_proba(scaled_features)[0]

    try:
        decoded_prediction = approval_encoder.inverse_transform([prediction])[0]
    except Exception:
        decoded_prediction = str(prediction)

    prediction_text = str(decoded_prediction).strip().lower()

    if prediction_text in ["approved", "approve", "1", "yes", "accepted"]:
        status = "Approved"
    else:
        status = "Rejected"

    if status == "Approved":
        if data.credit_score >= 700:
            product_name = "Premium Salary Loan"
            interest_rate_value = 0.055
            interest_rate_text = "5.5%"
            explanation = "Highly recommended due to excellent Credit Score and low DTI ratio."
        else:
            product_name = "Standard Loan"
            interest_rate_value = 0.068
            interest_rate_text = "6.8%"
            explanation = "Recommended because the client is approved with an acceptable credit profile."

        monthly_payment_value = calculate_monthly_payment(
            data.requested_loan_amount,
            interest_rate_value
        )

        monthly_payment_text = f"{monthly_payment_value} EGP"

        if product_name == "Premium Salary Loan":
            alternatives = [
                {
                    "name": "Standard Loan",
                    "interest_rate": "6.8%",
                    "monthly_payment": f"{calculate_monthly_payment(data.requested_loan_amount, 0.068)} EGP"
                },
                {
                    "name": "Secured Loan",
                    "interest_rate": "4.9%",
                    "monthly_payment": f"{calculate_monthly_payment(data.requested_loan_amount, 0.049)} EGP"
                }
            ]
        else:
            alternatives = [
                {
                    "name": "Premium Salary Loan",
                    "interest_rate": "5.5%",
                    "monthly_payment": f"{calculate_monthly_payment(data.requested_loan_amount, 0.055)} EGP"
                },
                {
                    "name": "Secured Loan",
                    "interest_rate": "4.9%",
                    "monthly_payment": f"{calculate_monthly_payment(data.requested_loan_amount, 0.049)} EGP"
                }
            ]

    else:
        product_name = "N/A"
        interest_rate_text = "0%"
        monthly_payment_text = "0 EGP"
        explanation = "The client does not currently meet the loan recommendation criteria."
        alternatives = []

    debug_info = {
        "numeric_prediction": int(prediction),
        "model_classes": [int(c) for c in model.classes_],
        "probabilities": [float(p) for p in probabilities],
        "approval_encoder_classes": list(approval_encoder.classes_),
        "decoded_prediction": str(decoded_prediction)
    }

    return {
        "status": status,
        "prediction_details": {
            "product_name": product_name,
            "interest_rate": interest_rate_text,
            "monthly_payment": monthly_payment_text,
            "explanation": explanation
        },

        # Old response keys kept so Flutter does not break
        "recommended_loan": product_name,
        "interest_rate": interest_rate_text,
        "monthly_installment": monthly_payment_text,
        "reason": explanation,
        "alternatives": alternatives,
        "raw_prediction": str(decoded_prediction),

        # Temporary debug to check the real model output
        "debug": debug_info
    }


@router.get("/loan-employment-values")
def loan_employment_values():
    return {
        "allowed_values": list(emp_encoder.classes_)
    }