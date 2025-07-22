# watcher.py

import time
import os
from pathlib import Path

# --- MODIFIED IMPORTS ---
# Imports for extract, chunker, and embedder are removed.
# Import for actor is also removed as it's no longer called from here.
from src.core.utils.paths import get_config_file, get_watch_paths
from src.core.utils.logger import has_been_handled
from src.core.utils.notifier import notify_system_event
from src.core.pipelines.sorter import handle_new_file # Sorter is now the main entry point
# --- END MODIFIED IMPORTS ---

# ─── PID Tracking ──────────────────────────────────────────────

def is_pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False
    except Exception:
        return False

def get_pid_file() -> Path:
    return get_config_file().with_name("watcher.pid")

def write_pid():
    try:
        pid_file = get_pid_file()
        pid_file.parent.mkdir(parents=True, exist_ok=True)
        pid_file.write_text(str(os.getpid()), encoding="utf-8")
        print(f"[Watcher] PID {os.getpid()} written to: {pid_file}")
    except Exception as e:
        notify_system_event("Watcher Error", f"Fatal: Failed to write PID file: {e}")
        print(f"[Watcher] FATAL ERROR: Could not write PID file: {e}")
        raise RuntimeError("PID write failed")

def clear_pid():
    pid_file = get_pid_file()
    if pid_file.exists():
        try:
            pid_file.unlink()
            print(f"[Watcher] PID file deleted: {pid_file}")
        except Exception as e:
            print(f"[Watcher] WARNING: Failed to delete PID file on exit: {e}")

# ─── File Validation ───────────────────────────────────────────

def is_valid_file(path: Path) -> bool:
    return (
        path.is_file() and
        not path.name.startswith(("~", ".")) and
        path.suffix.lower() not in {".tmp", ".ds_store", ".crdownload"}
    )

# ─── Main Watcher Loop (Patched) ───────────────────────────────

def watcher_loop(poll_interval: float = 3.0):
    pid_file = get_pid_file()
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text())
            if is_pid_alive(pid):
                print(f"[Watcher] ABORTED: Another instance (PID: {pid}) is already running.")
                return
        except (ValueError, FileNotFoundError):
            print("[Watcher] Found stale PID file. Proceeding to start a new instance.")
            pass

    try:
        write_pid()
    except RuntimeError:
        return

    notify_system_event("Watcher Online", "SortedPC is now monitoring new files.")
    print("[Watcher] Online and monitoring...")

    watch_dirs = get_watch_paths()
    seen_files = set()
    boot_time = time.time()

    try:
        while True:
            for folder_str in watch_dirs:
                folder = Path(folder_str).resolve()
                if not folder.is_dir():
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

                        # --- MODIFIED CORE LOGIC ---
                        # The watcher's responsibility now ends here. It finds a valid,
                        # new file and passes its path directly to the sorter pipeline.
                        # All processing, sorting, and acting happens downstream.
                        print(f"[Watcher] Detected new file, delegating to sorter: {resolved.name}")
                        handle_new_file(str(resolved))
                        
                        # Add to seen_files to prevent re-processing in the same session
                        seen_files.add(str(resolved))
                        # --- END OF MODIFIED CORE LOGIC ---

                    except Exception as e:
                        notify_system_event("Watcher Error", f"Failed to delegate {file_path.name}: {e}")
                        print(f"[Watcher] ERROR: Failed to delegate file {file_path.name}: {e}")

            time.sleep(poll_interval)

    except KeyboardInterrupt:
        notify_system_event("Watcher Stopped", "Watcher interrupted by user.")
        print("\n[Watcher] Interrupted by user. Shutting down.")

    finally:
        clear_pid()
        notify_system_event("Watcher Offline", "Watcher has stopped.")
        print("[Watcher] Stopped and offline.")

# ─── Public API & Entry Point (Unchanged) ─────────────────────────

def start_watcher():
    watcher_loop()

def kill_watcher():
    clear_pid()
    notify_system_event("Watcher Stopped", "Watcher was killed by SortedPC.")

if __name__ == "__main__":
    notify_system_event("Watcher Launch", "Watcher launched directly.")
    print("[Watcher] Launching watcher from __main__.")
    start_watcher()