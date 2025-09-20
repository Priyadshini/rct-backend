from typing import List, Dict
import re


from google.oauth2 import service_account
import json

import google.generativeai as genai

from langchain.prompts import PromptTemplate
prompt_template = (
    "You are a compliance expert specializing in financial regulations.\n"
    "Analyze the following clause and generate three clearly labeled sections:\n"
    "User Story:\n"
    "Acceptance Criteria:\n"
    "Test Case:\n\n"
    "Clause:\n{text}\n\n"
    "Entity: {entity}\n\n"
    "Respond with each section labeled exactly as 'User Story:', 'Acceptance Criteria:' and 'Test Case:'."
)

prompt = PromptTemplate(template=prompt_template, input_variables=["entity", "text"])




# Load credentials from a JSON file
creds_path = r"resources\crack-mix-472718-s0-8030bdbf378b.json"
credentials = service_account.Credentials.from_service_account_file(creds_path)

# Pass the credentials object to the ChatVertexAI instance


def create_prompt(ner_term: str, text: str) -> str:
    """Render the prompt template with the given entity and clause text."""
    return prompt.format(entity=ner_term, text=text)



def initialize_llm():
    # Load the API key from the credentials JSON file
    # with open(creds_path, "r") as f:
    #     creds_json = json.load(f)
    # api_key = creds_json.get("api_key")
    # if not api_key:
    #     raise ValueError("API key not found in credentials file.")
    genai.configure(api_key="AIzaSyABuJqqe-WsN5SYkQl-gYGYMTJNEPqsWJ8")
    llm_model = genai.GenerativeModel('gemini-1.5-flash')
    return llm_model


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


def extract_user_story_from_clause(clause_text: str, ner_json) -> List[Dict]:
    """
    Call the LLM and extract structured user story, acceptance criteria, and test case
    for each NER term found.

    Args:
        clause_text: The clause to analyze.
        ner_json: Dict or JSON-like object containing NER terms.

    Returns:
        A list of dicts with keys: 'text', 'type', 'confidence', 'entity' (if available).
    """
    # Extract all NER terms (if any)
    ner_terms = []
    if isinstance(ner_json, dict):
        items = ner_json.get("Legal_Regulatory_Terms_NER") or ner_json.get("entities")
        if items:
            for item in items:
                if isinstance(item, dict) and "term" in item:
                    ner_terms.append(item["term"])
                else:
                    ner_terms.append(str(item))
    if not ner_terms:
        ner_terms = ["<NER term>"]

    llm = initialize_llm()
    all_stories = []

    for ner_term in ner_terms:
        prompt_text = create_prompt(ner_term, clause_text)
        try:
            response = llm.generate_content(prompt_text)
            response_text = getattr(response, "text", str(response))
        except Exception:
            try:
                out = genai.generate_text(model=llm, input=prompt_text)
                if isinstance(out, dict):
                    response_text = out.get("output", out.get("candidates", [{}])[0].get("content", ""))
                else:
                    response_text = str(out)
            except Exception:
                response_text = ""

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
