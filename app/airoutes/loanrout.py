from fastapi import FastAPI, HTTPException, APIRouter, Depends
from pydantic import BaseModel
import joblib
import numpy as np

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.model import LoanPredictionLog

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter()




from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

model = joblib.load(
    BASE_DIR / "ai_models" / "loan" / "loan_model.pkl"
)

emp_encoder = joblib.load(
    BASE_DIR / "ai_models" / "loan" / "emp_encoder.pkl"
)

approval_encoder = joblib.load(
    BASE_DIR / "ai_models" / "loan" / "approval_encoder.pkl"
)


class LoanRequest(BaseModel):
    employee_id: str
    income: float              
    credit_score: float
    loan_amount: float
    dti_ratio: float
    employment_status: str


def calculate_monthly_payment(loan_amount, annual_interest_rate, months):
    total_amount = loan_amount * (1 + annual_interest_rate)
    return round(total_amount / months, 2)


def get_income_category(income):
    if income >= 30000:
        return "High Income"
    elif income >= 15000:
        return "Good Income"
    elif income >= 8000:
        return "Moderate Income"
    elif income >= 5000:
        return "Low Income"
    else:
        return "Very Low Income"


def get_credit_category(credit_score):
    if credit_score >= 800:
        return "Excellent"
    elif credit_score >= 720:
        return "Very Good"
    elif credit_score >= 650:
        return "Good"
    elif credit_score >= 580:
        return "Fair"
    else:
        return "Poor"


def calculate_eligibility_score(income, credit_score, loan_amount, dti_ratio, employment_status):
    score = 0

    # Credit Score: 35 points
    if credit_score >= 800:
        score += 35
    elif credit_score >= 720:
        score += 30
    elif credit_score >= 650:
        score += 22
    elif credit_score >= 580:
        score += 12
    else:
        score += 0

    # Income: 25 points
    if income >= 30000:
        score += 25
    elif income >= 15000:
        score += 20
    elif income >= 8000:
        score += 12
    elif income >= 5000:
        score += 6
    else:
        score += 0

    # DTI: 20 points
    if dti_ratio <= 20:
        score += 20
    elif dti_ratio <= 30:
        score += 15
    elif dti_ratio <= 40:
        score += 8
    elif dti_ratio <= 50:
        score += 3
    else:
        score += 0

    # Loan Amount Burden: 15 points
    # كل ما القرض أكبر بالنسبة للدخل، المخاطرة أعلى
    loan_to_income_ratio = loan_amount / max(income, 1)

    if loan_to_income_ratio <= 6:
        score += 15
    elif loan_to_income_ratio <= 12:
        score += 10
    elif loan_to_income_ratio <= 18:
        score += 5
    else:
        score += 0

    # Employment: 5 points
    if employment_status == "employed":
        score += 5

    return min(score, 100)


def get_rejection_reasons(income, credit_score, loan_amount, dti_ratio, employment_status):
    reasons = []

    loan_to_income_ratio = loan_amount / max(income, 1)

    if income < 5000:
        reasons.append("income is below the minimum acceptable threshold")

    if credit_score < 580:
        reasons.append("credit score is too low for unsecured lending")

    if dti_ratio > 50:
        reasons.append("DTI ratio is too high, indicating heavy existing debt burden")

    if loan_to_income_ratio > 18:
        reasons.append("requested loan amount is too high compared to monthly income")

    if employment_status != "employed":
        reasons.append("employment status is unstable")

    if not reasons:
        reasons.append("overall eligibility score is below the minimum approval threshold")

    return reasons


def build_product(product_name, label, loan_amount):
    products = {
        "Premium Salary Loan": {
            "interest_rate": "18.5%",
            "rate_value": 0.185,
            "loan_term": "60 Months",
            "months": 60,
            "reason": "Recommended for applicants with strong income, high credit score, low DTI ratio, and low loan burden."
        },
        "Standard Loan": {
            "interest_rate": "22%",
            "rate_value": 0.22,
            "loan_term": "48 Months",
            "months": 48,
            "reason": "Recommended for applicants with a good financial profile and moderate repayment risk."
        },
        "Secured Loan": {
            "interest_rate": "16%",
            "rate_value": 0.16,
            "loan_term": "36 Months",
            "months": 36,
            "reason": "Recommended when the applicant has moderate risk and may need collateral to reduce lending risk."
        }
    }

    p = products[product_name]

    return {
        "label": label,
        "product_name": product_name,
        "interest_rate": p["interest_rate"],
        "monthly_payment": f"{calculate_monthly_payment(loan_amount, p['rate_value'], p['months'])} EGP",
        "loan_term": p["loan_term"],
        "reason": p["reason"]
    }


