import os
import shutil
import sqlite3

DB_PATH = "data/features.db"

def sort_file(file_path, predicted_label):
    try:
        # Step 1: Get target directory from DB using label
        target_dir = resolve_target_directory(predicted_label)

        if not target_dir:
            print(f"[ERROR] Could not resolve target directory for label: {predicted_label}")
            return

        # Step 2: Create the directory if it doesn't exist
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            print(f"[INFO] Created new directory: {target_dir}")

        # Step 3: Move the file
        file_name = os.path.basename(file_path)
        dest_path = os.path.join(target_dir, file_name)

        shutil.move(file_path, dest_path)
        print(f"[SUCCESS] Moved file to: {dest_path}")

    except Exception as e:
        print(f"[ERROR] Failed to sort file: {e}")

def resolve_target_directory(label):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT directory FROM file_features
            WHERE parent_folder = ?
            LIMIT 1
        """, (label,))
        result = cursor.fetchone()
        conn.close()

        return result[0] if result else None

    except Exception as e:
        print(f"[ERROR] Failed to lookup directory for label '{label}': {e}")
        return None
