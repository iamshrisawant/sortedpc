import numpy as np
import faiss
import json
from typing import List, Tuple

class Retriever:
    def __init__(self, index_path: str, meta_path: str):
        self.index = faiss.read_index(index_path)
        with open(meta_path, "r") as f:
            self.meta = json.load(f)

    def search(self, embedding: List[float], k: int = 5) -> List[Tuple[str, float]]:
        query = np.array([embedding]).astype("float32")
        distances, indices = self.index.search(query, k)
        results = []
        for i, dist in zip(indices[0], distances[0]):
            if i != -1:
                results.append((self.meta[i], float(dist)))
        return results
