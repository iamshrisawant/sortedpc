# src/core/file_watcher.py

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent
from pathlib import Path
from threading import Thread
import time
import json
import argparse

from sorter_pipeline import sort_file
from kb_builder import INDEX_FILE, META_FILE
from utils.config import get_organized_roots
from loguru import logger

LOG_PATH = Path("src/core/logs/watcher.log")
SORT_LOG_PATH = Path("src/core/logs/moves.log")
IGNORE_SUFFIXES = {".tmp", ".crdownload", ".part"}

logger.add(LOG_PATH, rotation="1 MB", enqueue=True)

_watcher_thread = None
_observer = None


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
                    original = str(Path(entry["file"]).resolve())
                    final = str(Path(entry["final_folder"], entry["file"]).resolve())
                    sorted_paths.update({original, final})
            except Exception as e:
                logger.warning(f"[Watcher] Parse error in move log: {e}")
    return sorted_paths


class SortingEventHandler(FileSystemEventHandler):
    def __init__(self, sorted_paths: set[str]):
        self.sorted_paths = sorted_paths

    def handle_file(self, file_path: Path):
        path_str = str(file_path)

        if file_path.suffix.lower() in IGNORE_SUFFIXES:
            logger.debug(f"[Watcher] Ignored temp file: {file_path}")
            return

        if path_str in self.sorted_paths:
            logger.debug(f"[Watcher] Already sorted: {file_path}")
            return

        logger.info(f"[Watcher] New file detected: {file_path.name}")

        for _ in range(10):
            try:
                mtime1 = file_path.stat().st_mtime
                time.sleep(1)
                mtime2 = file_path.stat().st_mtime
                if mtime1 == mtime2:
                    break
            except FileNotFoundError:
                return
        else:
            logger.warning(f"[Watcher] File unstable or still writing: {file_path}")
            return

        result = sort_file(file_path)
        if "moved_to" in result:
            dest_path = Path(result["moved_to"]).resolve()
            self.sorted_paths.add(path_str)
            self.sorted_paths.add(str(dest_path))
            logger.info(f"[Watcher] Moved: {file_path.name} → {dest_path}")
        else:
            logger.warning(f"[Watcher] Sorting failed: {result.get('error')}")

    def on_created(self, event: FileCreatedEvent):
        if not event.is_directory:
            self.handle_file(Path(event.src_path).resolve())

    def on_modified(self, event: FileModifiedEvent):
        if not event.is_directory:
            self.handle_file(Path(event.src_path).resolve())


def reset_and_run_watcher(watch_paths: list[Path] = None):
    global _watcher_thread, _observer

    if not (INDEX_FILE.exists() and META_FILE.exists()):
        logger.error("[Watcher] FAISS index missing. Cannot start watcher.")
        return

    if _observer:
        _observer.stop()
        _observer.join()

    if watch_paths is None:
        watch_paths = get_organized_roots()

    watch_paths = [Path(p).expanduser().resolve(strict=False) for p in watch_paths]

    def watch():
        global _observer
        sorted_paths = get_sorted_file_paths()
        _observer = Observer()

        for folder in watch_paths:
            if not folder.exists() or not folder.is_dir():
                logger.warning(f"[Watcher] Skipping invalid path: {folder}")
                continue

            handler = SortingEventHandler(sorted_paths)
            _observer.schedule(handler, str(folder), recursive=False)
            logger.info(f"[Watcher] Watching: {folder}")

        _observer.start()
        while True:
            time.sleep(5)

    _watcher_thread = Thread(target=watch, daemon=True)
    _watcher_thread.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start file watcher for automatic sorting.")
    parser.add_argument(
        "--folders",
        nargs="+",
        help="(Optional) Folders to watch. If omitted, uses kb_paths from config."
    )
    args = parser.parse_args()

    resolved_paths = [Path(f).expanduser().resolve(strict=False) for f in args.folders] if args.folders else get_organized_roots()
    logger.info("[Watcher] Launching with: " + ", ".join(map(str, resolved_paths)))

    reset_and_run_watcher(resolved_paths)

    print("\n[Watcher] Running. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n[Watcher] Stopped.")
        if _observer:
            _observer.stop()
            _observer.join()
