# models/learner/preprocessor.py
import sqlite3
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sentence_transformers import SentenceTransformer
import numpy as np

# Load MiniLM embedding model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

CATEGORICAL_COLS = ["type"]
NUMERIC_COLS = ["size"]

def fetch_data(db_path="features.db"):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM file_features", conn)
    conn.close()
    return df

def embed_tokens(tokens):
    joined = tokens.apply(lambda x: ' '.join(x.split(',')))
    return np.vstack(embedder.encode(joined.tolist()))

def encode_metadata(df):
    cat_data = df[CATEGORICAL_COLS].copy()
    enc = OneHotEncoder(sparse_output=False, handle_unknown='ignore')  # use sparse_output=False if on latest sklearn
    cat_encoded = enc.fit_transform(cat_data)
    num_data = df[NUMERIC_COLS].to_numpy()
    return np.hstack([num_data, cat_encoded])

def build_features_and_labels(db_path="features.db"):
    df = fetch_data(db_path)

    # Generate text embeddings
    text_features = embed_tokens(df["tokens"])

    # Encode metadata (numeric + one-hot categorical)
    meta_features = encode_metadata(df)

    # Combine embeddings and metadata
    X = np.hstack([text_features, meta_features])

    # Label encode the target (parent_folder)
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(df["parent_folder"])

    return X, y, label_encoder
