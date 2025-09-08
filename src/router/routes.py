from fastapi import FastAPI, APIRouter
from src.database.db import Base, engine

router = APIRouter(prefix="/rct")

@router.get("/health")
def health_check():
    return {"status": "ok"}


