from pydantic import BaseModel

class Login(BaseModel):
    employee_id: str
    password_hash: str
    
class LoanRequest(BaseModel):
    client_id: str
    monthly_income: float
    credit_score: int
    loan_amount: float
    dti: float
    employment_status: str    