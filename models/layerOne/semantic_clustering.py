# semantic_clustering.py
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import numpy as np
from collections import Counter

def load_rules(path):
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def cluster_rules(rules, n_clusters=5):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(rules)

    print(f"\n🔍 Selecting best cluster count (2–{n_clusters})...")
    best_score = -1
    best_k = 2
    for k in range(2, n_clusters + 1):
        km = KMeans(n_clusters=k, random_state=42)
        labels = km.fit_predict(embeddings)
        score = silhouette_score(embeddings, labels)
        if score > best_score:
            best_score = score
            best_k = k

    print(f"✅ Best cluster count: {best_k} (silhouette = {best_score:.3f})")
    kmeans = KMeans(n_clusters=best_k, random_state=42)
    labels = kmeans.fit_predict(embeddings)

    counts = Counter(labels)
    for cid, count in counts.items():
        print(f"[Cluster {cid}] {count} rules")

    return list(zip(rules, labels))

if __name__ == "__main__":
    rules = load_rules("models/layer1/generalized_rules.txt")
    clustered = cluster_rules(rules)

    with open("models/layer1/clustered_rules.txt", "w", encoding="utf-8") as f:
        for rule, label in clustered:
            f.write(f"[Cluster {label}] {rule}\n")

    print("✅ Rules clustered and saved with coverage stats.")
