import faiss
import numpy as np
from typing import List, Tuple
import json

class Indexer:
    def __init__(self, dim: int):
        self.index = faiss.IndexFlatL2(dim)
        self.meta: List[Tuple[str, str]] = []

    def add(self, vectors: List[List[float]], paths: List[Tuple[str, str]]):
        self.index.add(np.array(vectors).astype("float32"))
        self.meta.extend(paths)

    def save(self, index_path: str, meta_path: str):
        faiss.write_index(self.index, index_path)
        with open(meta_path, "w") as f:
            json.dump(self.meta, f)

    def load(self, index_path: str, meta_path: str):
        self.index = faiss.read_index(index_path)
        with open(meta_path, "r") as f:
            self.meta = json.load(f)
