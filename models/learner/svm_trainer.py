import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import numpy as np
import os

DB_PATH = "features.db"
MODEL_PATH = "models/learner/svm_model.joblib"
ENCODER_PATH = "models/learner/label_encoder.joblib"
VECTORIZER_PATH = "models/learner/tfidf_vectorizer.joblib"

def load_data_from_db():
    print("[INFO] Loading data from features.db...")
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT tokens, parent_folder FROM file_features", conn)
    conn.close()
    return df

def train_svm():
    df = load_data_from_db()

    print("[INFO] Vectorizing text with TF-IDF...")
    tfidf = TfidfVectorizer()
    X = tfidf.fit_transform(df["tokens"])

    print("[INFO] Encoding labels...")
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(df["parent_folder"])

    print("[INFO] Splitting dataset...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("[INFO] Training SVM (LinearSVC)...")
    model = LinearSVC(max_iter=1000)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    print("\n[RESULT] Classification Report:\n")
    all_class_indices = np.arange(len(label_encoder.classes_))
    print(classification_report(
        y_test,
        y_pred,
        labels=all_class_indices,
        target_names=label_encoder.classes_,
        zero_division=0
    ))

    joblib.dump(model, MODEL_PATH)
    joblib.dump(label_encoder, ENCODER_PATH)
    joblib.dump(tfidf, VECTORIZER_PATH)

    print(f"[SUCCESS] Model saved as {os.path.basename(MODEL_PATH)}")
    print(f"[SUCCESS] Label encoder saved as {os.path.basename(ENCODER_PATH)}")
    print(f"[SUCCESS] TF-IDF vectorizer saved.")
    print("[INFO] SVM training completed successfully.")

if __name__ == "__main__":
    train_svm()
