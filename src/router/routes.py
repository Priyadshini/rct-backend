from dataclasses import asdict
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
from src.utils.helper import *
import json


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
        return asdict(document)
    else:
        documents = DocumentRepository.get_documents()
        return  asdict(documents)
    

@router.get("/audit-logs")
def get_audit_logs(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1)):
    logs = AuditLogRepository.get_audit_logs(skip=skip, limit=limit)
    return asdict(logs)


@router.get("/audit-logs/{log_id}")
def get_audit_log_by_id(log_id: int):    
    log = AuditLogRepository.get_audit_log_by_id(log_id)
    if log is None:
        return {"error": f"Audit log with id {log_id} not found"}, 404
    return asdict(log)


@router.post("/requirements/extract/{doc_id}")
def extract_requirements(doc_id: int):
    user_id = 112223  # Placeholder for user identification logic
    document = DocumentRepository.get_document_by_id(doc_id)
    if document is None:
        return {"error": f"Document with id {doc_id} not found"}, 404

    clauses = extract_compliance_req_from_document(document.file_path)
    ner_json = read_json(r"tryouts\ner1.json")

    stories_output = []
    for clause in clauses:
        stories = extract_user_story_from_clause(clause, ner_json)
        stories_output.append([{
            "type": story["type"],
            "confidence": story["confidence"],
            "text": story["text"]
        } for story in stories])

    # save stories in file
    output_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"stories_doc_{doc_id}.json")
    save_json(output_file, stories_output)

    AuditLogRepository.create_audit_log(
        user_id=user_id,
        action="EXTRACT_REQUIREMENTS",
        target_type="document",
        target_id=doc_id,
        details=f"Extracted {len(clauses)} clauses and their obligations from document id {doc_id} and saved to {output_file}"
    )
    return {
        "message": f"Extracted {len(clauses)} clauses and their obligations from document id {doc_id}",
        "clauses_extracted": len(clauses),
        "stories": stories_output,
        "output_file": output_file
    }


    




