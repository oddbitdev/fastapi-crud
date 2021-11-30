from fastapi import FastAPI
from app.api.routers import planning_router

app = FastAPI()
app.include_router(planning_router)
