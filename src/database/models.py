from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel

class Role(BaseModel):
    role: str
    description: Optional[str] = None


class Document(BaseModel):
    id: int
    name: str
    upload_ts: datetime
    uploader_id: int
    file_path: str
    version: Optional[int] = None

class Clause(BaseModel):
    id: int
    document_id: int
    clause_seq: int
    clause_id: str
    text: str
    page_no: int

class Obligations(BaseModel):
    id: int
    clause_id: int
    text: str
    type: str
    confidence: float
    status: str

class Artifact(BaseModel):
    id: int
    obligation_id: int
    story_text: str
    acceptance_criteria: Optional[str] = None
    status: str

class LLMLog(BaseModel):
    id: int
    clause_id: int
    model_name: str
    model_version: str
    prompt: str
    response: str
    ts: datetime

class AuditLog(BaseModel):
    id: int
    user_id: int
    action: str
    target_type: str
    target_id: Optional[int] = None
    ts: datetime
    details: Optional[str] = None
