from fastapi import FastAPI
from app.auth import router as auth_router
from app.clients import router as clients_router
from app.dashboard import router as dashboard_router
from app.employees import router as employees_router
from app.branches import router as branches_router
from app.airoutes.loanrout import router as loan_router
from app.airoutes.creditcardrout import router as credit_card_router
from app.airoutes.churnrout import router as churn_router
from app.airoutes.performance import router as performance_router
from app.airoutes.deals import router as deals_router
from app.airoutes.admin_dashboard import router as admin_dashboard_router
from app.dashboard import router as dashboard_router
from app import activity_logs
from app.airoutes.loanrout import router as loan_router
from app.airoutes.creditcardrout import router as credit_card_router



from app.database import Base, engine
from app import model

Base.metadata.create_all(bind=engine)
app = FastAPI()

@app.get("/")
def root():
    return {"message": "API is working 🚀"}

app.include_router(auth_router)
app.include_router(clients_router)
app.include_router(dashboard_router)
app.include_router(employees_router)
app.include_router(branches_router)
app.include_router(loan_router)
app.include_router(credit_card_router)
app.include_router(churn_router)
app.include_router(performance_router)
app.include_router(deals_router)
app.include_router(admin_dashboard_router)
app.include_router(activity_logs.router)