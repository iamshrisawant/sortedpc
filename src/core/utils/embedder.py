import logging
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer

# --- Logger Setup ---
logger = logging.getLogger(__name__)

# --- Load SentenceTransformer model globally ---
_model = SentenceTransformer("all-MiniLM-L6-v2")


def get_embedding_dim() -> int:
    """
    Returns the dimensionality of embeddings produced by the model.
    """
    return _model.get_sentence_embedding_dimension()


def embed_texts(chunks: List[str]) -> List[List[float]]:
    """
    Generates sentence embeddings for a list of text chunks.

    Args:
        chunks (List[str]): Text chunks to embed.

    Returns:
        List[List[float]]: 2D list of float embeddings (one per chunk).
    """
    if not chunks:
        logger.warning("[Embedder] No chunks provided for embedding.")
        return []

    logger.info(f"[Embedder] Generating embeddings for {len(chunks)} chunk(s)...")

    try:
        embeddings = _model.encode(chunks, show_progress_bar=False)

        if isinstance(embeddings, np.ndarray):
            if embeddings.ndim == 1:
                embeddings = embeddings.reshape(1, -1)
            return embeddings.tolist()

        raise TypeError("[Embedder] Model output was not a NumPy array.")

    except Exception as e:
        logger.error(f"[Embedder] Failed to generate embeddings: {repr(e)}")
        return []
