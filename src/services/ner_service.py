import os
import fitz
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


def convert_pdf_to_text(file_path: str) -> str:
    """
    Convert PDF file to text using PyMuPDF.
    """
    print(file_path)
    with fitz.open(file_path) as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    print(text)
    return text


def embed_texts(texts: list, model_name: str = 'all-MiniLM-L6-v2') -> np.ndarray:
    """Embed a list of texts using a pre-trained model."""
    model = SentenceTransformer(model_name)
    embeddings = model.encode(texts)
    return np.array(embeddings)


def create_faiss_index(embeddings: np.ndarray) -> faiss.IndexFlatL2:
    """Create a FAISS index from embeddings."""
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index

def save_faiss_index(index: faiss.IndexFlatL2, file_path: str):
    """Save FAISS index to a file."""
    faiss.write_index(index, file_path)


def fetch_clauses(file_path: str) -> list:
    """Extract clauses from the document. Placeholder implementation."""
    text = convert_pdf_to_text(file_path)
    embeddings = embed_texts([text])
    index = create_faiss_index(embeddings)
    # For simplicity: split document into paragraphs as "clauses". Replace with real clause extraction logic.
    # Keep the FAISS index saved for later retrieval/search, but do not return it here
    save_faiss_index(index, "faiss_index.idx")
    raw_clauses = [p.strip() for p in text.split('\n\n') if p.strip()]
    # If splitting produced nothing, fallback to the whole text as a single clause  
    if not raw_clauses:
        raw_clauses = [text]
    return raw_clauses

