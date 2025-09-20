from .document import *

def extract_compliance_req_from_document(file_path: str) -> list:
    text = convert_pdf_to_text(file_path)
    embeddings = embed_texts([text])
    index = create_faiss_index(embeddings)
    # For simplicity: split document into paragraphs as "clauses". Replace with real clause extraction logic.
    # Keep the FAISS index saved for later retrieval/search, but do not return it here.
    save_faiss_index(index, "faiss_index.idx")

    # Naive clause extraction: split by two or more newlines or by sentences if needed.
    raw_clauses = [p.strip() for p in text.split('\n\n') if p.strip()]
    # If splitting produced nothing, fallback to the whole text as a single clause
    if not raw_clauses:
        raw_clauses = [text]

    return raw_clauses

