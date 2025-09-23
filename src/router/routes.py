import os
from datetime import datetime
from typing import Optional
from fastapi.responses import FileResponse
from fastapi import APIRouter, UploadFile, File
from dotenv import load_dotenv
from fastapi import BackgroundTasks
from PyPDF2 import PdfReader
from src.utils.helper import save_file
from src.database.db_repository import (
    DocumentRepository,
    RequirementRepository,
    UserStoryRepository,
    ReportRepository,
    AuditLogRepository,
)
from src.services.rct.ner_service import run_ner_on_document
from src.services.rct.llm_service import generate_user_stories_from_requirements
from src.services.rct.report_service import generate_report_file, download_report_file

load_dotenv()

progress_tracker = {}
router = APIRouter(prefix="/rct")
UPLOAD_DIR = "resources/data"


# ---------------- Health ----------------
@router.get("/health")
def health_check():
    return {"status": "ok"}


# ---------------- Documents ----------------
@router.post("/documents/upload")
async def upload_documents(file: UploadFile = File(...)):
    # Save file
    file_path = os.path.join(os.getcwd(), UPLOAD_DIR)
    saved_path = save_file(file_path, file)

    # Insert into DB
    doc_id = DocumentRepository.create_document(
        doc_name=file.filename,
        doc_type=file.content_type,
        file_path=saved_path,
    )

    # Log action
    AuditLogRepository.create_audit_log(action=f"Uploaded document {file.filename}")

    return {"Message": f"File Uploaded - {saved_path}", "doc_id": doc_id}


@router.get("/documents")
@router.get("/documents/{doc_id}")
def get_documents(doc_id: Optional[int] = None):
    if doc_id:
        doc = DocumentRepository.get_document_by_id(doc_id)
        if not doc:
            return {"error": "Document not found"}
        return {
            "doc_id": doc.doc_id,
            "doc_name": doc.doc_name,
            "doc_type": doc.doc_type,
            "upload_date": doc.upload_date,
            "status": doc.status,
            "file_path": doc.file_path,
        }
    else:
        docs = DocumentRepository.get_documents()
        return {
            "files": [
                {
                    "doc_id": d.doc_id,
                    "doc_name": d.doc_name,
                    "doc_type": d.doc_type,
                    "upload_date": d.upload_date,
                    "status": d.status,
                    "file_path": d.file_path,
                }
                for d in docs
            ]
        }


# ---------------- Requirements ----------------
@router.post("/requirements/extract/{doc_id}")
def extract_requirements(doc_id: int, background_tasks: BackgroundTasks):
    doc = DocumentRepository.get_document_by_id(doc_id)
    if not doc:
        return {"success": False, "error": "Document not found"}

    # reset progress
    progress_tracker[doc_id] = 0

    # kick off async background job
    background_tasks.add_task(process_document_async, doc_id, doc.file_path)

    return {"success": True, "message": "Extraction started. Poll /rct/requirements/progress/{doc_id}."}


def process_document_async(doc_id: int, file_path: str):
    reader = PdfReader(file_path)
    total_pages = len(reader.pages)

    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        # run lightweight NER
        results = run_ner_on_document(text, fast_mode=True)

        for r in results:
            RequirementRepository.create_requirement(
                doc_id=doc_id,
                section_ref=r.get("section_ref"),
                text=r.get("text"),
                category=r.get("category"),
                priority=r.get("priority"),
            )

        # update progress
        progress_tracker[doc_id] = int((i / total_pages) * 100)

    AuditLogRepository.create_audit_log(action=f"Extracted requirements for doc {doc_id}")
    progress_tracker[doc_id] = 100  # done


@router.get("/requirements/progress/{doc_id}")
def get_extraction_progress(doc_id: int):
    progress = progress_tracker.get(doc_id, None)
    if progress is None:
        return {"status": "not_started"}
    elif progress < 100:
        return {"status": "in_progress", "progress": progress}
    else:
        return {"status": "completed", "progress": 100}

@router.get("/requirements/{doc_id}")
def get_requirements(doc_id: int):
    reqs = RequirementRepository.get_requirements_by_doc(doc_id)
    return {
        "requirements": [
            {
                "requirement_id": r.requirement_id,
                "section_ref": r.section_ref,
                "text": r.text,
                "category": r.category,
                "priority": r.priority,
                "created_at": r.created_at,
            }
            for r in reqs
        ]
    }


# ---------------- User Stories ----------------
@router.post("/requirements/{doc_id}/generate_userstories")
def generate_userstories(doc_id: int):
    requirements = RequirementRepository.get_requirements_by_doc(doc_id)
    if not requirements:
        return {"success": False, "error": "No requirements found"}
    
    UserStoryRepository.delete_user_stories_by_doc(doc_id)

    generated = []
    for r in requirements:
        response = generate_user_stories_from_requirements(r.text)
        # story_id = UserStoryRepository.create_user_story(
        #     doc_id=doc_id,
        #     requirement_id=r.requirement_id,
        #     user_story_text=response.get("user_story", "US"),
        #     acceptance_criteria=response.get("acceptance_criteria", "AC"),
        #     test_case=response.get("test_case", "testt")
        # )
        story_id = UserStoryRepository.create_user_story(
            doc_id=doc_id,
            requirement_id=r.requirement_id,
            user_story_text="US",
            acceptance_criteria="AC",
            test_case="testt"
        )
        generated.append(story_id)

    AuditLogRepository.create_audit_log(action=f"Generated {len(generated)} user stories for doc {doc_id}")

    return {"success": True, "count": len(generated)}


@router.get("/userstories/{doc_id}")
def get_userstories(doc_id: int):
    stories = UserStoryRepository.get_user_stories_by_doc(doc_id)
    return {
        "userstories": [
            {
                "story_id": s.story_id,
                "requirement_id": s.requirement_id,
                "user_story_text": s.user_story_text,
                "acceptance_criteria": s.acceptance_criteria,
                "created_at": s.created_at,
            }
            for s in stories
        ]
    }


# ---------------- Reports ----------------
@router.post("/reports/generate/{doc_id}")
def generate_report(doc_id: int):
    doc = DocumentRepository.get_document_by_id(doc_id)
    if not doc:
        return {"success": False, "error": "Document not found"}

    stories = UserStoryRepository.get_user_stories_by_doc(doc_id)
    print(stories)
    if not stories:
        return {"success": False, "error": "No user stories available"}

    file_path, report_type = generate_report_file(doc, stories)

    report_id = ReportRepository.create_report(
        doc_id=doc_id,
        report_type=report_type,
        file_path=file_path,
    )

    AuditLogRepository.create_audit_log(action=f"Generated report {report_id} for doc {doc_id}")

    return {"success": True, "report_id": report_id, "file_path": file_path}


@router.get("/reports/{report_id}/download")
def download_report(report_id: int, format: str):
    report = ReportRepository.get_report(report_id)
    if not report:
        return {"error": "Report not found"}
    return FileResponse(download_report_file(report, format), media_type="application/octet-stream", filename=f"report_{report_id}.{format}")


@router.get("/audit/logs")
def get_audit_logs():
    logs = AuditLogRepository.get_audit_logs()
    return {
        "logs": [
            {"log_id": l.log_id, "action": l.action, "timestamp": l.timestamp}
            for l in logs
        ]
    }
