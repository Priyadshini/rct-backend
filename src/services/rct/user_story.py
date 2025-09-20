from langchain.prompts import *
from langchain_openai import ChatOpenAI


prompt_template = """You are a compliance expert specializing in financial regulations. 
Your task is to analyze the following clause extracted from a regulatory document and 
generate a user story, acceptance criteria, and a test case that encapsulate the requirements of the clause.
  "entity": "<NER term>",
  "prompt": "Generate a user story, acceptance criteria, and test case for <NER term> in the context of text"
"""

prompt = PromptTemplate.from_template(prompt_template)


def create_prompt(ner_term: str, text: str) -> str:
    return prompt.format(entity=ner_term, prompt=text)


def initialize_llm(model_name: str = "gpt-3.5-turbo", temperature: float = 0.7):
    return ChatOpenAI(model_name=model_name, temperature=temperature)


def extract_user_story_from_clause(clause_text: str) -> list:
    llm = initialize_llm()
    prompt_text = create_prompt("<NER term>", clause_text)
    response = llm.predict(prompt_text)
    # Simple parsing logic; in real scenarios, consider using a more robust method
    stories = []
    for part in response.split("\n\n"):
        if "User Story:" in part:
            story_text = part.split("User Story:")[1].strip()
            stories.append({"text": story_text, "type": "USER_STORY", "confidence": 0.9})
        elif "Acceptance Criteria:" in part:
            criteria_text = part.split("Acceptance Criteria:")[1].strip()
            stories.append({"text": criteria_text, "type": "ACCEPTANCE_CRITERIA", "confidence": 0.9})
        elif "Test Case:" in part:
            test_case_text = part.split("Test Case:")[1].strip()
            stories.append({"text": test_case_text, "type": "TEST_CASE", "confidence": 0.9})
    return stories