import os
import sys
import json
import time
import logging
from pathlib import Path

from src.core.pipelines.initializer import run_initializer
from src.core.pipelines.builder import build_from_paths
from src.core.pipelines.watcher import watcher_loop
from src.core.pipelines.sorter import handle_new_file
from src.core.pipelines.actor import act_on_file, handle_correction
from src.core.pipelines.reinforcer import reinforce

from src.core.utils.paths import (
    get_watch_paths,
    get_organized_paths,
    get_paths_file,
    get_config_file,
    normalize_path,
    get_logs_path
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


# --- Helpers ---
def prompt_paths(key: str) -> list:
    print(f"\nNo {key.replace('_', ' ')} found.")
    paths = []
    while True:
        user_input = input(f"Add a path to {key} (or press Enter to stop): ").strip()
        if not user_input:
            break
        normalized = normalize_path(user_input)
        if Path(normalized).exists():
            paths.append(normalized)
        else:
            print("Invalid path. Try again.")
    return paths


def update_paths_json(new_watch: list, new_organized: list):
    path_file = get_paths_file()
    if not path_file.exists():
        path_file.parent.mkdir(parents=True, exist_ok=True)
        with open(path_file, "w", encoding="utf-8") as f:
            json.dump({"watch_paths": new_watch, "organized_paths": new_organized}, f, indent=2)
    else:
        with open(path_file, "r+", encoding="utf-8") as f:
            data = json.load(f)
            data["watch_paths"] = new_watch or data.get("watch_paths", [])
            data["organized_paths"] = new_organized or data.get("organized_paths", [])
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=2)


def update_state(key: str, value: bool):
    config_path = get_config_file()
    config = {}
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    config[key] = value
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


# --- Correction flow ---
def show_move_logs():
    logs_path = get_logs_path()
    if not logs_path.exists():
        print("\nNo logs found.")
        return []

    entries = []
    with open(logs_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
                if entry["category"] == "moves":  # ✅ FIXED: was "move"
                    entries.append(entry)
            except Exception:
                continue

    if not entries:
        print("\nNo move logs yet.")
        return []

    print("\nMove Logs:")
    for i, entry in enumerate(entries):
        print(f"[{i}] {Path(entry['file_path']).name} → {entry['final_folder']}")
    return entries


def handle_user_correction():
    entries = show_move_logs()
    if not entries:
        return

    idx = input("\nEnter the index of a file to correct (or press Enter to cancel): ").strip()
    if not idx.isdigit() or int(idx) >= len(entries):
        print("Invalid selection.")
        return

    selected = entries[int(idx)]
    new_folder = input("Enter new folder path: ").strip()
    if not new_folder or not Path(new_folder).exists():
        print("Invalid folder.")
        return

    handle_correction(selected["file_path"], new_folder)
    reinforce()


# --- Watcher runner with sorter + actor ---
def run_live_watcher():
    from src.core.utils.extractor import extract
    from src.core.utils.chunker import chunk_text
    from src.core.utils.embedder import embed_texts

    config = {}
    config_path = get_config_file()
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

    if not config.get("faiss_built", False) or config.get("builder_running", False):
        print("\nFAISS not built or builder still running.")
        return

    print("\n[Watcher] Running... Press Ctrl+C to stop.")
    seen = set()

    logs_path = get_logs_path()
    logs_path.parent.mkdir(parents=True, exist_ok=True)
    logs_path.touch(exist_ok=True)

    update_state("watcher_online", True)
    try:
        while True:
            logs = []
            if logs_path.exists():
                with open(logs_path, "r", encoding="utf-8") as f:
                    logs = [json.loads(line) for line in f if line.strip()]

            for folder in get_watch_paths():
                for file in Path(folder).rglob("*"):
                    if not file.is_file() or file.name.startswith("~") or file.name.startswith("."):
                        continue
                    resolved = str(file.resolve())
                    if resolved in seen:
                        continue
                    if any(l.get("file_path") == resolved for l in logs):
                        continue

                    print(f"\n[New] {file.name}")
                    try:
                        data = extract(resolved)
                        chunks = chunk_text(data["content"])
                        embeddings = embed_texts(chunks)
                        file_data = {
                            "file_path": resolved,
                            "file_name": data["file_name"],
                            "parent_folder": data["parent_folder"],
                            "file_type": data["file_type"],
                            "content_hash": data["content_hash"],
                            "embeddings": embeddings
                        }
                        sorted_data = handle_new_file(file_data)
                        act_on_file(sorted_data)
                        seen.add(resolved)
                    except Exception as e:
                        print(f"Error processing {file.name}: {e}")
            time.sleep(3)

    except KeyboardInterrupt:
        print("\n[Watcher] Stopped.")
        resp = input("Run reinforcement now? (y/n): ").strip().lower()
        if resp == "y":
            reinforce()

    finally:
        update_state("watcher_online", False)


# --- Main ---
def main():
    print("\n🔧 SortedPC CLI Orchestrator 🔧")

    run_initializer()

    watch_paths = get_watch_paths()
    organized_paths = get_organized_paths()

    if not watch_paths:
        watch_paths = prompt_paths("watch_paths")
    if not organized_paths:
        organized_paths = prompt_paths("organized_paths")

    update_paths_json(watch_paths, organized_paths)

    print("\n[Builder] Indexing organized paths...")
    update_state("builder_running", True)
    build_from_paths(organized_paths)
    update_state("builder_running", False)
    update_state("faiss_built", True)

    run_live_watcher()


# --- Menu CLI ---
def menu():
    while True:
        print("\n====== SortedPC Menu ======")
        print("1. Launch pipeline (builder + watcher)")
        print("2. View and apply correction")
        print("3. Run full reinforcement learning")
        print("4. Exit")
        choice = input("Select an option: ").strip()

        if choice == "1":
            main()
        elif choice == "2":
            handle_user_correction()
        elif choice == "3":
            reinforce()
        elif choice == "4":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    menu()
