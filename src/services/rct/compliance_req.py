from .document import *

def extract_compliance_req_from_document(file_path: str) -> list:
    text = convert_pdf_to_text(file_path)
    embeddings = embed_texts([text])
    index = create_faiss_index(embeddings)
    # For simplicity, returning dummy clauses; in real scenarios, implement actual extraction logic
    save_faiss_index(index, "faiss_index.idx")
    return index

