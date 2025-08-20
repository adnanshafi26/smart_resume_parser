import fitz  # PyMuPDF
from docx import Document
import io

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extract text from PDF (bytes) using PyMuPDF."""
    text_parts = []
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page in doc:
            text_parts.append(page.get_text("text"))
    return "\n".join(text_parts)

def extract_text_from_docx_bytes(docx_bytes: bytes) -> str:
    """Extract text from DOCX (bytes) using python-docx."""
    file_like = io.BytesIO(docx_bytes)
    doc = Document(file_like)
    pars = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(pars)
