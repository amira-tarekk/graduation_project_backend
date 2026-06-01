from sqlalchemy import Column, Integer, String, Float, Numeric
from app.database import Base
from sqlalchemy import DateTime
from sqlalchemy.sql import func
from datetime import UTC, datetime
last_login = Column(DateTime)
from sqlalchemy import DateTime
from datetime import datetime


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    employee_id = Column(String, unique=True)
    password_hash = Column(String)
    status = Column(String)
    full_name = Column(String)
    email = Column(String)
    branch = Column(String)
    last_login = Column(DateTime)
    
class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    client_id = Column(String, unique=True)
    name = Column(String)
    branch = Column(String)
    status = Column(String) 
       
class LoanPredictionLog(Base):
    __tablename__ = "loan_prediction_logs"

    id = Column(Integer, primary_key=True, index=True)

    income = Column(Float)
    credit_score = Column(Integer)
    loan_amount = Column(Float)
    dti_ratio = Column(Float)
    employment_status = Column(String)

    status = Column(String)
    approval_probability = Column(Float)

    product_name = Column(String)
    interest_rate = Column(String)
    monthly_payment = Column(String)
    explanation = Column(String)

    created_at = Column(DateTime, default=datetime.now)  
    


class CreditCardPredictionLog(Base):
    __tablename__ = "credit_card_prediction_logs"

    id = Column(Integer, primary_key=True, index=True)

    income = Column(Float)
    credit_score = Column(Integer)
    employment_status = Column(String)

    status = Column(String)
    approval_probability = Column(Float)
    card_name = Column(String)
    interest_rate = Column(String)
    credit_limit = Column(String)
    annual_apr = Column(String)
    recommendation_reason = Column(String)

    created_at = Column(DateTime, default=datetime.now) 
    
    
class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True)
    admin_id = Column(String, unique=True)
    password = Column(String)    
     
     
class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)   
    
  
    
class EmployeeLogin(Base):
    __tablename__ = "employee_logins"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(20))
    login_time = Column(DateTime, default=datetime.now)  
    
class AdminActivityLog(Base):
    __tablename__ = "admin_activity_logs"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String)
    target_type = Column(String)
    target_name = Column(String)
    employee_id = Column(String, nullable=True)
    admin_name = Column(String, default="John Administrator")
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    
class DealApplication(Base):
    __tablename__ = "deal_applications"

    client_id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(String, nullable=False)

    
    product_name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)

    model_type = Column(String, nullable=True)
    risk_level = Column(String, nullable=True)

    status = Column(String, default="Initiated")

    created_at = Column(DateTime, default=datetime.utcnow)  
    
    
class ChurnPredictionLog(Base):
    __tablename__ = "churn_prediction_logs"

    id = Column(Integer, primary_key=True, index=True)

    credit_score = Column(Integer)
    age = Column(Integer)
    tenure = Column(Integer)
    balance = Column(Float)
    num_of_products = Column(Integer)
    has_credit_card = Column(Integer)
    is_active_member = Column(Integer)
    estimated_salary = Column(Float)

    churn_percentage = Column(Float)
    risk_level = Column(String)

    created_at = Column(DateTime, default=datetime.now)    