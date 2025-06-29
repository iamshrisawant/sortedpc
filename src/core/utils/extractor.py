from pathlib import Path
from typing import List, Tuple
import pdfplumber
import docx
import openpyxl
from pptx import Presentation
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
import logging

from loguru import logger

VALID_EXTENSIONS = {".pdf", ".docx", ".pptx", ".xlsx", ".txt", ".html"}

def extract_text_from_pdf(file_path: Path) -> str:
    try:
        with pdfplumber.open(file_path) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    except:
        return extract_text_from_pdf_fallback(file_path)

def extract_text_from_pdf_fallback(file_path: Path) -> str:
    try:
        doc = fitz.open(file_path)
        return "\n".join(page.get_text() for page in doc)
    except:
        return ""

def extract_text_from_docx(file_path: Path) -> str:
    return "\n".join(p.text for p in docx.Document(file_path).paragraphs)

def extract_text_from_pptx(file_path: Path) -> str:
    prs = Presentation(file_path)
    text = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text.append(shape.text)
    return "\n".join(text)

def extract_text_from_xlsx(file_path: Path) -> str:
    wb = openpyxl.load_workbook(file_path, data_only=True)
    text = []
    for sheet in wb:
        for row in sheet.iter_rows(values_only=True):
            text.append(" ".join(str(cell) for cell in row if cell))
    return "\n".join(text)

def extract_text_from_txt(file_path: Path) -> str:
    return file_path.read_text(errors="ignore")

def extract_text_from_html(file_path: Path) -> str:
    html = file_path.read_text(errors="ignore")
    return BeautifulSoup(html, "html.parser").get_text()

def extract_text(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
    try:
        if suffix == ".pdf":
            return extract_text_from_pdf(file_path)
        elif suffix == ".docx":
            return extract_text_from_docx(file_path)
        elif suffix == ".pptx":
            return extract_text_from_pptx(file_path)
        elif suffix == ".xlsx":
            return extract_text_from_xlsx(file_path)
        elif suffix == ".txt":
            return extract_text_from_txt(file_path)
        elif suffix == ".html":
            return extract_text_from_html(file_path)
    except Exception as e:
        logger.warning(f"Failed to extract: {file_path.name} | {e}")
    return ""

def find_documents(base_dir: Path) -> List[Tuple[Path, str]]:
    documents = []
    for file_path in base_dir.rglob("*"):
        if file_path.suffix.lower() in VALID_EXTENSIONS:
            content = extract_text(file_path).strip()
            if content:
                documents.append((file_path, content))
    return documents