import json
import shutil
from pathlib import Path
import logging

from src.core.utils.paths import (
    get_paths_file,
    get_config_file,
    get_logs_path,
    get_faiss_dir,
    get_unsorted_folder
)

from src.core.utils.notifier import notify_system_event


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

# --- Default Data Structures ---
DEFAULT_PATHS = {
    "organized_paths": [],
    "watch_paths": []
}

DEFAULT_CONFIG = {
    "faiss_built": False,
    "builder_busy": False,
    "watcher_online": False,
    "alpha": 0.6,
    "beta": 0.3,
    "gamma": 0.05,
    "delta": 0.05
}


# --- Helpers ---
def ensure_file(path: Path, default_data=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        if path.suffix == ".json":
            with path.open("w", encoding="utf-8") as f:
                json.dump(default_data or {}, f, indent=2)
        elif path.suffix == ".jsonl":
            path.touch()
        logger.info(f"[Initializer] Created: {path}")


def ensure_unsorted_folder():
    folder = get_unsorted_folder()
    folder.mkdir(parents=True, exist_ok=True)
    logger.info(f"[Initializer] Ensured unsorted folder: {folder}")


# --- Reset system (force clear) ---
def reset_all():
    logger.info("[Initializer] Resetting system state...")

    # Delete logs
    logs_path = get_logs_path()
    if logs_path.exists():
        logs_path.unlink()
        logger.info("[Initializer] Cleared logs.jsonl")

    # Delete and recreate FAISS directory
    faiss_dir = get_faiss_dir()
    if faiss_dir.exists():
        shutil.rmtree(faiss_dir)
        logger.info("[Initializer] Deleted FAISS index directory")
    faiss_dir.mkdir(parents=True, exist_ok=True)

    # Recreate config + paths
    with get_paths_file().open("w", encoding="utf-8") as f:
        json.dump(DEFAULT_PATHS, f, indent=2)

    with get_config_file().open("w", encoding="utf-8") as f:
        json.dump(DEFAULT_CONFIG, f, indent=2)

    # Touch empty logs.jsonl
    logs_path.touch()
    logger.info("[Initializer] All data files reset.")


# --- Initialization ---
def initialize(force_reset: bool = False):
    if force_reset:
        reset_all()
    else:
        ensure_file(get_paths_file(), DEFAULT_PATHS)
        ensure_file(get_config_file(), DEFAULT_CONFIG)
        ensure_file(get_logs_path())
    ensure_unsorted_folder()
    logger.info("[Initializer] System initialized.")
    notify_system_event("System Initialized","SortedPC is ready to use.")


# --- Entrypoint for programmatic calls ---
def run_initializer(force_reset: bool = False):
    initialize(force_reset=force_reset)


# --- CLI Entrypoint ---
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Initialize or reset the system state.")
    parser.add_argument("--reset", action="store_true", help="Force reset everything.")
    args = parser.parse_args()

    run_initializer(force_reset=args.reset)
