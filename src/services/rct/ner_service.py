import re
import json
from typing import List, Dict
from pathlib import Path
from PyPDF2 import PdfReader
import docx
import spacy
from spacy.matcher import Matcher
from spacy.lang.en import English

# Load spaCy model (sentence segmentation, tokenization)
nlp = spacy.load("en_core_web_sm")


# Lightweight pipeline for fast sentence splitting
sent_nlp = English()
sent_nlp.add_pipe("sentencizer")

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


def run_ner_on_document(text: str, fast_mode: bool = False):
    """
    Extract requirement-like sentences from raw text.
    fast_mode=True uses only sentence splitting + regex (much faster).
    """
    doc = sent_nlp(text) if fast_mode else nlp(text)

    requirements = []
    counter = 1

    for sent in doc.sents:
        sent_text = sent.text.strip()
        if not sent_text:
            continue

        # Match requirement-like phrases
        if re.search(r"\b(must|shall|should|required)\b", sent_text, re.I):
            requirements.append({
                "section_ref": f"REQ-{counter}",
                "text": sent_text,
                "category": classify_category(sent_text),
                "priority": "high",
                "numbers": re.findall(r"\d+(\.\d+)?%?", sent_text),
            })
            counter += 1

    return requirements
