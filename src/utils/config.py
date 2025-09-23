from dataclasses import dataclass
from datetime import datetime

@dataclass
class UserStoryDto:
    story_id: int
    doc_id: int
    returnment_id: int
    user_story_text: str
    acceptance_criteria: str
    test_case: str
    created_at: str

