import time
import json
import logging
from pathlib import Path
from typing import List, Dict

from src.core.utils.paths import (
    get_config_file,
    get_watch_paths,
    get_logs_path
)
from src.core.utils.extractor import extract
from src.core.utils.chunker import chunk_text
from src.core.utils.embedder import embed_texts

# from src.core.pipelines.sorter import handle_new_file  # Uncomment when ready

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")


# --- Internal Utilities ---

def load_config() -> Dict:
    config_path = get_config_file()
    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def load_move_logs() -> List[Dict]:
    logs = []
    logs_path = get_logs_path()
    if logs_path.exists():
        with logs_path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        logs.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    return logs

def file_already_sorted(file_path: Path, move_logs: List[Dict]) -> bool:
    resolved = str(file_path.resolve())
    return any(entry.get("file_path") == resolved for entry in move_logs)

def is_valid_file(file_path: Path) -> bool:
    return (
        file_path.is_file()
        and not file_path.name.startswith("~")
        and not file_path.name.startswith(".")
    )


# --- Core Watcher Loop ---

def watcher_loop(poll_interval: float = 3.0) -> None:
    config = load_config()

    if not config.get("faiss_built", False):
        logger.warning("[Watcher] FAISS index not built. Run builder first.")
        return

    if config.get("builder_busy", False):
        logger.warning("[Watcher] Builder is currently running. Watcher paused.")
        return

    watch_dirs = get_watch_paths()
    if not watch_dirs:
        logger.warning("[Watcher] No watch paths specified.")
        return

    seen_files = set()
    logger.info(f"[Watcher] Monitoring {len(watch_dirs)} folder(s)...")

    while True:
        try:
            move_logs = load_move_logs()

            for dir_path in watch_dirs:
                folder = Path(dir_path).resolve()
                if not folder.exists() or not folder.is_dir():
                    logger.warning(f"[Watcher] Invalid directory: {folder}")
                    continue

                for file_path in folder.rglob("*"):
                    if not is_valid_file(file_path):
                        continue

                    resolved = str(file_path.resolve())
                    if resolved in seen_files or file_already_sorted(file_path, move_logs):
                        continue

                    logger.info(f"[Watcher] New file detected: {file_path.name}")

                    try:
                        data = extract(str(file_path))
                        chunks = chunk_text(data["cleaned_content"])
                        embeddings = embed_texts(chunks)

                        file_data = {
                            "file_path": resolved,
                            "file_name": data["file_name"],
                            "parent_folder": data["parent_folder"],
                            "file_type": data["file_type"],
                            "content_hash": data["content_hash"],
                            "embeddings": embeddings
                        }

                        # handle_new_file(file_data)  # Uncomment once sorter is integrated
                        logger.info(f"[Watcher] File passed to sorter: {file_path.name}")
                        seen_files.add(resolved)

                    except Exception as e:
                        logger.warning(f"[Watcher] Failed to process {file_path.name}: {e}")

            time.sleep(poll_interval)

        except KeyboardInterrupt:
            logger.info("[Watcher] Gracefully stopped by user.")
            break


# --- Entrypoints ---

def start_watcher():
    watcher_loop()


if __name__ == "__main__":
    start_watcher()