def recommend_loan_product(income, credit_score, loan_amount, dti_ratio, employment_status):
    score = calculate_eligibility_score(
        income=income,
        credit_score=credit_score,
        loan_amount=loan_amount,
        dti_ratio=dti_ratio,
        employment_status=employment_status
    )

    loan_to_income_ratio = round(loan_amount / max(income, 1), 2)

    rejection_reasons = get_rejection_reasons(
        income,
        credit_score,
        loan_amount,
        dti_ratio,
        employment_status
    )

    # Hard Reject Conditions
    hard_reject = (
        income < 5000
        or credit_score < 580
        or dti_ratio > 50
        or loan_to_income_ratio > 18
    )

    if hard_reject or score < 45:
        main_reason = "Application rejected because " + ", ".join(rejection_reasons) + "."

        best_match = {
            "label": "NOT ELIGIBLE",
            "product_name": "N/A",
            "interest_rate": "0%",
            "monthly_payment": "0 EGP",
            "loan_term": "N/A",
            "reason": main_reason
        }

        return {
            "status": "Rejected",
            "eligibility_score": score,
            "approval_probability": max(5, min(score, 49)),
            "best_match": best_match,
            "other_suitable_products": [],
            "button_text": "Application Not Eligible",
            "decision_factors": {
                "income_category": get_income_category(income),
                "credit_category": get_credit_category(credit_score),
                "loan_to_income_ratio": loan_to_income_ratio,
                "main_rejection_reasons": rejection_reasons
            }
        }

    # Product Selection
    if score >= 85 and credit_score >= 720 and income >= 15000 and loan_to_income_ratio <= 12:
        best_match = build_product("Premium Salary Loan", "BEST MATCH", loan_amount)
        other_products = [
            build_product("Standard Loan", "OTHER SUITABLE PRODUCT", loan_amount),
            build_product("Secured Loan", "OTHER SUITABLE PRODUCT", loan_amount)
        ]

    elif score >= 65 and credit_score >= 650 and income >= 8000 and loan_to_income_ratio <= 15:
        best_match = build_product("Standard Loan", "BEST MATCH", loan_amount)
        other_products = [
            build_product("Secured Loan", "OTHER SUITABLE PRODUCT", loan_amount)
        ]

    else:
        best_match = build_product("Secured Loan", "BEST MATCH", loan_amount)
        other_products = []

    return {
        "status": "Approved",
        "eligibility_score": score,
        "approval_probability": max(55, score),
        "best_match": best_match,
        "other_suitable_products": other_products,
        "button_text": f"Initiate Loan Application for {best_match['product_name']}",
        "decision_factors": {
            "income_category": get_income_category(income),
            "credit_category": get_credit_category(credit_score),
            "loan_to_income_ratio": loan_to_income_ratio,
            "main_rejection_reasons": []
        }
    }





@router.post("/predict/loan")
async def predict_loan(
    request: LoanRequest,
    db: Session = Depends(get_db)
):
    try:
        employment_status = request.employment_status.lower().strip()

        if employment_status not in list(emp_encoder.classes_):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid employment_status. Use one of: {list(emp_encoder.classes_)}"
            )

        emp_status_encoded = emp_encoder.transform([employment_status])[0]

        input_data = np.array([[
            request.income,
            request.credit_score,
            request.loan_amount,
            request.dti_ratio,
            emp_status_encoded
        ]])

        # ML model still works internally
        prediction_idx = model.predict(input_data)[0]
        model_status = approval_encoder.inverse_transform([prediction_idx])[0]

        probabilities = model.predict_proba(input_data)[0]
        approved_index = list(approval_encoder.classes_).index("Approved")
        model_approval_probability = round(probabilities[approved_index] * 100, 2)

        recommendation = recommend_loan_product(
            income=request.income,
            credit_score=request.credit_score,
            loan_amount=request.loan_amount,
            dti_ratio=request.dti_ratio,
            employment_status=employment_status
        )

        approval_probability = recommendation["approval_probability"]
        rejection_probability = round(100 - approval_probability, 2)

        try:
            new_log = LoanPredictionLog(
                employee_id=request.employee_id,
                income=request.income,
                credit_score=request.credit_score,
                loan_amount=request.loan_amount,
                dti_ratio=request.dti_ratio,
                employment_status=employment_status,

                status=recommendation["status"],
                approval_probability=f"{approval_probability}%",
                rejection_probability=f"{rejection_probability}%",
                eligibility_score=recommendation["eligibility_score"],

                recommended_product=recommendation["best_match"]["product_name"]
            )

            db.add(new_log)
            db.commit()
        except NameError:
            pass

        return {
            "status": recommendation["status"],
            "approval_probability": f"{approval_probability}%",
            "rejection_probability": f"{rejection_probability}%",
            "eligibility_score": recommendation["eligibility_score"],
            "client_profile": {
                "income": request.income,
                "credit_score": request.credit_score,
                "loan_amount": request.loan_amount,
                "dti_ratio": request.dti_ratio,
                "employment_status": employment_status
            },
            "decision_factors": recommendation["decision_factors"],
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