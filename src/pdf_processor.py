import pypdf
import pdfplumber
from typing import List, Dict

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF"""
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_pages(pdf_path: str) -> List[Dict]:
    """Extract pages with metadata"""
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for idx, page in enumerate(pdf.pages):
            pages.append({
                "page_num": idx + 1,
                "text": page.extract_text(),
                "height": page.height,
                "width": page.width
            })
    return pages
