# data/storage.py

import sqlite3
import os
import json

def init_db(db_path="output/features.db"):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS features (
            path TEXT PRIMARY KEY,
            name TEXT,
            parent TEXT,
            date TEXT,
            type TEXT,
            tokens TEXT
        )
    ''')
    conn.commit()
    return conn

def insert_feature(conn, metadata):
    """
    metadata["tokens"] may be a list; we JSON‑serialize it here.
    """
    tokens_serialized = json.dumps(metadata["tokens"], ensure_ascii=False)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO features (path, name, parent, date, type, tokens)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        metadata["path"],
        metadata["name"],
        metadata["parent"],
        metadata["date"],
        metadata["type"],
        tokens_serialized
    ))
    conn.commit()
