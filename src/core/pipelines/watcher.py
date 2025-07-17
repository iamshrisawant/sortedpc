import time
import json
import logging
from pathlib import Path
from typing import Dict

from src.core.utils.paths import get_config_file, get_watch_paths
from src.core.utils.extractor import extract
from src.core.utils.chunker import chunk_text
from src.core.utils.embedder import embed_texts
from src.core.utils.logger import has_been_handled
from src.core.utils.notifier import notify_system_event
from src.core.pipelines.sorter import handle_new_file
from src.core.pipelines.actor import act_on_file

# Set up logging to file (before any log statements)
logging.basicConfig(
    filename=r"C:\Users\Shriswarup Sawant\Documents\Shriswarup\Extras\Projects\sortedpc\watcher_launch.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)


# ─── Config ────────────────────────────────────────────────────

def load_config() -> Dict:
    path = get_config_file()
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

def update_watcher_state(online: bool):
    config = load_config()
    config["watcher_online"] = online
    get_config_file().write_text(json.dumps(config, indent=2), encoding="utf-8")


# ─── Watcher Logic ──────────────────────────────────────────

def is_valid_file(path: Path) -> bool:
    return (
        path.is_file() and
        not path.name.startswith(("~", ".")) and
        path.suffix.lower() not in {".tmp", ".ds_store"}
    )

def watcher_loop(poll_interval: float = 3.0):
    logger.info("[Watcher] Initializing watcher loop...")
    update_watcher_state(True)
    notify_system_event("Watcher Online", "SortedPC is now monitoring new files.")

    watch_dirs = get_watch_paths()
    seen_files = set()
    boot_time = time.time()

    try:
        while load_config().get("watcher_online", True):
            for folder_str in watch_dirs:
                folder = Path(folder_str).resolve()
                if not folder.exists() or not folder.is_dir():
                    logger.warning(f"[Watcher] Skipping invalid path: {folder}")
                    continue

                for file_path in folder.rglob("*"):
                    try:
                        resolved = file_path.resolve()
                        if (
                            not is_valid_file(resolved) or
                            resolved.stat().st_mtime < boot_time or
                            str(resolved) in seen_files or
                            has_been_handled(str(resolved))
                        ):
                            continue

                        logger.info(f"[Watcher] Detected new file: {resolved.name}")
                        extracted = extract(resolved)
                        chunks = chunk_text(extracted["content"])
                        embeddings = embed_texts(chunks)

                        file_data = {
                            "file_path": str(resolved),
                            "file_name": extracted["file_name"],
                            "parent_folder": extracted["parent_folder"],
                            "parent_folder_path": extracted["parent_folder_path"],
                            "file_type": extracted["file_type"],
                            "content_hash": extracted["content_hash"],
                            "embeddings": embeddings,
                        }

                        sorted_data = handle_new_file(file_data)
                        act_on_file(sorted_data)

                        seen_files.add(str(resolved))
                        logger.info(f"[Watcher] Processed and sorted: {resolved.name}")

                    except Exception as e:
                        logger.warning(f"[Watcher] Failed to process {file_path.name}: {e}")

            time.sleep(poll_interval)

    except KeyboardInterrupt:
        logger.info("[Watcher] Interrupted by user.")

    finally:
        update_watcher_state(False)
        logger.info("[Watcher] Watcher stopped.")


# ─── API ──────────────────────────────────────────

def start_watcher():
    watcher_loop()

def kill_watcher():
    update_watcher_state(False)
    logger.info("[Watcher] Kill signal sent: watcher_online = False")

def get_watcher_state() -> bool:
    return load_config().get("watcher_online", False)


# ─── Entry Point ─────────────────────────────────────────

if __name__ == "__main__":
    logger.info("[Watcher] Standalone launch detected. Initializing...")
    start_watcher()
