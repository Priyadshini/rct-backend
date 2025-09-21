import json
from typing import List, Dict
import google.generativeai as genai
from langchain.prompts import PromptTemplate



user_story_prompt_template = (
    "You are a compliance expert specializing in financial regulations.\n"
    "Analyze the following clause and generate three clearly labeled sections:\n"
    "User Story:\n"
    "Acceptance Criteria:\n"
    "Test Case:\n\n"
    "Clause:\n{text}\n\n"
    "Entity: {entity}\n\n"
    "Respond with each section labeled exactly as 'User Story:', 'Acceptance Criteria:' and 'Test Case:'."
)

prompt = PromptTemplate(template=user_story_prompt_template, input_variables=["entity", "text"])


def create_prompt(ner_term: str, text: str) -> str:
    """Render the prompt template with the given entity and clause text."""
    return prompt.format(entity=ner_term, text=text)

def initialize_llm(api_key: str = "AIzaSyABuJqqe-WsN5SYkQl-gYGYMTJNEPqsWJ8", model_name: str = 'gemini-1.5-flash'):
    genai.configure(api_key=api_key)
    llm_model = genai.GenerativeModel(model_name)
    return llm_model


def extract_user_story_from_clause(clause_text: str, ner_json) -> Dict[str, str]:
    """
    Call the LLM and extract structured user story, acceptance criteria, and test case
    for each NER term found.

    Args:
        clause_text: The clause to analyze.
        ner_json: Dict or JSON-like object containing NER terms.

    Returns:
        A dictionary where keys are NER terms and values are the LLM responses
        (or error messages if an exception occurred).
    """
    # Extract all NER terms (if any)
    ner_terms = []
    if isinstance(ner_json, dict):
        items = ner_json.get("basel_iii_legal_requirements")
        if items:
            for item in items:
                if isinstance(item, dict):
                    if "entity" in item:
                        ner_terms.append(item["entity"])
                    elif "entity" in item: # Handle common NER output formats
                        ner_terms.append(item["entity"])
                elif isinstance(item, str):
                    ner_terms.append(item)

    llm = initialize_llm()
    output_response = {}

    for ner_term in ner_terms:
        prompt_text = create_prompt(ner_term, clause_text)
        try:
            response = llm.generate_content(prompt_text)
            # Use .text for the content, or str(response) as a fallback
            output_response[ner_term] = getattr(response, "text", str(response))
        except Exception as e:
            # Store the error message directly for the given ner_term
            output_response[ner_term] = f"Error processing '{ner_term}': {e}"
    return output_response

