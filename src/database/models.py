from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel

class Role(BaseModel):
    role: str
    description: Optional[str] = None

