import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, String, DateTime, Enum, Float
from sqlalchemy.orm import Session

from .db import Base
from .models import *


class Role(Base):
    """role table definition"""
    __tablename__ = "role"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)


def get__all_roles(db: Session):
    return db.query(Role).all()
