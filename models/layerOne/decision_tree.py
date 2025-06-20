import sqlite3
import pandas as pd
from sklearn.tree import DecisionTreeClassifier, export_text
import joblib
import os

def load_data_from_db(db_path):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM features", conn)
    conn.close()
    return df

def train_decision_tree(df, label_col='parent'):
    print("[i] Original columns:")
    print(df.dtypes)

    X = df.drop(columns=[label_col, 'path'], errors='ignore')

    # Encode all categorical/object features to dummy vars
    X_encoded = pd.get_dummies(X)

    if X_encoded.empty:
        raise ValueError("[!] No features after encoding. Check your feature builder.")

    y = df[label_col]

    clf = DecisionTreeClassifier(max_depth=10, random_state=42)
    clf.fit(X_encoded, y)

    return clf, X_encoded.columns.tolist()

def save_model(clf, out_path):
    joblib.dump(clf, out_path)

def extract_rules(clf, feature_names):
    return export_text(clf, feature_names=feature_names)

if __name__ == "__main__":
    db_path = "output/features.db"
    model_path = "models/layerOne/tree_model.pkl"

    df = load_data_from_db(db_path)
    clf, feature_names = train_decision_tree(df)
    save_model(clf, model_path)

    rules_text = extract_rules(clf, feature_names)
    with open("models/layerOne/tree_rules.txt", "w") as f:
        f.write(rules_text)

    print("✅ Decision tree model and rules saved.")
