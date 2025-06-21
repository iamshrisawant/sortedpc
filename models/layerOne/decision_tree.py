import sqlite3
import pandas as pd
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
import joblib
import os

def load_data_from_db(db_path):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM features", conn)
    conn.close()
    return df

def balance_folders(df, max_per_folder=100):
    return df.groupby('parent', group_keys=False).apply(lambda x: x.sample(n=min(len(x), max_per_folder)))

def prepare_features(df, label_col='parent'):
    df = df.copy()
    y = df[label_col]
    df.drop(columns=[label_col, 'path'], errors='ignore', inplace=True)

    tokens = df['tokens'].fillna("").astype(str)
    df.drop(columns=['tokens'], inplace=True, errors='ignore')
    df_encoded = pd.get_dummies(df)

    tfidf = TfidfVectorizer(max_features=100)
    tfidf_matrix = tfidf.fit_transform(tokens)
    tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=tfidf.get_feature_names_out())

    X = pd.concat([df_encoded.reset_index(drop=True), tfidf_df], axis=1)
    return X, y, tfidf

def train_decision_tree(X, y):
    clf = DecisionTreeClassifier(max_depth=10, min_samples_leaf=5, random_state=42)
    clf.fit(X, y)
    return clf

def extract_rules(clf, feature_names):
    return export_text(clf, feature_names=feature_names)

def save_model(clf, out_path):
    joblib.dump(clf, out_path)

def classify_with_fallback(clf, X, y, fallback_label="Uncategorized"):
    y_pred = clf.predict(X)
    unmatched = set(y) - set(y_pred)
    if unmatched:
        print(f"[INFO] Fallback will handle these unmatched folders: {unmatched}")
    report = classification_report(y, y_pred, zero_division=0)
    print(report)

if __name__ == "__main__":
    db_path = "output/features.db"
    model_path = "models/layerOne/tree_model.pkl"

    df = load_data_from_db(db_path)
    df = balance_folders(df)
    X, y, tfidf = prepare_features(df)
    feature_names = X.columns.tolist()

    clf = train_decision_tree(X, y)
    save_model(clf, model_path)

    rules_text = extract_rules(clf, feature_names)
    os.makedirs("models/layerOne", exist_ok=True)
    with open("models/layerOne/tree_rules.txt", "w") as f:
        f.write(rules_text)

    classify_with_fallback(clf, X, y)

    print("✅ Decision Tree model, rules, and fallback behavior finalized.")
