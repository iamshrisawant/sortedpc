# src/core/utils/retriever.py

import json
import numpy as np
import faiss
from pathlib import Path
from typing import List, Dict, Tuple
from loguru import logger


class Retriever:
    def __init__(self, index_path: str, meta_path: str):
        self.index_path = Path(index_path)
        self.meta_path = Path(meta_path)

        if not self.index_path.exists():
            raise FileNotFoundError(f"[Retriever] Missing index: {self.index_path}")
        if not self.meta_path.exists():
            raise FileNotFoundError(f"[Retriever] Missing metadata: {self.meta_path}")

        self.index = faiss.read_index(str(self.index_path))
        with self.meta_path.open("r", encoding="utf-8") as f:
            self.meta: List[Dict] = json.load(f)

        if len(self.meta) != self.index.ntotal:
            raise ValueError(f"[Retriever] Metadata count ({len(self.meta)}) ≠ index entries ({self.index.ntotal})")

        logger.info(f"[Retriever] Index loaded with {self.index.ntotal} vectors")

    def search(self, embedding: List[float], k: int = 5) -> List[Tuple[Dict, float]]:
        if self.index.ntotal == 0:
            logger.warning("[Retriever] Empty index")
            return []

        query = np.array([embedding], dtype="float32")
        if query.shape[1] != self.index.d:
            raise ValueError(f"[Retriever] Query dim {query.shape[1]} ≠ index dim {self.index.d}")

        distances, indices = self.index.search(query, k)
        results = []

        for idx, dist in zip(indices[0], distances[0]):
            if 0 <= idx < len(self.meta):
                results.append((self.meta[idx], float(dist)))
            else:
                logger.warning(f"[Retriever] Invalid index {idx} in results")

        logger.debug(f"[Retriever] Top-{len(results)} retrieved")
        return results

    def get_text_snippets(self, results: List[Tuple[Dict, float]]) -> List[Tuple[str, str]]:
        snippets = []
        for meta, _ in results:
            folder = meta.get("folder")
            filename = meta.get("filename")
            chunk_text = meta.get("chunk_text", "").strip()

            if folder and filename and chunk_text:
                full_path = str(Path("organized_folders") / folder / filename)
                snippets.append((full_path, chunk_text))

        return snippets
