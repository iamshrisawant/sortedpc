from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent
from pathlib import Path
import time
import json
from threading import Thread
from loguru import logger

from sorter_pipeline import sort_file
from kb_builder import INDEX_FILE, META_FILE

LOG_PATH = Path("logs/watcher.log")
SORT_LOG_PATH = Path("logs/moves.log")
IGNORE_SUFFIXES = {".tmp", ".crdownload", ".part"}
WATCHED_FOLDERS = set()

logger.add(LOG_PATH, rotation="1 MB", enqueue=True)

# -------------------------------
# Util: Load already sorted files
# -------------------------------

def get_sorted_file_paths() -> set[str]:
    sorted_paths = set()
    if not SORT_LOG_PATH.exists():
        return sorted_paths

    with SORT_LOG_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                if "file_moved" in line:
                    json_part = line.split("|")[-1].strip()
                    entry = json.loads(json_part)
                    full_path = Path(entry["final_folder"]) / entry["file"]
                    sorted_paths.add(str(full_path))
            except Exception as e:
                logger.warning(f"Failed to parse move log line: {line.strip()} | {e}")
    return sorted_paths

class SortingEventHandler(FileSystemEventHandler):
    def __init__(self, sorted_paths: set[str]):
        self.sorted_paths = sorted_paths

    def on_created(self, event: FileCreatedEvent):
        if not event.is_directory:
            file_path = Path(event.src_path)

            if file_path.suffix.lower() in IGNORE_SUFFIXES:
                logger.info(f"Ignored temporary file: {file_path}")
                return

            if str(file_path) in self.sorted_paths:
                logger.info(f"Already sorted file (from log): {file_path}")
                return

            logger.info(f"New file detected: {file_path}")
            result = sort_file(file_path)

            if "moved_to" in result:
                self.sorted_paths.add(result["moved_to"])
                logger.info(f"Sorted and moved: {result['file']} -> {result['moved_to']}")
            else:
                logger.warning(f"Sorting failed for {result['file']}: {result.get('error')}")

def start_watcher(folders: list[str]):
    if not (Path(INDEX_FILE).exists() and Path(META_FILE).exists()):
        logger.error("Knowledge base not ready. Cannot start file watcher.")
        return

    WATCHED_FOLDERS.update(Path(p).resolve() for p in folders)
    sorted_paths = get_sorted_file_paths()
    observer = Observer()

    for folder in WATCHED_FOLDERS:
        if folder.exists():
            handler = SortingEventHandler(sorted_paths)
            observer.schedule(handler, str(folder), recursive=False)
            logger.info(f"Watching folder: {folder}")
        else:
            logger.warning(f"Invalid folder skipped: {folder}")

    observer.start()
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def run_in_background(folders: list[str]):
    thread = Thread(target=start_watcher, args=(folders,), daemon=True)
    thread.start()
