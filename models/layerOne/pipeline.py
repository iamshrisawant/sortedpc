import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from models.layerOne.decision_tree import load_data_from_db, train_decision_tree, save_model, extract_rules
from models.layerOne.pattern_analyzer import generalize_rules
from models.layerOne.semantic_clustering import load_rules, cluster_rules

DB_PATH = "output/features.db"
MODEL_DIR = "models/layerOne"
MODEL_PATH = os.path.join(MODEL_DIR, "tree_model.pkl")
RAW_RULES_PATH = os.path.join(MODEL_DIR, "tree_rules.txt")
GENERALIZED_RULES_PATH = os.path.join(MODEL_DIR, "generalized_rules.txt")
CLUSTERED_RULES_PATH = os.path.join(MODEL_DIR, "clustered_rules.txt")

def ensure_dirs():
    os.makedirs(MODEL_DIR, exist_ok=True)

def run_pipeline():
    ensure_dirs()

    # Step 1: Load data from database
    print("[1] Loading features from DB...")
    df = load_data_from_db(DB_PATH)

    # Step 2: Train decision tree
    print("[2] Training decision tree...")
    clf, feature_names = train_decision_tree(df)
    save_model(clf, MODEL_PATH)

    # Step 3: Extract rules
    print("[3] Extracting decision rules...")
    rules_text = extract_rules(clf, feature_names)
    with open(RAW_RULES_PATH, "w",encoding="utf-8") as f:
        f.write(rules_text)

    # Step 4: Generalize rules
    print("[4] Generalizing rules...")
    generalized = generalize_rules(rules_text)
    with open(GENERALIZED_RULES_PATH, "w", encoding="utf-8") as f:
        f.write(generalized)

    # Step 5: Semantic clustering
    print("[5] Clustering generalized rules...")
    rules = load_rules(GENERALIZED_RULES_PATH)
    clustered = cluster_rules(rules)
    with open(CLUSTERED_RULES_PATH, "w", encoding="utf-8") as f:
        for rule, label in clustered:
            f.write(f"[Cluster {label}] {rule}\n")

    print("✅ Layer 1 pipeline completed.")

if __name__ == "__main__":
    run_pipeline()
