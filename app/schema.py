from pydantic import BaseModel
from pydantic import BaseModel, field_validator
import re

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
    
from pydantic import BaseModel, field_validator
import re

class EmployeeCreate(BaseModel):
    employee_id: str
    password_hash: str
    full_name: str
    email: str
    branch: str

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value):
        if not re.fullmatch(r"[A-Za-z\u0600-\u06FF\s]+", value):
            print(f"ERROR: Invalid full name entered: {value}")
            raise ValueError(
                "Full name must contain letters only"
            )
        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        if not value.endswith("@gmail.com"):
            print(f"ERROR: Invalid email entered: {value}")
            raise ValueError(
                "Email must end with @gmail.com"
            )
        return value
    
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
    
class ClientCreate(BaseModel):
    client_id: str
    name: str
    phone: str
    email: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if not re.match(r"^[A-Za-z\s]+$", value):
            raise ValueError(
                "Name must contain only letters and spaces"
            )
        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        if not value.lower().endswith("@gmail.com"):
            raise ValueError(
                "Email must end with @gmail.com"
            )
        return value     