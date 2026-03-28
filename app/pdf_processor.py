"""
PDF Processor Module

Handles PDF extraction, text cleaning, and structuring for Lab Manual content.
"""

import pypdf
import re
from pathlib import Path
from typing import Dict, List, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFProcessor:
    """Process and extract text from PDF lab manuals."""

    def __init__(self, max_file_size: int = 50 * 1024 * 1024):
        """
        Initialize PDFProcessor.

        Args:
            max_file_size: Maximum allowed file size in bytes (default: 50 MB)
        """
        self.max_file_size = max_file_size

    def extract_text(self, pdf_path: str) -> Dict[str, any]:
        """
        Extract text from PDF file.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary containing:
            - 'success': bool indicating if extraction was successful
            - 'num_pages': number of pages extracted
            - 'raw_text': full extracted text
            - 'pages': list of text per page
            - 'error': error message if failed
        """
        try:
            pdf_path = Path(pdf_path)

            # Validate file
            if not pdf_path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {pdf_path}",
                    "num_pages": 0,
                    "raw_text": "",
                    "pages": [],
                }

            if pdf_path.stat().st_size > self.max_file_size:
                return {
                    "success": False,
                    "error": f"File too large. Max size: {self.max_file_size / 1024 / 1024:.1f} MB",
                    "num_pages": 0,
                    "raw_text": "",
                    "pages": [],
                }

            # Extract text from PDF
            pages = []
            raw_text = ""

            with open(pdf_path, "rb") as file:
                reader = pypdf.PdfReader(file)
                num_pages = len(reader.pages)

                for page_num, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    pages.append(page_text)
                    raw_text += f"\n--- Page {page_num + 1} ---\n{page_text}"

            logger.info(f"Successfully extracted {num_pages} pages from {pdf_path.name}")

            return {
                "success": True,
                "num_pages": num_pages,
                "raw_text": raw_text,
                "pages": pages,
                "error": None,
            }

        except Exception as e:
            logger.error(f"Error extracting PDF: {str(e)}")
            return {
                "success": False,
                "error": f"Error extracting PDF: {str(e)}",
                "num_pages": 0,
                "raw_text": "",
                "pages": [],
            }

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.

        Args:
            text: Raw extracted text

        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove special characters but keep essential punctuation
        text = re.sub(r"[^\w\s.,;:!?\-\n()]", "", text)

        # Fix spacing around punctuation
        text = re.sub(r"\s+([.,;:!?])", r"\1", text)

        # Convert multiple newlines to double newline
        text = re.sub(r"\n\n+", "\n\n", text)

        # Strip leading/trailing whitespace
        text = text.strip()

        return text

    def chunk_text(
        self, text: str, chunk_size: int = 500, overlap: int = 50
    ) -> List[str]:
        """
        Split text into chunks for processing.

        Args:
            text: Text to chunk
            chunk_size: Characters per chunk
            overlap: Character overlap between chunks

        Returns:
            List of text chunks
        """
        if not text:
            return []

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)

            # Move start position considering overlap
            start = end - overlap

        return chunks

    def process_pdf(
        self, pdf_path: str, clean: bool = True, chunk: bool = False
    ) -> Dict[str, any]:
        """
        Complete PDF processing pipeline.

        Args:
            pdf_path: Path to PDF file
            clean: Whether to clean the text
            chunk: Whether to chunk the text

        Returns:
            Dictionary with processed PDF data
        """
        # Extract text
        result = self.extract_text(pdf_path)

        if not result["success"]:
            return result

        # Clean text if requested
        if clean:
            cleaned_text = self.clean_text(result["raw_text"])
            result["cleaned_text"] = cleaned_text
        else:
            result["cleaned_text"] = result["raw_text"]

        # Chunk text if requested
        if chunk:
            chunks = self.chunk_text(result["cleaned_text"])
            result["chunks"] = chunks
            result["num_chunks"] = len(chunks)

        return result

    def extract_metadata(self, pdf_path: str) -> Dict[str, any]:
        """
        Extract PDF metadata.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with metadata
        """
        try:
            pdf_path = Path(pdf_path)

            with open(pdf_path, "rb") as file:
                reader = pypdf.PdfReader(file)
                metadata = reader.metadata

                return {
                    "title": metadata.title if metadata else None,
                    "author": metadata.author if metadata else None,
                    "subject": metadata.subject if metadata else None,
                    "creator": metadata.creator if metadata else None,
                    "pages": len(reader.pages),
                    "file_name": pdf_path.name,
                    "file_size": pdf_path.stat().st_size / 1024,  # in KB
                }
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
            return {"error": str(e)}

    def get_text_stats(self, text: str) -> Dict[str, any]:
        """
        Calculate statistics about the text.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with text statistics
        """
        words = text.split()
        sentences = re.split(r"[.!?]+", text)

        return {
            "character_count": len(text),
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "avg_word_length": (
                len(text) / len(words) if words else 0
            ),
            "avg_sentence_length": (
                len(words) / len(sentences) if sentences else 0
            ),
        }
