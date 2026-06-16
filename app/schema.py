from pydantic import BaseModel

class Login(BaseModel):
    employee_id: str
    password_hash: str
    
class LoanRequest(BaseModel):
    employee_id: str
    client_id: str
    monthly_income: float
    credit_score: int
    loan_amount: float
    dti: float
    employment_status: str    
    
    
    
class ChurnRequest(BaseModel):
    employee_id: str
    client_id: str
    credit_score: int
    age: int
    tenure: int
    balance: float
    products: int
    has_card: int
    active_member: int
    salary: float   
    
    
    
class AdminLogin(BaseModel):
    admin_id: str
    password: str    
    
class EmployeeCreate(BaseModel):
    employee_id: str
    password_hash: str
    full_name: str
    email: str
    branch: str 
    
class EmployeeUpdate(BaseModel):
    full_name: str
    email: str
    branch: str
    status: str   
    
class ResetPasswordRequest(BaseModel):
    admin_password: str
    new_password: str 
    
class BranchCreate(BaseModel):
    name: str          
    
class FollowUpRequest(BaseModel):
    deal_id: int
    employee_id: str
    contact_method: str
    contact_outcome: str
    application_status: str
    notes: str = ""    