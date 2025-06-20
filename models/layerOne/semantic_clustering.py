from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import numpy as np

def load_rules(path):
    with open(path, encoding="utf-8") as f:  # ✅ Use utf-8 here
        rules = [line.strip() for line in f if line.strip()]
    return rules

def cluster_rules(rules, n_clusters=5):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(rules)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(embeddings)
    return list(zip(rules, labels))

if __name__ == "__main__":
    rules = load_rules("models/layer1/generalized_rules.txt")
    clustered = cluster_rules(rules)

    with open("models/layer1/clustered_rules.txt", "w", encoding="utf-8") as f:
        for rule, label in clustered:
            f.write(f"[Cluster {label}] {rule}\n")

    print("Rules clustered and saved.")
