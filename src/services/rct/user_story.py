from typing import List, Dict
import re

from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI


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


def create_prompt(ner_term: str, text: str) -> str:
    """Render the prompt template with the given entity and clause text."""
    return prompt.format(entity=ner_term, text=text)


def initialize_llm(model_name: str = "gpt-3.5-turbo", temperature: float = 0.7, openai_api_key: str | None = None):
    """Create and return a ChatOpenAI instance.

    If `openai_api_key` is not provided, this function will attempt to read
    the `OPENAI_API_KEY` environment variable. If neither is available a
    ValueError is raised with actionable instructions.
    """
    import os

    key = openai_api_key or os.environ.get("OPENAI_API_KEY")
    if not key:
        raise ValueError(
            "OpenAI API key not found. Set the OPENAI_API_KEY env var or pass openai_api_key to initialize_llm()"
        )

    # Pass the key explicitly to ChatOpenAI to avoid relying on global config.
    return ChatOpenAI(model_name=model_name, temperature=temperature, openai_api_key=key)


def _split_sections(text: str) -> Dict[str, str]:
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


def extract_user_story_from_clause(clause_text: str, ner_term: str = "<NER term>") -> List[Dict]:
    """Call the LLM and extract structured user story, acceptance criteria, and test case.

    Returns a list of dicts with keys: 'text', 'type', 'confidence'.
    """
    llm = initialize_llm()
    prompt_text = create_prompt(ner_term, clause_text)

    # Use .predict; depending on LangChain version this may delegate to the model.
    response_text = llm.predict(prompt_text)

    sections = _split_sections(response_text)

    stories = []
    if sections["USER_STORY"]:
        stories.append({"text": sections["USER_STORY"], "type": "USER_STORY", "confidence": 0.9})
    if sections["ACCEPTANCE_CRITERIA"]:
        stories.append({"text": sections["ACCEPTANCE_CRITERIA"], "type": "ACCEPTANCE_CRITERIA", "confidence": 0.9})
    if sections["TEST_CASE"]:
        stories.append({"text": sections["TEST_CASE"], "type": "TEST_CASE", "confidence": 0.9})

    # Fallback: if the regex didn't detect sections but the model returned something,
    # include the full response as a generic user story.
    if not stories and response_text and response_text.strip():
        stories.append({"text": response_text.strip(), "type": "USER_STORY", "confidence": 0.7})

    return stories