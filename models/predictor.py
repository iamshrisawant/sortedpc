import os
import joblib
import sqlite3
import datetime
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import OneHotEncoder

from actions.sorter import sort_file

# Constants
MODEL_PATH = "xgb_model.joblib"
ENCODER_PATH = "label_encoder.joblib"
DB_PATH = "data/features.db"
CATEGORICAL_COLS = ["type"]
NUMERIC_COLS = ["size"]

# Load model components
embedder = SentenceTransformer("all-MiniLM-L6-v2")
model = joblib.load(MODEL_PATH)
label_encoder = joblib.load(ENCODER_PATH)

# Dummy fit OneHotEncoder on possible known categories (minimal stateless emulation)
# NOTE: This must match the training set's OneHotEncoder categories to work consistently
# For real use, save the encoder during training and load here
dummy_encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
dummy_encoder.fit([["pdf"], ["docx"], ["pptx"], ["html"], ["txt"]])  # extend as needed

def preprocess_single(metadata, tokens):
    # Token embedding
    joined = ' '.join(tokens)
    token_vec = embedder.encode([joined])  # shape: (1, 384)

    # Metadata encoding
    meta_df = {
        "type": [metadata["type"]],
        "size": [metadata["size"]]
    }
    cat = dummy_encoder.transform([[metadata["type"]]])  # shape: (1, N)
    num = np.array([[metadata["size"]]])  # shape: (1, 1)

    meta_vec = np.hstack([num, cat])  # shape: (1, N+1)

    return np.hstack([token_vec, meta_vec])  # shape: (1, final_dim)

def predict_and_sort(file_path, metadata, tokens):
    print(f"[INFO] Predicting for: {file_path}")

    # Step 1: Preprocess
    X = preprocess_single(metadata, tokens)

    # Step 2: Predict
    y_encoded = model.predict(X)
    predicted_label = label_encoder.inverse_transform(y_encoded)[0]

    print(f"[PREDICTION] Predicted parent folder: {predicted_label}")

    # Step 3: Save result
    persist_result(metadata, tokens, predicted_label)

    # Step 4: Move file
    sort_file(file_path, predicted_label)

def persist_result(metadata, tokens, predicted_label):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            directory TEXT,
            type TEXT,
            size INTEGER,
            created TEXT,
            predicted_folder TEXT,
            tokens TEXT,
            timestamp TEXT
        )
    """)

    cursor.execute("""
        INSERT INTO results (name, directory, type, size, created, predicted_folder, tokens, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        metadata["name"],
        metadata["directory"],
        metadata["type"],
        metadata["size"],
        metadata["created"],
        predicted_label,
        ','.join(tokens),
        datetime.datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()
    print("[DB] Prediction saved to results table.")
