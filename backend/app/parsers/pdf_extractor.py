import logging
import re
from pathlib import Path
from typing import Dict, List, Any
import pypdf

logger = logging.getLogger(__name__)


class PDFExtractor:
    """Handles robust text extraction and validation for lab manual PDFs."""

    def __init__(self, max_file_size_mb: int = 50):
        self.max_bytes = max_file_size_mb * 1024 * 1024

    def extract_pdf_data(self, file_path: str) -> Dict[str, Any]:
        path = Path(file_path)
        if not path.exists():
            return {"success": False, "error": f"File non-existent: {file_path}"}

        file_size_kb = int(path.stat().st_size / 1024)
        if path.stat().st_size > self.max_bytes:
            return {
                "success": False,
                "error": f"File size exceeds maximum limit of {self.max_bytes / 1024 / 1024:.0f}MB"
            }

        try:
            pages_text = []
            full_text_list = []

            with open(path, "rb") as f:
                reader = pypdf.PdfReader(f)
                num_pages = len(reader.pages)

                for page_idx, page in enumerate(reader.pages):
                    text = page.extract_text() or ""
                    cleaned = self.clean_text(text)
                    pages_text.append({
                        "page_number": page_idx + 1,
                        "text": cleaned,
                        "raw_text": text
                    })
                    full_text_list.append(f"--- Page {page_idx + 1} ---\n{cleaned}")

            combined_text = "\n\n".join(full_text_list)
            is_scanned = len(combined_text.strip()) < 100 and num_pages > 0

            return {
                "success": True,
                "num_pages": num_pages,
                "file_size_kb": file_size_kb,
                "pages": pages_text,
                "extracted_text": combined_text,
                "is_scanned": is_scanned,
                "warning": "Document appears to be scanned or contains image-only text." if is_scanned else None
            }

        except Exception as e:
            logger.error(f"Error reading PDF {file_path}: {e}")
            return {"success": False, "error": f"Failed to extract PDF content: {str(e)}"}

    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""
        # Remove null characters and non-printable noise
        text = text.replace('\x00', '')
        # Standardize newlines
        text = re.sub(r'\r\n|\r', '\n', text)
        # Normalize redundant horizontal spaces while preserving newlines
        lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in text.split('\n')]
        return '\n'.join(lines).strip()
