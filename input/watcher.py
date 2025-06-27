import os
import time
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from data.extractor import extract_metadata
from data.tokenizer import tokenize_file
from models.predictor import predict_and_sort

WATCHED_PATHS_FILE = "watched_paths.json"

class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        file_path = event.src_path
        print(f"[INFO] New file detected: {file_path}")

        try:
            metadata = extract_metadata(file_path)
            tokens = tokenize_file(file_path)
            if not tokens:
                print(f"[WARN] Skipping sparse or unreadable file: {file_path}")
                return

            print(f"[INFO] Metadata + tokens extracted, invoking predictor...")
            predict_and_sort(file_path, metadata, tokens)

        except Exception as e:
            print(f"[ERROR] Failed processing {file_path}: {e}")

def load_watch_paths():
    if not os.path.exists(WATCHED_PATHS_FILE):
        raise FileNotFoundError(f"{WATCHED_PATHS_FILE} not found.")
    with open(WATCHED_PATHS_FILE, "r") as f:
        paths = json.load(f)
    return [p for p in paths if os.path.isdir(p)]

def start_watching():
    paths = load_watch_paths()
    observer = Observer()
    handler = NewFileHandler()

    for path in paths:
        observer.schedule(handler, path, recursive=True)
        print(f"[INFO] Watching folder: {path}")

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n[INFO] Watcher stopped by user.")
    observer.join()

if __name__ == "__main__":
    start_watching()
