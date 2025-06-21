import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from models.layerOne.decision_tree import (
    load_data_from_db,
    balance_folders,
    prepare_features,
    train_decision_tree,
    save_model,
    extract_rules,
    classify_with_fallback
)
from models.layerOne.pattern_analyzer import generalize_rules
from models.layerOne.semantic_clustering import load_rules, cluster_rules

# --- Paths ---
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

    print("\n[1] 📥 Loading features from DB...")
    df = load_data_from_db(DB_PATH)
    df = balance_folders(df)

    print("[2] 🧪 Preparing features...")
    X, y, _ = prepare_features(df)
    feature_names = X.columns.tolist()

    print("[3] 🌳 Training Decision Tree...")
    clf = train_decision_tree(X, y)
    save_model(clf, MODEL_PATH)

    print("[4] 🧾 Extracting decision rules...")
    rules_text = extract_rules(clf, feature_names)
    with open(RAW_RULES_PATH, "w", encoding="utf-8") as f:
        f.write(rules_text)

    print("[5] 📄 Generalizing rules...")
    generalized = generalize_rules(rules_text)
    with open(GENERALIZED_RULES_PATH, "w", encoding="utf-8") as f:
        f.write(generalized)

    print("[6] 🤖 Semantic clustering...")
    rules = load_rules(GENERALIZED_RULES_PATH)
    clustered = cluster_rules(rules)
    with open(CLUSTERED_RULES_PATH, "w", encoding="utf-8") as f:
        for rule, label in clustered:
            f.write(f"[Cluster {label}] {rule}\n")

    print("[7] 🩺 Auditing fallback classification coverage...")
    classify_with_fallback(clf, X, y)

    print("\n✅ Layer 1 pipeline completed.\n")

if __name__ == "__main__":
    run_pipeline()
