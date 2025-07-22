# [processor.py] — Patched for Deferred Model Loading

import hashlib
import logging
import re
from pathlib import Path
from typing import Dict, List, Union

import docx
import numpy as np
import pandas as pd
import pdfplumber
from openpyxl import load_workbook
from pptx import Presentation
from sentence_transformers import SentenceTransformer
from nltk.corpus import stopwords

# --- Logger Setup ---
logging.getLogger("pdfminer").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

# --- Globals & Constants ---
STOPWORDS = set(stopwords.words('english'))
MODEL_NAME = "all-MiniLM-L6-v2"

# --- Patched Block: Deferred Model Loading ---
# The model is no longer loaded here. It is set to None.
_model = None
# The embedding dimension is a fixed constant for this model.
# Hardcoding it here avoids loading the model just to check this value.
embedding_dim = 384
# --- End Patched Block ---


# --------------------------------------------------------------------------
# --- TEXT EXTRACTION LOGIC (No changes needed)
# --------------------------------------------------------------------------
def _extract_content(path: Path, file_type: str) -> str:
    """Extracts raw text content from a file."""
    try:
        if file_type == "pdf":
            with pdfplumber.open(path) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages)
        elif file_type == "docx":
            doc = docx.Document(path)
            return "\n".join(p.text for p in doc.paragraphs)
        elif file_type == "pptx":
            prs = Presentation(path)
            return "\n".join(shape.text for slide in prs.slides for shape in slide.shapes if hasattr(shape, "text"))
        elif file_type == "xlsx":
            wb = load_workbook(path, data_only=True)
            return "\n".join(str(cell.value) for ws in wb.worksheets for row in ws.iter_rows() for cell in row if cell.value is not None)
        elif file_type == "csv":
            df = pd.read_csv(path)
            return df.astype(str).to_string(index=False)
        elif file_type in ("txt", "md"):
            return path.read_text(encoding="utf-8", errors="ignore")
        else:
            return ""
    except Exception as e:
        logger.error(f"[Processor] Failed to read {path.name} ({file_type}): {e}")
        return ""

def _clean_text(text: str) -> str:
    """Cleans text by lowercasing, removing punctuation, and filtering stopwords."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    words = text.split()
    filtered = [w for w in words if w not in STOPWORDS]
    return " ".join(filtered)

def _compute_hash(text: str) -> str:
    """Computes a SHA256 hash of the text content."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

# --------------------------------------------------------------------------
# --- TEXT CHUNKING LOGIC (No changes needed)
# --------------------------------------------------------------------------
def _chunk_text(text: str, max_chunk_size: int = 300, overlap: int = 50) -> List[str]:
    """Splits cleaned text into overlapping word-based chunks."""
    if not text.strip():
        return []
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + max_chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        start += max_chunk_size - overlap
    return chunks

# --------------------------------------------------------------------------
# --- EMBEDDING LOGIC (Now with lazy loading)
# --------------------------------------------------------------------------
def _load_model(local_only: bool = True):
    """Lazily loads the SentenceTransformer model when first needed."""
    global _model
    if _model is None:
        try:
            logger.info(f"[Processor] Loading model for the first time: {MODEL_NAME}")
            _model = SentenceTransformer(MODEL_NAME, local_files_only=local_only)
            logger.info("[Processor] Model loaded successfully.")
        except Exception as e:
            logger.error(f"[Processor] Failed to load model: {e}")
            # Raise the exception to prevent the application from continuing in a broken state.
            raise e
    return _model

def _embed_texts(chunks: List[str]) -> List[List[float]]:
    """Generates sentence embeddings for a list of text chunks."""
    if not chunks:
        return []
    try:
        # This will trigger the one-time model load if it hasn't happened yet.
        model = _load_model()
        embeddings = model.encode(chunks, show_progress_bar=False)
        if isinstance(embeddings, np.ndarray):
            return embeddings.tolist()
        return []
    except Exception as e:
        logger.error(f"[Processor] Failed to generate embeddings: {repr(e)}")
        return []

# --------------------------------------------------------------------------
# --- PUBLIC MASTER FUNCTION (No changes needed)
# --------------------------------------------------------------------------
def process_file(file_path: Union[str, Path]) -> Dict:
    """Processes a single file from path to embeddings."""
    path = Path(file_path)
    if not path.is_file():
        return {}
    file_type = path.suffix.lower().lstrip('.')
    raw_content = _extract_content(path, file_type)
    cleaned_content = _clean_text(raw_content)
    chunks = _chunk_text(cleaned_content)
    embeddings = _embed_texts(chunks)
    return {
        "file_path": str(path),
        "file_name": _clean_text(path.stem),
        "parent_folder": path.parent.name,
        "parent_folder_path": str(path.parent.resolve()),
        "file_type": file_type,
        "content_hash": _compute_hash(raw_content),
        "embeddings": embeddings,
    }
