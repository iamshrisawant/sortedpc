# data/builder.py
import sqlite3

def init_db(db_path="features.db"):
    with sqlite3.connect(db_path) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS file_features (
                name TEXT,
                directory TEXT,
                type TEXT,
                size INTEGER,
                created TEXT,
                parent_folder TEXT,
                tokens TEXT
            )
        ''')

def insert_features(metadata, tokens, db_path="features.db"):
    with sqlite3.connect(db_path) as conn:
        conn.execute('''
            INSERT INTO file_features
            (name, directory, type, size, created, parent_folder, tokens)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            metadata['name'], metadata['directory'], metadata['type'], metadata['size'],
            metadata['created'], metadata['parent_folder'], ','.join(tokens)
        ))
