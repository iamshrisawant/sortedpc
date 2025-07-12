import json
import numpy as np
import faiss
from typing import List, Dict
from pathlib import Path
from loguru import logger

class Indexer:
    def __init__(self, dim: int):
        self.dim = dim
        self.index = faiss.IndexFlatL2(dim)
        self.meta: List[Dict] = []
        logger.debug(f"[Indexer] Initialized (dim={dim})")

    def add(self, vectors: List[List[float]], metadatas: List[Dict]):
        if not vectors or not metadatas:
            logger.warning("[Indexer] Empty vectors or metadata. Skipping.")
            return

        if len(vectors) != len(metadatas):
            raise ValueError(f"[Indexer] Mismatch: {len(vectors)} vectors vs {len(metadatas)} metadata.")

        np_vectors = np.array(vectors, dtype="float32")
        if np_vectors.ndim != 2 or np_vectors.shape[1] != self.dim:
            raise ValueError(f"[Indexer] Expected shape (*, {self.dim}), got {np_vectors.shape}")

        self.index.add(np_vectors)
        self.meta.extend(metadatas)
        logger.info(f"[Indexer] Added {len(vectors)} vectors. Total: {self.index.ntotal}")

    def save(self, index_path: str, meta_path: str):
        try:
            faiss.write_index(self.index, str(index_path))
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(self.meta, f, indent=2, ensure_ascii=False)
            logger.info(f"[Indexer] Saved index → {index_path}")
            logger.info(f"[Indexer] Saved metadata → {meta_path}")
        except Exception as e:
            logger.error(f"[Indexer] Save failed: {e}")

    def load(self, index_path: str, meta_path: str):
        if not Path(index_path).exists():
            raise FileNotFoundError(f"[Indexer] Index missing: {index_path}")
        if not Path(meta_path).exists():
            raise FileNotFoundError(f"[Indexer] Metadata missing: {meta_path}")

        try:
            self.index = faiss.read_index(str(index_path))
            with open(meta_path, "r", encoding="utf-8") as f:
                self.meta = json.load(f)
            logger.info(f"[Indexer] Loaded index and {len(self.meta)} metadata entries.")
        except Exception as e:
            logger.error(f"[Indexer] Load failed: {e}")
            raise

    def reset(self):
        self.index = faiss.IndexFlatL2(self.dim)
        self.meta.clear()
        logger.info("[Indexer] Index and metadata reset.")

    def get_metadata(self) -> List[Dict]:
        return self.meta

    def size(self) -> int:
        return self.index.ntotal
