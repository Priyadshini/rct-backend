import re
import json
from typing import List, Dict



def split_sections(text: str) -> Dict[str, str]:
    """Split LLM response into sections by the three expected labels.

    Returns a dict with keys 'USER_STORY', 'ACCEPTANCE_CRITERIA', 'TEST_CASE' where
    values are the section bodies (or empty string if not present).
    """
    sections = {"USER_STORY": "", "ACCEPTANCE_CRITERIA": "", "TEST_CASE": ""}
    # Use a regex to find the labeled sections (case-insensitive)
    pattern = re.compile(r"(?mi)^(User Story:|Acceptance Criteria:|Test Case:)\s*(.*?)(?=^User Story:|^Acceptance Criteria:|^Test Case:|\Z)", re.S | re.M)
    for match in pattern.finditer(text):
        label = match.group(1).strip().lower()
        body = match.group(2).strip()
        if label.startswith("user story"):
            sections["USER_STORY"] = body
        elif label.startswith("acceptance criteria"):
            sections["ACCEPTANCE_CRITERIA"] = body
        elif label.startswith("test case"):
            sections["TEST_CASE"] = body
    return sections


def structure_llm_response(output_response) -> Dict[str, str]:
    """Convert raw LLM response text into structured sections."""
    all_stories = []
    for ner_term, response_text in output_response.items():
        sections=split_sections(response_text)
        
        sections = split_sections(response_text)
        if sections["USER_STORY"]:
            all_stories.append({"text": sections["USER_STORY"], "type": "USER_STORY", "confidence": 0.9, "entity": ner_term})
        if sections["ACCEPTANCE_CRITERIA"]:
            all_stories.append({"text": sections["ACCEPTANCE_CRITERIA"], "type": "ACCEPTANCE_CRITERIA", "confidence": 0.9, "entity": ner_term})
        if sections["TEST_CASE"]:
            all_stories.append({"text": sections["TEST_CASE"], "type": "TEST_CASE", "confidence": 0.9, "entity": ner_term})

        # Fallback: if the regex didn't detect sections but the model returned something,
        # include the full response as a generic user story.
        if not (sections["USER_STORY"] or sections["ACCEPTANCE_CRITERIA"] or sections["TEST_CASE"]) and response_text and response_text.strip():
            all_stories.append({"text": response_text.strip(), "type": "USER_STORY", "confidence": 0.7, "entity": ner_term})
        
    return all_stories

def generate_user_story_report(doc_id: int, story_outputs: List[Dict]):
    """Generate a report file (e.g., PDF or HTML) summarizing the user stories."""
    # Placeholder implementation: In a real scenario, you'd use a library like ReportLab or WeasyPrint
    # to generate a formatted report. Here, we'll just create a simple text file.
    report_path = f"reports/user_stories_report_doc_{doc_id}.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(story_outputs, f, ensure_ascii=False, indent=4)
    return report_path
    