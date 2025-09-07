from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="Job Chatbot")

app.include_router(router, prefix="", tags=["chat"])