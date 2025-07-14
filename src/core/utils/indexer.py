import faiss
import json
from pathlib import Path
from typing import List
import numpy as np
import logging

from src.core.utils.paths import get_faiss_index_path, get_faiss_metadata_path

logger = logging.getLogger(__name__)


def index_file(
    embedding: List[List[float]],
    file_path: str,
    file_name: str,
    parent_folder: str,
    file_type: str,
    content_hash: str = ""
) -> None:
    """
    Indexes embeddings of a file and appends metadata.
    
    Args:
        embedding (List[List[float]]): List of chunk embeddings.
        file_path (str): Full resolved path to file.
        file_name (str): File stem (name without extension).
        parent_folder (str): Folder the file belongs to.
        file_type (str): File extension/type (e.g., 'pdf').
        content_hash (str): Optional hash of file content.
    """
    if not embedding:
        logger.warning("[Indexer] No embeddings provided.")
        return

    vecs = np.array(embedding).astype("float32")
    dim = vecs.shape[1]

    index_path = get_faiss_index_path()
    meta_path = get_faiss_metadata_path()

    # Load or initialize FAISS index
    if index_path.exists():
        index = faiss.read_index(str(index_path))
        if index.d != dim:
            raise ValueError(f"[Indexer] Dimension mismatch: {index.d} (index) vs {dim} (embedding).")
        logger.debug(f"[Indexer] Loaded existing FAISS index: {index_path}")
    else:
        index = faiss.IndexFlatL2(dim)
        logger.debug(f"[Indexer] Created new FAISS index (dim={dim})")

    # Add vectors and write index
    index.add(vecs)
    faiss.write_index(index, str(index_path))
    logger.info(f"[Indexer] Indexed {len(embedding)} chunk(s) for: {file_name}")

    # Append metadata
    with meta_path.open("a", encoding="utf-8") as f:
        for i in range(len(embedding)):
            metadata_entry = {
                "file_path": file_path,
                "file_name": file_name,
                "parent_folder": parent_folder,
                "file_type": file_type,
                "content_hash": content_hash,
                "chunk_index": i
            }
            f.write(json.dumps(metadata_entry) + "\n")
    logger.debug(f"[Indexer] Appended metadata for {file_name} to {meta_path}")
