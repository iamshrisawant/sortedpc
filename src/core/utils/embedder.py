from typing import List
from sentence_transformers import SentenceTransformer
import logging

# Configure logger if needed
logger = logging.getLogger(__name__)

# Load model once globally
_model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_texts(chunks: List[str]) -> List[List[float]]:
    """
    Generates embeddings for a list of text chunks.

    Args:
        chunks (List[str]): Cleaned and chunked text.

    Returns:
        List[List[float]]: Embeddings for each chunk.
    """
    if not chunks:
        return []

    logger.debug(f"[Embedder] Embedding {len(chunks)} chunk(s)...")
    embeddings = _model.encode(chunks, show_progress_bar=False)
    return embeddings.tolist()
