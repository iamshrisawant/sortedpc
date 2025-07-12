from pathlib import Path
from typing import Callable, Dict, List, Tuple
import hashlib
import re

import pdfplumber
import docx
import openpyxl
import fitz
from pptx import Presentation
from bs4 import BeautifulSoup
from loguru import logger

VALID_EXTENSIONS = {".pdf", ".docx", ".pptx", ".xlsx", ".txt", ".html"}
MIN_CONTENT_CHARS = 50

def extract_pdf(path: Path) -> str:
    try:
        with pdfplumber.open(path) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
            text = "\n".join(pages)
            if len(text.strip()) >= MIN_CONTENT_CHARS:
                return text
    except Exception as e:
        logger.warning(f"[PDF] Primary failed for {path.name}: {e}")
    return extract_pdf_fallback(path)

def extract_pdf_fallback(path: Path) -> str:
    try:
        doc = fitz.open(path)
        return "\n".join(page.get_text() for page in doc)
    except Exception as e:
        logger.error(f"[PDF-Fallback] Failed for {path.name}: {e}")
        return ""

def extract_docx(path: Path) -> str:
    try:
        return "\n".join(p.text for p in docx.Document(path).paragraphs)
    except Exception as e:
        logger.error(f"[DOCX] Failed for {path.name}: {e}")
        return ""

def extract_pptx(path: Path) -> str:
    try:
        prs = Presentation(path)
        return "\n".join(
            shape.text.strip()
            for slide in prs.slides
            for shape in slide.shapes
            if hasattr(shape, "text") and shape.text.strip()
        )
    except Exception as e:
        logger.error(f"[PPTX] Failed for {path.name}: {e}")
        return ""

def extract_xlsx(path: Path) -> str:
    try:
        wb = openpyxl.load_workbook(path, data_only=True)
        return "\n".join(
            " ".join(str(cell) for cell in row if cell)
            for sheet in wb.worksheets
            for row in sheet.iter_rows(values_only=True)
        )
    except Exception as e:
        logger.error(f"[XLSX] Failed for {path.name}: {e}")
        return ""

def extract_txt(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        logger.error(f"[TXT] Failed for {path.name}: {e}")
        return ""

def extract_html(path: Path) -> str:
    try:
        html = path.read_text(encoding="utf-8", errors="ignore")
        return BeautifulSoup(html, "html.parser").get_text()
    except Exception as e:
        logger.error(f"[HTML] Failed for {path.name}: {e}")
        return ""

EXTENSION_DISPATCH: Dict[str, Callable[[Path], str]] = {
    ".pdf": extract_pdf,
    ".docx": extract_docx,
    ".pptx": extract_pptx,
    ".xlsx": extract_xlsx,
    ".txt": extract_txt,
    ".html": extract_html,
}

def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

def extract_text(file_path: Path) -> str:
    ext = file_path.suffix.lower()
    extractor = EXTENSION_DISPATCH.get(ext)
    if not extractor:
        logger.warning(f"[Unsupported] Skipping unsupported file: {file_path.name} ({ext})")
        return ""
    raw = extractor(file_path)
    cleaned = clean_text(raw)
    logger.debug(f"[Extract] {file_path.name} → {len(cleaned)} chars")
    return cleaned

def compute_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def find_documents(base_dir: Path, min_chars: int = MIN_CONTENT_CHARS) -> List[Tuple[Path, str]]:
    documents: List[Tuple[Path, str]] = []
    for path in base_dir.rglob("*"):
        if path.suffix.lower() not in VALID_EXTENSIONS:
            continue
        text = extract_text(path)
        if len(text) >= min_chars:
            documents.append((path, text))
        else:
            logger.debug(f"[Skip] {path.name} — too short ({len(text)} chars)")
    logger.info(f"[Discover] {len(documents)} valid documents in {base_dir}")
    return documents
