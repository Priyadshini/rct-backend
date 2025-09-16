from fastapi import FastAPI, APIRouter, UploadFile, File
from src.database.db import Base, engine
import os
from dotenv import load_dotenv
from src.utils.helper import *
from src.database.db_repository import *
from datetime import datetime


load_dotenv()

router = APIRouter(prefix="/rct")

@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.post("/documents/upload")
async def upload_documents(file: UploadFile = File(...)):
    user_id = 112223  # Placeholder for user identification logic
    file_path = os.path.join(os.getcwd(),os.getenv("UPLOAD_DIR"), datetime.now().strftime("%Y/%m/%d"))
    saved_path = save_file(file_path, file)
    AuditLogRepository.create_audit_log(user_id=user_id, action="UPLOAD", details=f"Uploaded file to {saved_path}")
    DocumentRepository.create_document(name=file.filename, uploader_id=user_id, file_path=saved_path)
    return {"Message": f"File Uploaded - {saved_path}"}

@router.get("/documents")
def list_documents():
    upload_dir = os.path.join(os.getcwd(), os.getenv("UPLOAD_DIR"))
    file_list = []
    for root, dirs, files in os.walk(upload_dir):
        for filename in files:
            file_list.append(os.path.relpath(os.path.join(root, filename), upload_dir))
    return {"files": file_list}



    




