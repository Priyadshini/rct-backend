# import pytesseract
import os
# from pdf2image import convert_from_path
import fitz  # PyMuPDF
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


def convert_pdf_to_text(file_path: str) -> str:
    """
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
    
