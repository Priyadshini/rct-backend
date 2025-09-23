from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Session

from .db import Base, connect_db

db = next(connect_db())

# ------------------ TABLE DEFINITIONS ------------------

class Document(Base):
    __tablename__ = "documents"
    doc_id = Column(Integer, primary_key=True, autoincrement=True)
    doc_name = Column(String(255), nullable=False)
    doc_type = Column(String(50), nullable=False)
    upload_date = Column(DateTime, default=datetime.now())
    status = Column(String(50), default="uploaded")
    file_path = Column(String(500), nullable=False)


class ComplianceRequirement(Base):
    __tablename__ = "compliance_requirements"
    requirement_id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(Integer, ForeignKey("documents.doc_id"), nullable=False)
    section_ref = Column(String(100), nullable=True)
    text = Column(String, nullable=False)
    category = Column(String(50), nullable=True)
    priority = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.now())


class UserStory(Base):
    __tablename__ = "user_stories"
    story_id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(Integer, ForeignKey("documents.doc_id"), nullable=False)
    requirement_id = Column(Integer, ForeignKey("compliance_requirements.requirement_id"), nullable=False)
    user_story_text = Column(String, nullable=False)
    acceptance_criteria = Column(String, nullable=True)
    test_case = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now())


class Report(Base):
    __tablename__ = "reports"
    report_id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(Integer, ForeignKey("documents.doc_id"), nullable=False)
    report_type = Column(String(50), nullable=False)
    generated_at = Column(DateTime, default=datetime.now())
    file_path = Column(String(500), nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    log_id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(String(100), nullable=False)
    timestamp = Column(DateTime, default=datetime.now())

# ------------------ REPOSITORIES ------------------

class DocumentRepository:
    @staticmethod
    def create_document(doc_name, doc_type, file_path, status="uploaded"):
        doc = Document(
            doc_name=doc_name,
            doc_type=doc_type,
            file_path=file_path,
            status=status,
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc.doc_id

    @staticmethod
    def get_documents() -> List[Document]:
        return db.query(Document).all()

    @staticmethod
    def get_document_by_id(doc_id: int) -> Optional[Document]:
        return db.query(Document).filter(Document.doc_id == doc_id).first()


class RequirementRepository:
    @staticmethod
    def create_requirement(doc_id, section_ref, text, category, priority):
        req = ComplianceRequirement(
            doc_id=doc_id,
            section_ref=section_ref,
            text=text,
            category=category,
            priority=priority,
        )
        db.add(req)
        db.commit()
        db.refresh(req)
        return req.requirement_id

    @staticmethod
    def get_requirements_by_doc(doc_id: int) -> List[ComplianceRequirement]:
        return db.query(ComplianceRequirement).filter(ComplianceRequirement.doc_id == doc_id).limit(5).all()


class UserStoryRepository:
    @staticmethod
    def create_user_story(doc_id, requirement_id, user_story_text, acceptance_criteria, test_case):
        story = UserStory(
            doc_id=doc_id,
            requirement_id=requirement_id,
            user_story_text=user_story_text,
            acceptance_criteria=acceptance_criteria,
            test_case=test_case
        )
        db.add(story)
        db.commit()
        db.refresh(story)
        return story.story_id

    @staticmethod
    def get_user_stories_by_doc(doc_id: int) -> List[UserStory]:
        return db.query(UserStory).filter(UserStory.doc_id == doc_id).all()

    @staticmethod
    def delete_user_stories_by_doc(doc_id: int):
        db.query(UserStory).filter(UserStory.doc_id == doc_id).delete()
        db.commit()

class ReportRepository:
    @staticmethod
    def create_report(doc_id, report_type, file_path):
        report = Report(
            doc_id=doc_id,
            report_type=report_type,
            file_path=file_path,
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report.report_id

    @staticmethod
    def get_report(report_id: int) -> Optional[Report]:
        return db.query(Report).filter(Report.report_id == report_id).first()


class AuditLogRepository:
    @staticmethod
    def create_audit_log(action):
        log = AuditLog(action=action)
        db.add(log)
        db.commit()
        db.refresh(log)
        return log.log_id

    @staticmethod
    def get_audit_logs(limit=100) -> List[AuditLog]:
        return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
