# data/pipeline.py
import sys
from extractor import extract_metadata
from tokenizer import tokenize_file
from builder import init_db, insert_features

def run_pipeline(file_path, verbose=True):
    if verbose:
        print(f"[INFO] Starting pipeline for: {file_path}")

    if verbose:
        print("[INFO] Extracting metadata...")
    metadata = extract_metadata(file_path)

    if verbose:
        print("[INFO] Tokenizing file...")
    tokens = tokenize_file(file_path)

    if verbose:
        print("[INFO] Initializing database...")
    init_db()

    if verbose:
        print("[INFO] Inserting features into database...")
    insert_features(metadata, tokens)

    if verbose:
        print("[SUCCESS] Pipeline completed for:", file_path)
        print("[RESULT] Metadata:", metadata)
        print("[RESULT] Tokens:", tokens)

if __name__ == "__main__":
    file_path = input("Enter the file path: ").strip()
    if file_path:
        run_pipeline(file_path, verbose=True)
    else:
        print("[ERROR] No file path provided.")