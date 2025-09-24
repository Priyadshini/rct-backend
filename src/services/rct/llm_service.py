import json
from typing import Dict
import google.generativeai as genai

# Improved prompt: forces structured JSON output
prompt_template = """
You are a compliance expert specializing in financial regulations.
Analyze the following clause and generate three fields in JSON:

{
  "user_story": "As a <user>, I want <goal>, so that <benefit>.",
  "acceptance_criteria": [
    "Given <context>, When <action>, Then <outcome>",
    "..."
  ],
  "test_case": "A high-level test case for validation"
}

Clause:
{{text}}

Respond ONLY with valid JSON, no explanations.
"""


def initialize_llm(api_key: str, model_name: str = "gemini-1.5-flash"):
    """Initialize Google Generative AI model."""
    genai.configure(api_key=api_key)  # ensure API key is applied
    return genai.GenerativeModel(model_name)


def parse_llm_response(response_text: str) -> Dict[str, str]:
    """Parse LLM response safely into structured dict."""
    try:
        return json.loads(response_text)
    except Exception:
        # try to extract JSON substring
        start, end = response_text.find("{"), response_text.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(response_text[start:end + 1])
            except Exception:
                pass
    # fallback defaults
    return {
        "user_story": "Parsing failed",
        "acceptance_criteria": ["Parsing failed"],
        "test_case": "Parsing failed",
    }


def generate_user_stories_from_requirements(requirement_text: str, api_key: str) -> Dict[str, str]:
    """
    Take a regulatory clause (requirement) and generate:
    - User Story
    - Acceptance Criteria
    - Test Case
    """
    llm = initialize_llm(api_key)

    # Avoid overloading model with extremely long requirements
    truncated_text = requirement_text[:1200]

    prompt_text = prompt_template.replace("{{text}}", truncated_text)

    try:
        response = llm.generate_content(prompt_text)

        # Safely extract model response text
        response_text = getattr(response, "text", None)
        if not response_text and hasattr(response, "candidates"):
            response_text = response.candidates[0].content.parts[0].text

        if not response_text:
            return {
                "user_story": "No response from model",
                "acceptance_criteria": ["N/A"],
                "test_case": "N/A",
            }

        # Parse JSON response
        structured_response = parse_llm_response(response_text)
        return structured_response

    except Exception as e:
        return {
            "user_story": "Error generating user story",
            "acceptance_criteria": [f"Error: {e}"],
            "test_case": "N/A",
        }
