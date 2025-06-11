# db.py

import sqlite3
import json
from pathlib import Path
from typing import List, Dict

import logging
logger = logging.getLogger(__name__)


DB_PATH = Path("file_index.db")

def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    logger.info(f"Initializing database at {DB_PATH}")

    with get_connection() as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS file_records (
                path TEXT PRIMARY KEY,
                name TEXT,
                extension TEXT,
                size_bytes INTEGER,
                created TEXT,
                modified TEXT,
                accessed TEXT,
                parent_dirs TEXT,
                scan_id TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS scan_paths (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS scans (
                scan_id TEXT PRIMARY KEY,
                started_at TEXT,
                completed_at TEXT
            )
        ''')
        # After table creation
        c.execute("CREATE INDEX IF NOT EXISTS idx_files_scan_id ON file_records(scan_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_files_path ON file_records(path)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_scans_started ON scans(started_at)")
        conn.commit()
        logger.info("Tables ensured.")

        

def add_scan_path(path: str):
    with get_connection() as conn:
        conn.execute('INSERT OR IGNORE INTO scan_paths (path) VALUES (?)', (path,))
        conn.commit()
        logger.info(f"Path registered: {path}")

def get_scan_paths() -> List[str]:
    with get_connection() as conn:
        cur = conn.execute('SELECT path FROM scan_paths')
        return [row[0] for row in cur.fetchall()]

def remove_scan_path(path: str):
    with get_connection() as conn:
        logger.warning(f"Attempted to remove non-existent path: {path}")
        conn.execute('DELETE FROM scan_paths WHERE path = ?', (path,))
        conn.commit()

def save_file_record(metadata: Dict):
    """
    Insert or update file metadata based on file path.
    """
    with get_connection() as conn:
        conn.execute('''
            INSERT INTO file_records (
                path, name, extension, size_bytes, created,
                modified, accessed, parent_dirs, scan_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(path) DO UPDATE SET
                name=excluded.name,
                extension=excluded.extension,
                size_bytes=excluded.size_bytes,
                created=excluded.created,
                modified=excluded.modified,
                accessed=excluded.accessed,
                parent_dirs=excluded.parent_dirs,
                scan_id=excluded.scan_id
        ''', (
            metadata['path'],
            metadata['name'],
            metadata['extension'],
            metadata['size_bytes'],
            metadata['created'],
            metadata['modified'],
            metadata['accessed'],
            json.dumps(metadata['parent_dirs']),
            metadata.get('scan_id')
        ))
        conn.commit()

def record_scan(scan_id: str, started_at: str, completed_at: str):
    with get_connection() as conn:
        conn.execute('''
            INSERT OR REPLACE INTO scans (scan_id, started_at, completed_at)
            VALUES (?, ?, ?)
        ''', (scan_id, started_at, completed_at))
        conn.commit()

def get_files_by_scan(scan_id: str) -> List[Dict]:
    with get_connection() as conn:
        cur = conn.execute('SELECT * FROM file_records WHERE scan_id = ?', (scan_id,))
        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]
