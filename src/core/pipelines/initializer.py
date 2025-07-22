import json
import logging
from pathlib import Path
import faiss

from src.core.utils.paths import (
    get_paths_file,
    get_config_file,
    get_logs_path,
    get_faiss_index_path,
    get_faiss_metadata_path,
    get_unsorted_folder,
    get_data_dir,
)
from src.core.utils.notifier import notify_system_event
from src.core.utils.embedder import get_embedding_dim, load_model  # 🔁 Updated
# ───────────────────────────────────────────────────────────────

# --- Logger Setup ---
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

# --- Default Data ---
DEFAULT_PATHS = {
    "organized_paths": [],
    "watch_paths": []
}

DEFAULT_CONFIG = {
    "faiss_built": False,
    "builder_busy": False,
    "alpha": 0.6,
    "beta": 0.3,
    "gamma": 0.05,
    "delta": 0.05
}

# --- File & Folder Ensurers ---
def ensure_file(path: Path, default_data=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        if path.suffix == ".json":
            path.write_text(json.dumps(default_data or {}, indent=2), encoding="utf-8")
        elif path.suffix == ".jsonl":
            path.write_text("", encoding="utf-8")
        logger.info(f"[Initializer] Created: {path}")

def ensure_unsorted_folder():
    folder = get_unsorted_folder()
    folder.mkdir(parents=True, exist_ok=True)
    logger.info(f"[Initializer] Ensured unsorted folder: {folder}")

def ensure_faiss_files():
    dim = get_embedding_dim()
    index_path = get_faiss_index_path()
    metadata_path = get_faiss_metadata_path()
    data_dir = get_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)

    if not index_path.exists():
        logger.info(f"[Initializer] Creating empty FAISS index at: {index_path} (dim={dim})")
        index = faiss.IndexFlatL2(dim)
        faiss.write_index(index, str(index_path))

    if not metadata_path.exists():
        logger.info(f"[Initializer] Creating empty metadata file at: {metadata_path}")
        metadata_path.write_text("[]", encoding="utf-8")

# --- Reset Logic ---
def reset_all():
    logger.warning("[Initializer] Resetting system state...")

    logs_path = get_logs_path()
    if logs_path.exists():
        logs_path.unlink()
        logger.info("[Initializer] Cleared logs.jsonl")

    data_dir = get_data_dir()
    if data_dir.exists():
        for file in data_dir.iterdir():
            if file.is_file():
                file.unlink()
        logger.info("[Initializer] Cleared data files")
    data_dir.mkdir(parents=True, exist_ok=True)

    get_paths_file().write_text(json.dumps(DEFAULT_PATHS, indent=2), encoding="utf-8")
    get_config_file().write_text(json.dumps(DEFAULT_CONFIG, indent=2), encoding="utf-8")
    get_logs_path().write_text("", encoding="utf-8")

    ensure_faiss_files()
    logger.info("[Initializer] All system files reset.")

# --- Checks ---
def all_critical_files_exist() -> bool:
    return all([
        get_paths_file().exists(),
        get_config_file().exists(),
        get_logs_path().exists(),
        get_faiss_index_path().exists(),
        get_faiss_metadata_path().exists()
    ])

# --- Initialization Entry ---
def initialize(force_reset: bool = False):
    if force_reset or not all_critical_files_exist():
        logger.warning("[Initializer] Missing critical files or reset forced. Performing full reset...")
        reset_all()
    else:
        ensure_file(get_paths_file(), DEFAULT_PATHS)
        ensure_file(get_config_file(), DEFAULT_CONFIG)
        ensure_file(get_logs_path())
        ensure_faiss_files()

    ensure_unsorted_folder()

    # 🔁 Preload model to ensure it's cached before watcher starts
    try:
        load_model(local_only=False)
    except Exception as e:
        logger.error(f"[Initializer] Failed to preload embedding model: {e}")

    logger.info("[Initializer] System initialized.")
    notify_system_event("System Initialized", "SortedPC is ready to use.")

def run_initializer(force_reset: bool = False):
    initialize(force_reset=force_reset)

# --- CLI Entrypoint ---
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Initialize or reset SortedPC system state.")
    parser.add_argument("--reset", action="store_true", help="Force full reset of all data/config/index files.")
    args = parser.parse_args()

    run_initializer(force_reset=args.reset)
