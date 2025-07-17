# [main.py] — SortedPC Launcher

import sys
import json
import ctypes
import logging
import subprocess
import time
from pathlib import Path

from colorama import Fore, Style, init as colorama_init
colorama_init(autoreset=True)

from src.core.pipelines.initializer import run_initializer
from src.core.pipelines.builder import build_from_paths
from src.core.pipelines.actor import handle_correction
from src.core.pipelines.reinforcer import reinforce
from src.core.utils.paths import (
    get_watch_paths, get_organized_paths, get_paths_file,
    get_config_file, normalize_path, get_logs_path,
)
from src.core.utils.notifier import notify_system_event

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


# ─── Config State ───

def load_config() -> dict:
    path = get_config_file()
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

def update_state(key: str, value: bool):
    config = load_config()
    config[key] = value
    get_config_file().write_text(json.dumps(config, indent=2), encoding="utf-8")

def get_state(key: str) -> bool:
    return load_config().get(key, False)


# ─── Admin + Short Path Utilities ───

def run_as_admin(command: str) -> bool:
    try:
        result = ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd.exe", f"/c {command}", None, 1)
        return result > 32
    except Exception as e:
        logger.error(f"[Main] Elevation failed: {e}")
        return False

def get_short_path(path: Path) -> str:
    try:
        result = subprocess.check_output(f'for %I in ("{path}") do @echo %~sI', shell=True, text=True)
        return result.strip()
    except Exception as e:
        logger.error(f"[Main] Could not convert to short path: {e}")
        return str(path)


# ─── Watcher Management ───

def register_watcher_task():
    task_name = "SortedPC_Watcher"
    xml_file = Path(__file__).parent / "config.xml"

    if not xml_file.exists():
        logger.error(f"[Main] XML config file not found at {xml_file}")
        notify_system_event("Watcher Not Registered", "Missing config.xml. Cannot register watcher.")
        return False

    short_xml_path = get_short_path(xml_file.resolve())
    command = f'schtasks /Create /TN "{task_name}" /XML "{short_xml_path}" /F'

    success = run_as_admin(command)
    if success:
        time.sleep(2.5)
        if is_watcher_task_registered():
            update_state("watcher_registered", True)
            notify_system_event("Watcher Registered", "Watcher registered using config.xml")
            logger.info("[Main] Watcher registered successfully.")
            return True
        else:
            logger.error("[Main] Watcher registration failed after elevation.")
    else:
        logger.error("[Main] Watcher registration denied or failed.")

    notify_system_event("Watcher Not Registered", "Watcher registration failed or denied.")
    return False

def unregister_watcher_task():
    command = 'schtasks /Delete /TN "SortedPC_Watcher" /F'
    if run_as_admin(command):
        update_state("watcher_registered", False)
        notify_system_event("Watcher Unregistered", "Unregistered with elevation.")
        logger.info("[Main] Watcher unregistered with elevation.")
    else:
        logger.error("[Main] Watcher unregistration denied.")
        notify_system_event("Watcher Not Unregistered", "Admin access denied.")

def is_watcher_online() -> bool:
    try:
        return get_state("watcher_online")
    except Exception as e:
        logger.error(f"[Main] Failed to read watcher_online from config: {e}")
        return False

def is_watcher_task_registered() -> bool:
    try:
        subprocess.check_output('schtasks /Query /TN "SortedPC_Watcher"', shell=True, text=True)
        return True
    except subprocess.CalledProcessError:
        return False

def maybe_start_watcher():
    should_start = get_state("faiss_built") and get_watch_paths() and not get_state("builder_busy")
    registered = is_watcher_task_registered()
    running = is_watcher_online()

    logger.info(f"[Main] Watcher registered: {registered}")
    logger.info(f"[Main] Watcher running: {running}")
    logger.info(f"[Main] Preconditions met: {should_start}")

    if not should_start:
        logger.info("[Main] Watcher will not be started — prerequisites not met.")
        return

    if not registered:
        logger.warning("[Main] Watcher not registered. Attempting registration…")
        registered = register_watcher_task()

    if registered and not running:
        try:
            subprocess.Popen([sys.executable, "-m", "src.core.pipelines.watcher"], shell=True)
            logger.info("[Main] Watcher started via subprocess.")
            while not is_watcher_online():
                time.sleep(0.25)
            logger.info("[Main] Watcher is now online.")
        except Exception as e:
            logger.error(f"[Main] Failed to start watcher: {e}")
    elif not registered:
        logger.warning("[Main] Watcher not started because registration failed.")


def stop_watcher():
    from src.core.pipelines.watcher import kill_watcher
    kill_watcher()
    unregister_watcher_task()


# ─── Path Management ───

