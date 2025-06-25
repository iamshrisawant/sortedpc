import joblib
import os
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.metrics import classification_report
from models.learner.preprocessor import build_features_and_labels

def train_decision_tree(X, y):
    clf = DecisionTreeClassifier(max_depth=10, min_samples_leaf=5, random_state=42)
    clf.fit(X, y)
    return clf

def extract_rules(clf, feature_names):
    return export_text(clf, feature_names=feature_names)

def classify_and_report(clf, X, y, label_encoder):
    y_pred = clf.predict(X)
    decoded_y = label_encoder.inverse_transform(y)
    decoded_pred = label_encoder.inverse_transform(y_pred)

    unmatched = set(decoded_y) - set(decoded_pred)
    if unmatched:
        print(f"[INFO] Fallback will handle these unmatched folders: {unmatched}")

    report = classification_report(decoded_y, decoded_pred, zero_division=0)
    print(report)

if __name__ == "__main__":
    # Use preprocessed MiniLM + metadata feature vectors
    X, y, label_encoder = build_features_and_labels()
    feature_names = [f"f{i}" for i in range(X.shape[1])]  # decision tree doesn't use names directly

    clf = train_decision_tree(X, y)

    os.makedirs("models/layerOne", exist_ok=True)
    joblib.dump(clf, "models/layerOne/tree_model.pkl")
    joblib.dump(label_encoder, "models/layerOne/label_encoder.pkl")

    rules = extract_rules(clf, feature_names)
    with open("models/layerOne/tree_rules.txt", "w") as f:
        f.write(rules)

    classify_and_report(clf, X, y, label_encoder)

    print("✅ Decision Tree model trained using MiniLM + metadata features.")
