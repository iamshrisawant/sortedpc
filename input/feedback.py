import sqlite3
import pandas as pd

DB_PATH = "data/features.db"

def show_recent_predictions(limit=10):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(f"""
        SELECT id, name, predicted_folder, timestamp
        FROM results
        ORDER BY timestamp DESC
        LIMIT {limit}
    """, conn)
    conn.close()

    if df.empty:
        print("[INFO] No prediction results found.")
        return None

    print("\n[INFO] Recent Predictions:")
    print(df.to_string(index=False))
    return df

def update_prediction(record_id, new_label):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE results
        SET predicted_folder = ?
        WHERE id = ?
    """, (new_label, record_id))

    conn.commit()
    conn.close()
    print(f"[SUCCESS] Updated prediction to '{new_label}' for record ID {record_id}")

def main():
    df = show_recent_predictions()

    if df is None or df.empty:
        return

    try:
        record_id = int(input("\nEnter the ID of the prediction you want to correct: "))
        if record_id not in df["id"].values:
            print("[ERROR] Invalid ID selected.")
            return

        new_label = input("Enter the correct folder label: ").strip()
        if not new_label:
            print("[ERROR] Empty label is not allowed.")
            return

        update_prediction(record_id, new_label)

    except Exception as e:
        print(f"[ERROR] Failed to update prediction: {e}")

if __name__ == "__main__":
    main()
