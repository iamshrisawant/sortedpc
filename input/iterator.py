# input/iterator.py
import os
import sys
from data.pipeline import run_pipeline

VALID_EXTENSIONS = {'.txt', '.pdf', '.docx', '.pptx', '.xlsx', '.html'}

def process_folder(root_path, verbose=True):
    if verbose:
        print(f"[INFO] Scanning folder: {root_path}")
    for dirpath, _, filenames in os.walk(root_path):
        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext in VALID_EXTENSIONS:
                file_path = os.path.join(dirpath, fname)
                if verbose:
                    print(f"[INFO] Processing file: {file_path}")
                run_pipeline(file_path, verbose=verbose)
    if verbose:
        print("[SUCCESS] All valid files processed.")

if __name__ == "__main__":
    folder = input("Enter the path to the organized folder: ").strip()
    if folder and os.path.exists(folder):
        process_folder(folder, verbose=True)
    else:
        print("[ERROR] Provided path is invalid.")
