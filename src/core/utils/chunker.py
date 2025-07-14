import logging
from typing import List

logger = logging.getLogger(__name__)

def chunk_text(text: str, max_chunk_size: int = 300, overlap: int = 50) -> List[str]:
    """
    Splits the input text into overlapping word-based chunks.
    
    Args:
        text (str): The cleaned text to be chunked.
        max_chunk_size (int): Maximum number of words per chunk.
        overlap (int): Number of words to overlap between consecutive chunks.
    
    Returns:
        List[str]: List of text chunks.
    """
    if not text.strip():
        logger.warning("[Chunker] Empty text received, returning 0 chunks.")
        return []

    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = min(start + max_chunk_size, len(words))
        chunk = words[start:end]
        chunks.append(" ".join(chunk))
        start += max_chunk_size - overlap

    logger.info(f"[Chunker] Chunked text into {len(chunks)} chunk(s) | Chunk size: {max_chunk_size} | Overlap: {overlap}")
    return chunks
