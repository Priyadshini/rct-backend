import re
import json
from typing import List, Dict
from pathlib import Path
from PyPDF2 import PdfReader
import docx
import spacy
from spacy.matcher import Matcher

# Load spaCy model (sentence segmentation, tokenization)
nlp = spacy.load("en_core_web_sm")

BASE_DIR = Path(__file__).resolve().parent  # points to services/rct
KEYWORDS_FILE = BASE_DIR / "resources" / "domain_keyword_list.json"

def load_domain_keywords(json_path: str = KEYWORDS_FILE) -> dict:
    """Load domain-specific keywords from JSON config file."""
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


# Load domain keywords once at startup
DOMAIN_KEYWORDS = load_domain_keywords()


def extract_text_from_file(file_path: str) -> str:
    """Extract raw text from PDF, DOCX, or TXT file."""
    ext = Path(file_path).suffix.lower()
    text = ""

    if ext == ".pdf":
        reader = PdfReader(file_path)
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"

    elif ext == ".docx":
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"

    else:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

    return text


def classify_category(text: str) -> str:
    """Classify sentence into domain categories using keywords from JSON."""
    for category, keywords in DOMAIN_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text.lower():
                return category
    return "general"


def run_ner_on_document(file_path: str) -> List[Dict]:
    """
    Extract requirement-like sentences from a regulatory document.
    Uses spaCy sentence segmentation + rule-based matcher + regex.
    """
    raw_text = extract_text_from_file(file_path)
    doc = nlp(raw_text)

    matcher = Matcher(nlp.vocab)
    # Rule-based requirement patterns
    patterns = [
        [{"LOWER": {"IN": ["must", "shall", "should", "required"]}}],
        [{"LOWER": "is"}, {"LOWER": "required"}, {"LOWER": "to"}],
        [{"LIKE_NUM": True}, {"TEXT": "%"}],  # percentages like 4.5%
    ]
    for i, pattern in enumerate(patterns):
        matcher.add(f"REQ_PATTERN_{i}", [pattern])

    requirements = []
    counter = 1

    for sent in doc.sents:
        sent_doc = nlp(sent.text)
        matches = matcher(sent_doc)

        if matches:
            text = sent.text.strip()

            # Extract percentages and numbers
            numbers = re.findall(r"\d+(\.\d+)?%?", text)

            # Category classification
            category = classify_category(text)

            # Priority assignment
            if re.search(r"\b(must|shall|required)\b", text, re.I):
                priority = "high"
            elif re.search(r"\bshould\b|\brecommended\b", text, re.I):
                priority = "medium"
            else:
                priority = "low"

            requirements.append({
                "section_ref": f"REQ-{counter}",
                "text": text,
                "category": category,
                "priority": priority,
                "numbers": numbers,
            })
            counter += 1

    return requirements
