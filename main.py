#main.py
import sys
from data.iterator import get_valid_files
from data.feature_builder import build_features

from db.storage import init_db, insert_feature

from models.layerOne.pipeline import run_pipeline

def main(input_dir):
    all_files = get_valid_files(input_dir)
    conn = init_db("output/features.db")

    for file_path in all_files:
        try:
            features = build_features(file_path)
            if features:
                insert_feature(conn, features)
        except Exception as e:
            print(f"[ERROR] Failed to process {file_path}: {e}")

    print(f"\n[SAVED] All features stored in SQLite database.")


if __name__ == "__main__":
    test_path = r"C:\Users\Shriswarup Sawant\Documents\Shriswarup\Acad"
    main(test_path)
    run_pipeline()