from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import Session

from .db import Base, connect_db
from sqlalchemy import ForeignKey

db = next(connect_db())


class AuditLog(Base):
    """audit_logs table definition"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    action = Column(String(100), nullable=False)
    target_type = Column(String(50), nullable=False)
    target_id = Column(Integer, nullable=True)
    ts = Column(DateTime, default=datetime.now())
    details = Column(String(500), nullable=True)

class Document(Base):
    """documents table definition"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    doc_type = Column(String(255), nullable=True)
    upload_ts = Column(DateTime, default=datetime.now())
    uploader_id = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)
    version = Column(Integer, nullable=True)

class ComplianceRequirements(Base):
    """clauses table definition"""
    __tablename__ = "compliance_requirements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    section_ref = Column(Integer, nullable=False)
    text = Column(String, nullable=False)
    category = Column(String(355), nullable=True)
    priority = Column(Integer, nullable=True)
    created_ts = Column(DateTime, default=datetime.now())
    

class UserStories(Base):
    """obligations table definition"""
    __tablename__ = "user_stories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    requirement_id = Column(Integer, ForeignKey("compliance_requirements.id"), nullable=False)
    user_story_text = Column(String(255), nullable=False)
    acceptance_criteria = Column(String(255), nullable=True)
    created_ts = Column(DateTime, default=datetime.now())

class Reports(Base):
    """artifacts table definition"""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    report_type = Column(String(255), nullable=False)
    created_ts = Column(DateTime, default=datetime.now())
    file_path = Column(String(500), nullable=False)

class LLMLog(Base):
    """llm_logs table definition"""
    __tablename__ = "llm_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    compliance_id = Column(Integer, ForeignKey("compliance_requirements.id"), nullable=False)
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=False)
    prompt = Column(String, nullable=False)
    response = Column(String, nullable=False)
    created_ts = Column(DateTime, default=datetime.now())


class AuditLogRepository:
    
    @staticmethod
    def create_audit_log(user_id, action, target_type=None, target_id=None, details=None):
        # Ensure target_id is never None to satisfy NOT NULL constraint
        db_audit_log = AuditLog(
            user_id=user_id,
            action=action,
            target_type=target_type if target_type else "",
            target_id=target_id,
            details=details
        )
        print(db_audit_log)
        db.add(db_audit_log)
        db.commit()
        db.refresh(db_audit_log)
        return db_audit_log

    @staticmethod
    def get_audit_logs(skip: int = 0, limit: int = 100) -> List[AuditLog]:
        return db.query(AuditLog).offset(skip).limit(limit).all()
    
class DocumentRepository:

    @staticmethod
    def create_document(name, uploader_id, file_path, version=None):
        db_document = Document(
            name=name,
            uploader_id=uploader_id,
            file_path=file_path,
            version=version
        )
        print( db_document)
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        return db_document.id

    @staticmethod
    def get_documents(skip: int = 0, limit: int = 100) -> List[Document]:
        return db.query(Document).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_document_by_id(doc_id: int) -> Optional[Document]:
        return db.query(Document).filter(Document.id == doc_id).first()
