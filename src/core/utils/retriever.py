import faiss
import json
from pathlib import Path
from typing import List, Dict
import numpy as np
import logging

from src.core.utils.paths import get_faiss_index_path, get_faiss_metadata_path

logger = logging.getLogger(__name__)


def retrieve_similar(
    query_embeddings: List[List[float]],
    top_k: int = 10
) -> List[Dict]:
    """
    Retrieves top_k most similar indexed chunks for given embeddings.

    Args:
        query_embeddings (List[List[float]]): New file's chunk embeddings.
        top_k (int): Number of similar results per chunk.

    Returns:
        List[Dict]: List of matches with distance and metadata.
    """
    if not query_embeddings:
        logger.warning("[Retriever] No embeddings provided.")
        return []

    index_path = get_faiss_index_path()
    meta_path = get_faiss_metadata_path()

    if not index_path.exists():
        raise FileNotFoundError(f"[Retriever] FAISS index not found at: {index_path}")
    if not meta_path.exists():
        raise FileNotFoundError(f"[Retriever] Metadata file not found at: {meta_path}")

    # Load index
    index = faiss.read_index(str(index_path))
    query_vecs = np.array(query_embeddings).astype("float32")
    D, I = index.search(query_vecs, top_k)

    # Load metadata
    with meta_path.open("r", encoding="utf-8") as f:
        metadata = [json.loads(line) for line in f]

    results = []
    for query_chunk_idx, (distances, indices) in enumerate(zip(D, I)):
        for distance, index_id in zip(distances, indices):
            if index_id == -1 or index_id >= len(metadata):
                continue
            match = metadata[index_id].copy()
            match.update({
                "distance": float(distance),
                "match_index": index_id,
                "query_chunk": query_chunk_idx
            })
            results.append(match)

    logger.info(f"[Retriever] Retrieved {len(results)} matches for {len(query_embeddings)} query chunks.")
    return results
