from fastapi import FastAPI, APIRouter, UploadFile, File
from src.database.db import Base, engine
import os
from dotenv import load_dotenv
from src.utils.helper import *
from datetime import datetime


load_dotenv()

router = APIRouter(prefix="/rct")

@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.post("/documents/upload")
async def upload_documents(file: UploadFile = File(...)):
    file_path = os.path.join(os.getcwd(),os.getenv("UPLOAD_DIR"), datetime.now().strftime("%Y/%m/%d"))
    saved_path = save_file(file_path, file)
    return {"Message": f"File Uploaded - {saved_path}" }



    




