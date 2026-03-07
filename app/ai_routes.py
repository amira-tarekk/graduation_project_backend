from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.model import Loan
from app.schema import LoanRequest
import numpy as np
import joblib

# load AI model
model = joblib.load("app/ai_models/loan/model.pkl")
scaler = joblib.load("app/ai_models/loan/scaler2.pkl")

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/predict-loan")
def predict_loan(data: LoanRequest, db: Session = Depends(get_db)):

    
    real_inputs = [
        data.monthly_income,
        data.credit_score,
        data.loan_amount,
        data.dti
    ]

    
    features = np.zeros(246)

    
    features[:len(real_inputs)] = real_inputs

    input_data = [features]

   
    scaled = scaler.transform(input_data)

    
    prediction = model.predict(scaled)[0]

    
    loan = Loan(
        client_id=data.client_id,
        monthly_income=data.monthly_income,
        credit_score=data.credit_score,
        loan_amount=data.loan_amount,
        dti=data.dti,
        employment_status=data.employment_status,
        prediction=str(prediction)
    )

    db.add(loan)
    db.commit()

    return {"prediction": int(prediction)}