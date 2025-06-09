import sqlite3

DB_FILE = "file_metadata.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

def create_table():
    with get_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS file_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL UNIQUE,
                extension TEXT,
                size_bytes INTEGER,
                created_at TEXT,
                modified_at TEXT,
                parent_folder TEXT,
                depth INTEGER,
                is_hidden INTEGER,
                download_source TEXT,
                organization_status TEXT DEFAULT NULL,
                org_feedback TEXT DEFAULT NULL
            )
        ''')
        conn.commit()

def migrate_add_columns():
    with get_connection() as conn:
        try:
            conn.execute("ALTER TABLE file_metadata ADD COLUMN organization_status TEXT DEFAULT NULL")
        except sqlite3.OperationalError:
            pass
        try:
            conn.execute("ALTER TABLE file_metadata ADD COLUMN org_feedback TEXT DEFAULT NULL")
        except sqlite3.OperationalError:
            pass
        conn.commit()

def insert_metadata_batch(records):
    if not records:
        return
    with get_connection() as conn:
        try:
            conn.executemany('''
                INSERT OR IGNORE INTO file_metadata (
                    file_name, file_path, extension, size_bytes,
                    created_at, modified_at, parent_folder, depth, is_hidden, download_source
                ) VALUES (
                    :file_name, :file_path, :extension, :size_bytes,
                    :created_at, :modified_at, :parent_folder, :depth, :is_hidden, :download_source
                )
            ''', records)
            conn.commit()
        except Exception as e:
            print(f"❌ DB Insert Error: {e}")

# -----------------------------
# Query utilities for main menu
# -----------------------------

def fetch_all_files():
    with get_connection() as conn:
        return conn.execute("SELECT * FROM file_metadata ORDER BY id DESC").fetchall()

def fetch_by_extension(ext):
    with get_connection() as conn:
        return conn.execute("SELECT * FROM file_metadata WHERE extension = ?", (ext,)).fetchall()

def fetch_by_name(name_fragment):
    with get_connection() as conn:
        return conn.execute("SELECT * FROM file_metadata WHERE file_name LIKE ?", (f"%{name_fragment}%",)).fetchall()

def fetch_by_size_range(min_size, max_size):
    with get_connection() as conn:
        return conn.execute("SELECT * FROM file_metadata WHERE size_bytes BETWEEN ? AND ?", (min_size, max_size)).fetchall()

def fetch_hidden_files():
    with get_connection() as conn:
        return conn.execute("SELECT * FROM file_metadata WHERE is_hidden = 1").fetchall()

# -----------------------------
# Learner-specific functions
# -----------------------------

def fetch_unorganized_files():
    with get_connection() as conn:
        return conn.execute('''
            SELECT * FROM file_metadata
            WHERE organization_status IS NULL OR organization_status = 'unorganized'
        ''').fetchall()

def update_folder_org_status(folder, feedback):
    with get_connection() as conn:
        conn.execute('''
            UPDATE file_metadata
            SET org_feedback = ?
            WHERE parent_folder = ?
        ''', (feedback, folder))
        conn.commit()

def update_organization_status_for_folder(folder, status):
    with get_connection() as conn:
        conn.execute('''
            UPDATE file_metadata
            SET organization_status = ?
            WHERE parent_folder = ?
        ''', (status, folder))
        conn.commit()

def fetch_folder_summary():
    with get_connection() as conn:
        return conn.execute('''
            SELECT parent_folder,
                   COUNT(*) as total_files,
                   SUM(CASE WHEN organization_status = 'organized' THEN 1 ELSE 0 END) as organized_count,
                   MAX(org_feedback) as user_feedback
            FROM file_metadata
            GROUP BY parent_folder
            ORDER BY total_files DESC
        ''').fetchall()