def update_paths_json(watch_paths=None, organized_paths=None):
    file = get_paths_file()
    data = {"watch_paths": [], "organized_paths": []}
    if file.exists():
        data = json.loads(file.read_text(encoding="utf-8"))
    if watch_paths is not None:
        data["watch_paths"] = watch_paths
    if organized_paths is not None:
        data["organized_paths"] = organized_paths
    file.write_text(json.dumps(data, indent=2), encoding="utf-8")

def prompt_and_add_paths(key: str):
    is_watch = key == "watch_paths"
    existing = get_watch_paths() if is_watch else get_organized_paths()
    print(f"\nAdd {key.replace('_', ' ')}. Enter blank line to stop.")
    updated = list(existing)

    while True:
        path = input("Path: ").strip()
        if not path:
            break
        norm = normalize_path(path)
        if Path(norm).exists() and norm not in updated:
            updated.append(norm)
        else:
            print("  → Invalid or duplicate path.")

    update_paths_json(
        watch_paths=updated if is_watch else None,
        organized_paths=updated if not is_watch else None
    )
    return updated


# ─── Main Actions ───

def add_organized_paths():
    paths = prompt_and_add_paths("organized_paths")
    print("Rebuilding FAISS index…")
    update_state("builder_busy", True)
    build_from_paths(paths)
    update_state("builder_busy", False)
    update_state("faiss_built", True)
    print("✅ FAISS index rebuilt.")
    maybe_start_watcher()

def add_watch_paths():
    paths = prompt_and_add_paths("watch_paths")
    if paths:
        print("Restarting watcher…")
        stop_watcher()
        maybe_start_watcher()
        print("✅ Watcher restarted.")
    else:
        print("No paths added. Skipping watcher restart.")

def show_move_logs():
    log_file = get_logs_path()
    if not log_file.exists():
        print("No logs found.")
        return []
    entries = {}
    for line in log_file.read_text(encoding="utf-8").splitlines():
        try:
            item = json.loads(line)
            if item.get("category") in {"moves", "corrections"}:
                name = Path(item["file_path"]).name.lower()
                if name not in entries or item["timestamp"] > entries[name]["timestamp"]:
                    entries[name] = item
        except Exception:
            continue
    if not entries:
        print("No move logs found.")
        return []
    print("\nMove Logs:")
    result = list(entries.values())
    for i, entry in enumerate(result):
        mark = " (corrected)" if entry["category"] == "corrections" else ""
        print(f"[{i}] {Path(entry['file_path']).name} → {entry['final_folder']}{mark}")
    return result

def apply_user_correction():
    entries = show_move_logs()
    if not entries:
        return
    idx = input("Select index to correct (blank to cancel): ").strip()
    if not idx.isdigit() or not (0 <= int(idx) < len(entries)):
        print("Invalid selection.")
        return
    new_folder = input("Enter new folder path: ").strip()
    if not Path(new_folder).exists():
        print("Invalid folder.")
        return
    handle_correction(entries[int(idx)]["file_path"], new_folder)
    reinforce()
    print("✅ Correction applied and reinforced.")


# ─── UI ───

def print_watcher_status():
    online = is_watcher_online()
    registered = get_state("watcher_registered")
    print()
    if online:
        print(Fore.GREEN + "🟢 Watcher is online and running." + Style.RESET_ALL)
    elif registered:
        print(Fore.YELLOW + "🟡 Watcher is registered but offline." + Style.RESET_ALL)
    else:
        print(Fore.RED + "🔴 Watcher is not registered." + Style.RESET_ALL)

    if not get_organized_paths():
        print(Fore.RED + "→ No organized paths set.")
    if not get_watch_paths():
        print(Fore.RED + "→ No watch paths set.")
    if not get_state("faiss_built"):
        print(Fore.RED + "→ FAISS index not built.")


# ─── Menu ───

def menu():
    run_initializer()
    if not get_organized_paths():
        add_organized_paths()
    maybe_start_watcher()

    while True:
        print("\n====== SortedPC Menu ======")
        print_watcher_status()
        print("1. Add organized path(s) + rebuild index")
        print("2. Add watch path(s) + restart watcher")
        print("3. Kill watcher")
        print("4. View / apply correction")
        print("5. Run full reinforcement")
        print("6. Reset everything")
        print("7. Exit")
        choice = input("Select: ").strip()

        if choice == "1":
            add_organized_paths()
        elif choice == "2":
            add_watch_paths()
        elif choice == "3":
            stop_watcher()
            print("✅ Watcher killed and unregistered.")
        elif choice == "4":
            apply_user_correction()
        elif choice == "5":
            reinforce()
            print("✅ Reinforcement complete.")
        elif choice == "6":
            print("Resetting system…")
            stop_watcher()
            run_initializer(force_reset=True)
            if not get_organized_paths():
                add_organized_paths()
            maybe_start_watcher()
        elif choice == "7":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")


# ─── Entrypoint ───

if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        print("\nExiting…")
        stop_watcher()
        notify_system_event("SortedPC Exited.")
