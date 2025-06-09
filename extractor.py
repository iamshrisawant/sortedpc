import os
import json
import threading
from pathlib import Path
from datetime import datetime
from config import CONFIG_FILE
from db import insert_metadata_batch

_is_running_event = threading.Event()

def is_extraction_running():
    return _is_running_event.is_set()

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"watch_paths": [], "sweeped_paths": []}
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_config(config_data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config_data, f, indent=4)

def detect_new_paths(watch_paths, sweeped_paths):
    return list(set(watch_paths) - set(sweeped_paths))

def all_files_recursive(folder_path):
    ignore_dirs = {
        ".git", "__pycache__", ".venv", "venv", "env", "build", "dist",
        "node_modules", ".idea", ".vscode", ".mypy_cache", ".pytest_cache",
        ".gradle", ".settings", ".cache"
    }

    ignored_extensions = {
        ".class", ".o", ".so", ".dll", ".pyc", ".lock", ".log", ".tmp", ".bin",
        ".exe", ".out", ".apk", ".a", ".d", ".db-journal"
    }

    allowed_extensions = {
        ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".csv", ".tsv", ".txt",
        ".md", ".json", ".xml", ".yaml", ".yml", ".sql", ".py", ".java",
        ".cpp", ".c", ".js", ".ts", ".html", ".css", ".ipynb", ".r", ".sh"
    }

    files = []
    for root, dirs, filenames in os.walk(folder_path):
        # Remove ignored directories in-place (modifies dirs to prevent os.walk from descending)
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith(".")]

        for filename in filenames:
            path = Path(root) / filename
            ext = path.suffix.lower()

            if path.name.startswith("."):
                continue  # Skip hidden files
            if ext in ignored_extensions:
                continue
            if ext and ext not in allowed_extensions:
                continue

            files.append(path)

    return files

    return [p for p in Path(folder_path).rglob('*') if p.is_file()]

def extract_basic_metadata(file_path):
    try:
        path = Path(file_path)
        stats = path.stat()
        return {
            "file_name": path.name,
            "file_path": str(path.resolve()),
            "extension": path.suffix.lower(),
            "size_bytes": stats.st_size,
            "created_at": datetime.fromtimestamp(stats.st_ctime).isoformat(),
            "modified_at": datetime.fromtimestamp(stats.st_mtime).isoformat(),
            "parent_folder": path.parent.name,
            "depth": len(path.resolve().parts),
            "is_hidden": path.name.startswith("."),
            "download_source": None
        }
    except Exception as e:
        print(f"⚠️ Could not extract metadata from {file_path}: {e}")
        return None

def preview_extracted_data(extracted_data):
    if extracted_data:
        preview = extracted_data[:5]
        print("\n📝 Preview of extracted metadata:")
        for i, entry in enumerate(preview, 1):
            print(f"{i}. {entry['file_name']} ({entry['extension']}, {entry['size_bytes']} bytes)")
        if len(extracted_data) > 5:
            print(f"... and {len(extracted_data) - 5} more entries skipped.\n")

def sweep_path(path, show_preview=False):
    if isinstance(path, list):
        print(f"⚠️ sweep_path() received a list instead of a string: {path}")
        return []

    resolved_path = Path(path).resolve()
    print(f"\n🚀 Sweep started for: {resolved_path}")
    print(f"📂 Exists? {resolved_path.exists()}  | Is Dir? {resolved_path.is_dir()}")

    extracted = []
    for file_path in all_files_recursive(str(resolved_path)):
        metadata = extract_basic_metadata(file_path)
        if metadata:
            extracted.append(metadata)
    if extracted:
        insert_metadata_batch(extracted)

    print(f"✅ Sweep complete for: {path} ({len(extracted)} files)")
    if show_preview:
        preview_extracted_data(extracted)

    return extracted

def extract_from_new_paths():
    if _is_running_event.is_set():
        print("⚠️ Extraction is already running.")
        return []

    _is_running_event.set()
    try:
        config = load_config()
        watch_paths = config.get("watch_paths", [])
        sweeped_paths = config.get("sweeped_paths", [])

        new_paths = detect_new_paths(watch_paths, sweeped_paths)

        if not new_paths:
            print("✅ No new paths to sweep.")
            return []

        all_extracted = []
        for path in new_paths:
            extracted_data = sweep_path(path, show_preview=True)
            all_extracted.extend(extracted_data)
            sweeped_paths.append(path)

        config["sweeped_paths"] = sweeped_paths
        save_config(config)

        print(f"\n📊 Total files extracted: {len(all_extracted)}")
        return all_extracted
    finally:
        _is_running_event.clear()
