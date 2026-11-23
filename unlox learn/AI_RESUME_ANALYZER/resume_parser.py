"""
resume_parser.py
Module 1 & 2 (partial): Resume Upload + Text Extraction

Responsible for pulling raw text out of an uploaded resume file.
Supports PDF (via pypdf) and DOCX (via python-docx).
"""

from __future__ import annotations
import io
from pathlib import Path

from pypdf import PdfReader
from docx import Document

MAX_FILE_SIZE_MB = 5
ALLOWED_EXTENSIONS = {".pdf", ".docx"}


class ResumeParsingError(Exception):
    """Raised when a resume file cannot be read or is invalid."""


def validate_file(filename: str, file_size_bytes: int) -> None:
    """Validate file extension and size before attempting extraction."""
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ResumeParsingError(
            f"Unsupported file type '{ext}'. Please upload a PDF or DOCX file."
        )
    size_mb = file_size_bytes / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise ResumeParsingError(
            f"File is too large ({size_mb:.1f} MB). Maximum allowed size is {MAX_FILE_SIZE_MB} MB."
        )


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from every page of a PDF resume."""
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
    except Exception as exc:
        raise ResumeParsingError(f"Could not read PDF file: {exc}") from exc

    pages_text = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages_text.append(text)

    full_text = "\n".join(pages_text).strip()
    if not full_text:
        raise ResumeParsingError(
            "No extractable text was found in this PDF. It may be a scanned "
            "image — try a text-based PDF or a DOCX file instead."
        )
    return full_text


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from every paragraph (and table cell) of a DOCX resume."""
    try:
        doc = Document(io.BytesIO(file_bytes))
    except Exception as exc:
        raise ResumeParsingError(f"Could not read DOCX file: {exc}") from exc

    parts = [p.text for p in doc.paragraphs if p.text.strip()]

    # Also pull text out of any tables (common in resume templates).
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text.strip():
                    parts.append(cell.text)

    full_text = "\n".join(parts).strip()
    if not full_text:
        raise ResumeParsingError("No extractable text was found in this DOCX file.")
    return full_text


def parse_resume(filename: str, file_bytes: bytes) -> str:
    """
    Main entry point: validates and extracts text from a resume file.

    Args:
        filename: original name of the uploaded file (used to detect type).
        file_bytes: raw bytes of the uploaded file.

    Returns:
        Extracted raw text (not yet cleaned).
    """
    validate_file(filename, len(file_bytes))
    ext = Path(filename).suffix.lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_bytes)
    elif ext == ".docx":
        return extract_text_from_docx(file_bytes)
    else:
        # Should be unreachable because validate_file already checked this.
        raise ResumeParsingError(f"Unsupported file type '{ext}'.")
