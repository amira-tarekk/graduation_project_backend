from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    employee_id = Column(String, unique=True)
    password_hash = Column(String)
    
class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    client_id = Column(String, unique=True)
    name = Column(String)
    branch = Column(String)
    status = Column(String) 
       
class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True)
    client_id = Column(String)
    monthly_income = Column(Float)
    credit_score = Column(Integer)
    loan_amount = Column(Float)
    dti = Column(Float)
    employment_status = Column(String)
    prediction = Column(String)   