# src/core/utils/embedder.py

from typing import List
from sentence_transformers import SentenceTransformer
from loguru import logger
import re

_MODEL_NAME = "all-MiniLM-L6-v2"

try:
    _embedder = SentenceTransformer(_MODEL_NAME)
except Exception as e:
    logger.error(f"[Embedder] Failed to load model '{_MODEL_NAME}': {e}")
    raise


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def embed_texts(texts: List[str]) -> List[List[float]]:
    clean_inputs = []
    seen = set()

    for t in texts:
        if not isinstance(t, str):
            continue
        cleaned = clean_text(t)
        if len(cleaned) >= 3 and cleaned not in seen:
            seen.add(cleaned)
            clean_inputs.append(cleaned)

    if not clean_inputs:
        logger.warning("[Embedder] No valid text chunks to embed")
        return []

    logger.debug(f"[Embedder] Embedding {len(clean_inputs)} chunk(s)...")
    try:
        return _embedder.encode(clean_inputs, convert_to_numpy=True).tolist()
    except Exception as e:
        logger.error(f"[Embedder] Embedding failed: {e}")
        return []
