from sqlalchemy import Column, Integer, String, Float, Numeric
from app.database import Base
from sqlalchemy import DateTime
from sqlalchemy.sql import func
from datetime import UTC, datetime
last_login = Column(DateTime)
from sqlalchemy import DateTime
from datetime import datetime
from datetime import datetime
from zoneinfo import ZoneInfo

EGYPT_TZ = ZoneInfo("Africa/Cairo")

def egypt_now():
    return datetime.now(EGYPT_TZ)



class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    employee_id = Column(String, unique=True)
    password_hash = Column(String)
    status = Column(String)
    full_name = Column(String)
    email = Column(String)
    branch = Column(String)
    last_login = Column(DateTime, default=egypt_now)
    
class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    client_id = Column(String, unique=True)
    name = Column(String)
    branch = Column(String)
    status = Column(String) 
    phone = Column(String)
    email = Column(String)
       
class LoanPredictionLog(Base):
    __tablename__ = "loan_prediction_logs"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String)
    income = Column(Float)
    credit_score = Column(Float)
    loan_amount = Column(Float)
    dti_ratio = Column(Float)
    employment_status = Column(String)

    status = Column(String)
    approval_probability = Column(String)
    rejection_probability = Column(String)
    eligibility_score = Column(Integer)

    recommended_product = Column(String)

    created_at = Column(DateTime, default=egypt_now) 
    


class CreditCardPredictionLog(Base):
    __tablename__ = "credit_card_prediction_logs"
     
    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(String)
    income = Column(Float)
    credit_score = Column(Float)
    employment_status = Column(String)

    status = Column(String)

    approval_probability = Column(String)
    rejection_probability = Column(String)

    recommended_product = Column(String)

    created_at = Column(DateTime, default=egypt_now)
    
    
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
    login_time = Column(DateTime, default=egypt_now)  
    
class AdminActivityLog(Base):
    __tablename__ = "admin_activity_logs"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String)
    target_type = Column(String)
    target_name = Column(String)
    employee_id = Column(String, nullable=True)
    admin_name = Column(String, default="John Administrator")
    created_at = Column(DateTime, default=egypt_now)
    
class DealApplication(Base):
    __tablename__ = "deal_applications"

    id = Column(Integer, primary_key=True, index=True)

    client_id = Column(String, nullable=False)

    employee_id = Column(String, nullable=False)

    product_name = Column(String, nullable=False)

    amount = Column(Float, nullable=False)

    model_type = Column(String, nullable=True)

    risk_level = Column(String, nullable=True)

    status = Column(String, default="Initiated")

    created_at = Column(DateTime, default=egypt_now) 
    
    
class ChurnPredictionLog(Base):
    __tablename__ = "churn_prediction_logs"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(String)
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

    created_at = Column(DateTime, default=egypt_now)    
    
    
    
class ClientFollowUp(Base):
    __tablename__ = "client_followups"

    id = Column(Integer, primary_key=True)

    deal_id = Column(Integer)

    employee_id = Column(String)

    client_id = Column(String)

    contact_method = Column(String)

    contact_outcome = Column(String)

    application_status = Column(String)

    notes = Column(String)

    created_at = Column(DateTime, default=egypt_now)    
    
    
class EmployeePerformanceSnapshot(Base):
    __tablename__ = "employee_performance_snapshots"

    id = Column(Integer, primary_key=True)

    employee_id = Column(String)

    performance_score = Column(Float)

    performance_level = Column(String)

    conversion_rate = Column(Float)

    rank = Column(Integer)

    created_at = Column(DateTime, default=egypt_now)    