from fastapi import FastAPI, APIRouter, UploadFile, File
from src.database.db import Base, engine
import os
from dotenv import load_dotenv
from src.utils.helper import *
from src.database.db_repository import *
from datetime import datetime
from typing import Optional
from fastapi import Query
from src.services.rct.user_story import *
from src.services.rct.compliance_req import *


load_dotenv()

router = APIRouter(prefix="/rct")
UPLOAD_DIR = "resources/data"

@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.post("/documents/upload")
async def upload_documents(file: UploadFile = File(...)):
    user_id = 112223  # Placeholder for user identification logic
    file_path = os.path.join(os.getcwd(),UPLOAD_DIR)
    saved_path = save_file(file_path, file)
    doc_id = DocumentRepository.create_document(name=file.filename, uploader_id=user_id, file_path=saved_path)
    AuditLogRepository.create_audit_log(user_id=user_id, action="UPLOAD", target_type="document", target_id=doc_id,details=f"Uploaded file to {saved_path}")
    return {"Message": f"File Uploaded - {saved_path}"}


@router.get("/documents")
@router.get("/documents/{doc_id}")
def get_all_documents(doc_id: Optional[int] = None):
    if doc_id is not None:
        document = DocumentRepository.get_document_by_id(doc_id)
        if document is None:
            return {"error": f"Document with id {doc_id} not found"}, 404
        return {"id": document.id, "name": document.name, "upload_ts": document.upload_ts, "uploader_id": document.uploader_id, "file_path": document.file_path, "version": document.version}
    else:
        documents = DocumentRepository.get_documents()
        file_list = [{"id": doc.id, "name": doc.name, "upload_ts": doc.upload_ts, "uploader_id": doc.uploader_id, "file_path": doc.file_path, "version": doc.version} for doc in documents]
        return {"files": file_list}
    

@router.get("/audit-logs")
def get_audit_logs(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1)):
    logs = AuditLogRepository.get_audit_logs(skip=skip, limit=limit)
    log_list = [{"id": log.id, "user_id": log.user_id, "action": log.action, "target_type": log.target_type, "target_id": log.target_id, "ts": log.ts, "details": log.details} for log in logs]
    return {"audit_logs": log_list}

@router.get("/audit-logs/{log_id}")
def get_audit_log_by_id(log_id: int):    
    log = AuditLogRepository.get_audit_log_by_id(log_id)
    if log is None:
        return {"error": f"Audit log with id {log_id} not found"}, 404
    return {"id": log.id, "user_id": log.user_id, "action": log.action, "target_type": log.target_type, "target_id": log.target_id, "ts": log.ts, "details": log.details}

@router.post("/requirements/extract/{doc_id}")
def extract_requirements(doc_id: int):
    user_id = 112223  # Placeholder for user identification logic
    document = DocumentRepository.get_document_by_id(doc_id)
    if document is None:
        return {"error": f"Document with id {doc_id} not found"}, 404
    print(document.file_path)
    clauses = extract_compliance_req_from_document(document.file_path)
    print(clauses)
    return {"clauses": clauses}
    for clause in clauses:
        stories = extract_user_story_from_clause(clause)
        print(stories)
    # #
    AuditLogRepository.create_audit_log(user_id=user_id, action="EXTRACT_REQUIREMENTS", target_type="document", target_id=doc_id, details=f"Extracted {len(clauses)} clauses and their obligations from document id {doc_id}")
    return {"Message": f"Extracted {len(clauses)} clauses and their obligations from document id {doc_id}"}




    




