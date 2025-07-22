# [watcher.py] — Patched for Robust Startup and Crash Logging

import time
import os
from pathlib import Path
import logging

# --- Minimal Initial Imports for Fast PID Writing ---
# These are unlikely to fail.
from src.core.utils.paths import get_config_file, get_watch_paths, get_watcher_log
from src.core.utils.notifier import notify_system_event

# ─── PID Tracking (Essential for startup signaling) ──────────────────────────

def is_pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False

def get_pid_file() -> Path:
    return get_config_file().with_name("watcher.pid")

def write_pid():
    """Writes the current process ID to the PID file."""
    try:
        pid_file = get_pid_file()
        pid_file.parent.mkdir(parents=True, exist_ok=True)
        pid_file.write_text(str(os.getpid()), encoding="utf-8")
    except Exception as e:
        # If this fails, log it to our dedicated file.
        logging.getLogger('watcher_debug').error(f"FATAL: Could not write PID file: {e}")
        raise RuntimeError("FATAL: Could not write PID file.")

def clear_pid():
    """Removes the PID file on clean shutdown."""
    get_pid_file().unlink(missing_ok=True)

# ─── Main Watcher Loop ────────────────────────────────────────────────────────

def watcher_loop(poll_interval: float = 3.0):
    # The logger is already configured by the __main__ block.
    logger = logging.getLogger('watcher_debug')

    # --- Step 1: Announce Online Status IMMEDIATELY ---
    try:
        write_pid()
        logger.info(f"PID {os.getpid()} written successfully. Proceeding with heavy imports.")
    except RuntimeError as e:
        logger.error(e)
        return # Abort if we can't even write the PID.

    # --- Step 2: Perform Heavy Imports Inside a Try/Except Block ---
    try:
        from src.core.pipelines.sorter import handle_new_file
        from src.core.utils.logger import has_been_handled
        heavy_imports_loaded = True
        logger.info("Core libraries (sorter, logger) loaded successfully.")
    except Exception as e:
        heavy_imports_loaded = False
        # This is the crucial log that will tell us what's wrong.
        logger.error("FATAL: Failed to load core libraries during startup.", exc_info=True)
        notify_system_event("Watcher Startup Failed", f"Error: {e}")

    if not heavy_imports_loaded:
        clear_pid() # Clean up before exiting a failed state.
        return

    notify_system_event("Watcher Online", "Monitoring for new files.")
    logger.info("Now monitoring for file changes...")

    watch_dirs = get_watch_paths()
    seen_files = set()
    boot_time = time.time()

    try:
        while True:
            # The rest of the watcher logic remains the same.
            for folder_str in watch_dirs:
                folder = Path(folder_str).resolve()
                if not folder.is_dir(): continue

                for file_path in folder.rglob("*"):
                    try:
                        resolved = file_path.resolve()
                        if (not file_path.is_file() or file_path.name.startswith(("~", ".")) or
                            resolved.stat().st_mtime < boot_time or str(resolved) in seen_files or
                            has_been_handled(str(resolved))):
                            continue

                        logger.info(f"Detected: {resolved.name}. Delegating to sorter.")
                        handle_new_file(str(resolved))
                        seen_files.add(str(resolved))
                    except Exception as e:
                        notify_system_event("Watcher Error", f"Failed to process {file_path.name}: {e}")
                        logger.error(f"ERROR delegating file {file_path.name}: {e}")
            time.sleep(poll_interval)
    except KeyboardInterrupt:
        logger.info("Interrupted by user.")
    finally:
        clear_pid()
        notify_system_event("Watcher Offline", "Watcher has stopped.")
        logger.info("Stopped and offline.")

# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # --- Patched Block for Robust Logging ---
    # Set up a dedicated log file for the watcher *immediately*.
    # This ensures that any crash, at any point, is recorded.
    log_file_path = get_watcher_log()
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create a specific logger for the watcher to avoid conflicts
    debug_logger = logging.getLogger('watcher_debug')
    debug_logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_file_path, mode='w', encoding='utf-8')
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    handler.setFormatter(formatter)
    debug_logger.addHandler(handler)

    try:
        watcher_loop()
    except Exception as e:
        # Catch any unexpected error that might have slipped past other checks.
        debug_logger.error("A fatal, untrapped error occurred in the watcher.", exc_info=True)
    finally:
        # The input() is removed as the log file is now the primary debug tool.
        debug_logger.info("Watcher process has ended.")
    # --- End Patched Block ---
