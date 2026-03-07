from fastapi import FastAPI
from app.auth import router as auth_router
from app.ai_routes import router as ai_router
from app.clients import router as clients_router
from app.ai_routes import router as ai_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(ai_router)
app.include_router(clients_router)
app.include_router(ai_router)

