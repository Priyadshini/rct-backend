import pdfplumber

def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

import requests

API_URL = "https://api-inference.huggingface.co/models/dbmdz/bert-large-cased-finetuned-conll03-english"
headers = {"Authorization": f"Bearer YOUR_HF_API_KEY"}

def get_named_entities(text):
    response = requests.post(API_URL, headers=headers, json={"inputs": text})
    return response.json()


pdf_text = extract_text_from_pdf("sample.pdf")
entities = get_named_entities(pdf_text)

for entity in entities:
    print(f"{entity['word']} → {entity['entity_group']}")