from fastapi import FastAPI, APIRouter, UploadFile, File
from src.database.db import Base, engine
import os
from dotenv import load_dotenv
from src.utils.helper import *
from src.database.db_repository import *
from datetime import datetime
from typing import Optional
from fastapi import Query


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
    doc_id = DocumentRepository.create_document(name=file.filename, uploader_id=user_id, file_path=saved_path)
    AuditLogRepository.create_audit_log(user_id=user_id, action="UPLOAD", target_type="document", target_id=doc_id,details=f"Uploaded file to {saved_path}")
    return {"Message": f"File Uploaded - {saved_path}"}


@router.get("/documents")
@router.get("/documents/{doc_id}")
def get_all_documents(doc_id: Optional[int] = None):
    if doc_id is not None:
        document = DocumentRepository.get_document_by_id(doc_id)
        return {"id": document.id, "name": document.name, "upload_ts": document.upload_ts, "uploader_id": document.uploader_id, "file_path": document.file_path, "version": document.version}
    else:
        documents = DocumentRepository.get_documents()
        file_list = [{"id": doc.id, "name": doc.name, "upload_ts": doc.upload_ts, "uploader_id": doc.uploader_id, "file_path": doc.file_path, "version": doc.version} for doc in documents]
        return {"files": file_list}




    




