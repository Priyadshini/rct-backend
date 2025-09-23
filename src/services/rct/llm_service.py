import json
from typing import List, Dict
import google.generativeai as genai



prompt_template = '''
    "You are a compliance expert specializing in financial regulations.\n"
    "Analyze the following clause and generate three clearly labeled sections:\n"
    "User Story:\n"
    "Acceptance Criteria:\n"
    "Test Case:\n\n"
    "Clause:\n{{text}}\n\n"
    "Respond with each section labeled exactly as 'User Story:', 'Acceptance Criteria:' and 'Test Case:'."
    '''


def initialize_llm(api_key: str, model_name: str = 'gemini-1.5-flash'):
    genai.configure(api_key=api_key)
    llm_model = genai.GenerativeModel(model_name)
    return llm_model


def generate_user_stories_from_requirements(requirement_text: str,  api_key: str):
    """
    Yes so now for the document the requirements table will have NERs 
    so what we need to do is take an individua NER insert into prompt and 
    create the User story and AC
    """
    llm = initialize_llm(api_key)
    prompt_text = prompt_template.replace("{{text}}", requirement_text)
    try:
        response = llm.generate_content(prompt_text)        
        original_response = getattr(response, "text", str(response))
        structured_response = structure_user_story_response(original_response)
        return structured_response
    except Exception as e:
        return f"Error generating user story: {e}"
    

def structure_user_story_response(response_text: str) -> Dict[str, str]:
    sections = {
        "user_story": "",
        "acceptance_criteria": "",
        "test_case": ""
    }

    # Define the expected bolded headers from the LLM's response
    user_story_header = "**User Story:**"
    acceptance_criteria_header = "**Acceptance Criteria:**"
    test_case_header = "**Test Case:**"

    for line in response_text.splitlines():
        line = line.strip()
        if line.startswith(user_story_header):
            # Extract content after the header, stripping any leading/trailing whitespace
            sections["user_story"] = line[len(user_story_header):].strip()
        elif line.startswith(acceptance_criteria_header):
            sections["acceptance_criteria"] = line[len(acceptance_criteria_header):].strip()
        elif line.startswith(test_case_header):
            sections["test_case"] = line[len(test_case_header):].strip()

    return sections

    