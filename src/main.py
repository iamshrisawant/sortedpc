# [main.py] — Patched for Full Functionality with On-Demand Elevation

import sys
import json
import ctypes
import logging
import subprocess
import time
import os
from pathlib import Path
import shutil
import colorama

colorama.init(autoreset=True, strip=True, convert=True)
from colorama import Fore, Style

# Assuming these imports are correct for your project structure
from src.core.pipelines.watcher import get_pid_file, is_pid_alive
from src.core.pipelines.initializer import run_initializer
from src.core.pipelines.builder import build_from_paths
from src.core.pipelines.actor import handle_correction
from src.core.pipelines.reinforcer import reinforce
from src.core.utils.paths import (
    get_watch_paths, get_organized_paths, get_paths_file,
    get_config_file, get_faiss_index_path, get_faiss_metadata_path,
    get_logs_path, get_xml, ROOT_DIR, normalize_path
)
from src.core.utils.notifier import notify_system_event

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

SYSTEM32_PATH = Path(os.environ.get("SystemRoot", "C:\\Windows")) / "System32"
SCHTASKS_EXE = SYSTEM32_PATH / "schtasks.exe"
TASKKILL_EXE = SYSTEM32_PATH / "taskkill.exe"

# ─── Admin Check & Elevation Helper ───────────────────────────────────────────

def is_admin() -> bool:
    """Checks if the script is currently running with administrative privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def run_as_admin(command_arg: str):
    """
    Re-launches the current script with a specific command-line argument,
    triggering a UAC prompt to gain administrative rights.
    """
    try:
        params = f'"{__file__}" {command_arg}'
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    except Exception as e:
        print(Fore.RED + f"Error: Elevation failed. {e}" + Style.RESET_ALL)

# ─── Admin-Only Tasks (Executed by the temporary elevated process) ────────────

def do_register_and_start():
    """Admin task: Registers the watcher for auto-startup and launches it."""
    print("Running admin task: Registering and starting watcher...")
    if not generate_watcher_xml():
        print("CRITICAL: Could not generate config.xml. Aborting.")
        time.sleep(3)
        return
    task_name = "SortedPC_Watcher"
    xml_file = get_xml()
    subprocess.run([str(SCHTASKS_EXE), '/Create', '/TN', task_name, '/XML', str(xml_file.resolve()), '/F'], check=True, capture_output=True)
    pythonw_exe = Path(sys.executable).parent / "python.exe"
    if not pythonw_exe.exists(): pythonw_exe = sys.executable
    subprocess.Popen([str(pythonw_exe), "-m", "src.core.pipelines.watcher"], cwd=str(ROOT_DIR), creationflags=subprocess.CREATE_NO_WINDOW)
    print("Admin task complete. This window will close shortly.")
    time.sleep(2)

def do_stop_only():
    """Admin task: Kills the watcher process but leaves the startup task registered."""
    print("Running admin task: Stopping watcher process...")
    pid_file = get_pid_file()
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text())
            subprocess.run([str(TASKKILL_EXE), '/PID', str(pid), '/F'], check=True, capture_output=True)
        except (ValueError, subprocess.CalledProcessError): pass
        finally: pid_file.unlink(missing_ok=True)
    print("Admin task complete. This window will close shortly.")
    time.sleep(2)

def do_stop_and_unregister():
    """Admin task: Kills the watcher process and removes it from auto-startup."""
    print("Running admin task: Stopping and unregistering watcher...")
    do_stop_only()
    if is_watcher_task_registered():
        subprocess.run([str(SCHTASKS_EXE), '/Delete', '/TN', 'SortedPC_Watcher', '/F'], check=True, capture_output=True)
    print("Unregistration complete. This window will close shortly.")
    time.sleep(2)

def do_reset():
    """Admin task: Stops all processes, unregisters tasks, and deletes all data."""
    print("Running admin task: Resetting system...")
    do_stop_and_unregister()
    paths_to_delete = [
        get_paths_file(), get_config_file(), get_faiss_index_path(),
        get_faiss_metadata_path(), get_xml()
    ]
    for p in paths_to_delete:
        if p.is_file(): p.unlink(missing_ok=True)
    log_dir = get_logs_path().parent
    if log_dir.is_dir(): shutil.rmtree(log_dir, ignore_errors=True)
    print("System reset complete. This window will close shortly.")
    time.sleep(3)

# ─── Standard User Functions ──────────────────────────────────────────────────

def safe_input(prompt: str = "") -> str:
    """A wrapper for input() to handle Ctrl+C gracefully."""
    try: return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print("\nExiting.")
        sys.exit(0)

def is_watcher_online() -> bool:
    """Checks if the watcher process is running by checking its PID file."""
    try:
        pid_file = get_pid_file()
        if not pid_file.exists():
            return False
        pid = int(pid_file.read_text())
        return is_pid_alive(pid)
    except (ValueError, FileNotFoundError):
        return False

def is_watcher_task_registered() -> bool:
    """Checks if the watcher task exists in the Windows Task Scheduler."""
    try:
        subprocess.check_output([str(SCHTASKS_EXE), '/Query', '/TN', 'SortedPC_Watcher'], stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError): return False

def wait_for_watcher_online(timeout: int = 15) -> bool:
    """Pauses execution until the watcher's PID file is found and the process is alive."""
    print("  -> Waiting for watcher to confirm it is online...", end="", flush=True)
    for _ in range(timeout):
        if is_watcher_online():
            print(Fore.GREEN + " Confirmed!" + Style.RESET_ALL)
            return True
        time.sleep(1)
        print(".", end="", flush=True)
    print(Fore.RED + " Timed out." + Style.RESET_ALL)
    return False

def generate_watcher_xml() -> bool:
    """Dynamically creates the config.xml for the Task Scheduler."""
    python_executable = sys.executable
    working_directory = str(ROOT_DIR)
    xml_template = f"""<?xml version="1.0" encoding="UTF-16"?><Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task"><RegistrationInfo><Date>2025-07-21T00:00:00</Date><Author>SortedPC</Author><URI>\\SortedPC_Watcher</URI></RegistrationInfo><Principals><Principal id="Author"><LogonType>InteractiveToken</LogonType><RunLevel>HighestAvailable</RunLevel></Principal></Principals><Settings><MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy><DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries><StopIfGoingOnBatteries>false</StopIfGoingOnBatteries><StartWhenAvailable>true</StartWhenAvailable><RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable><AllowHardTerminate>true</AllowHardTerminate><ExecutionTimeLimit>PT0S</ExecutionTimeLimit><Enabled>true</Enabled><Hidden>true</Hidden><RunOnlyIfIdle>false</RunOnlyIfIdle><WakeToRun>true</WakeToRun><Priority>7</Priority><RestartOnFailure><Interval>PT1M</Interval><Count>3</Count></RestartOnFailure></Settings><Triggers><BootTrigger><Enabled>true</Enabled></BootTrigger><LogonTrigger><Enabled>true</Enabled></LogonTrigger></Triggers><Actions Context="Author"><Exec><Command>{python_executable}</Command><Arguments>-m src.core.pipelines.watcher</Arguments><WorkingDirectory>{working_directory}</WorkingDirectory></Exec></Actions></Task>"""
    try:
        xml_path = get_xml()
        xml_path.parent.mkdir(exist_ok=True, parents=True)
        xml_path.write_text(xml_template, encoding="utf-16")
        return True
    except Exception as e:
        logger.error(f"Failed to generate config.xml: {e}")
        return False

# ─── Menu Action Functions (Ported from old main.py) ───────────────────────

def update_paths_json(watch_paths=None, organized_paths=None):
    """Updates the central paths.json file."""
    file = get_paths_file()
    data = {"watch_paths": get_watch_paths(), "organized_paths": get_organized_paths()}
    if watch_paths is not None: data["watch_paths"] = watch_paths
    if organized_paths is not None: data["organized_paths"] = organized_paths
    file.write_text(json.dumps(data, indent=2), encoding="utf-8")

def prompt_and_add_paths(key: str):
    """Generic function to prompt user for a list of paths."""
    is_watch = key == "watch_paths"
    existing = get_watch_paths() if is_watch else get_organized_paths()
    print(f"\nCurrently configured {key.replace('_', ' ')}:")
    for p in existing: print(f"  - {p}")
    print("\nEnter new paths below (or a blank line to finish).")
    
    updated = list(existing)
    while True:
        path = safe_input("Path: ").strip()
        if not path: break
        norm = normalize_path(path)
        if Path(norm).exists() and norm not in updated:
            updated.append(norm)
            print(f"  -> Added: {norm}")
        else:
            print(Fore.YELLOW + "  -> Path is invalid or already in the list." + Style.RESET_ALL)
    
    update_paths_json(
        watch_paths=updated if is_watch else None,
        organized_paths=updated if not is_watch else None
    )
    return updated

def add_organized_paths_action():
    """Handles adding organized paths and rebuilding the search index."""
    paths = prompt_and_add_paths("organized_paths")
    if not paths:
        print(Fore.RED + "No organized paths configured. The index cannot be built." + Style.RESET_ALL)
        return
    print("\nRebuilding search index from organized paths...")
    build_from_paths(paths)
    print(Fore.GREEN + "✅ Search index rebuilt successfully." + Style.RESET_ALL)

def add_watch_paths_action():
    """Handles adding watch paths and restarting the watcher if needed."""
    prompt_and_add_paths("watch_paths")
    print("\nWatch paths updated.")
    if is_watcher_online():
        print("  -> Restarting watcher to apply changes...")
        run_as_admin('--stop-only')
        time.sleep(2)
        run_as_admin('--register-and-start')
        wait_for_watcher_online()
        print(Fore.GREEN + "✅ Watcher restarted." + Style.RESET_ALL)

def show_move_logs():
    """Displays the latest move/correction log for each file."""
    log_file = get_logs_path()
    if not log_file.exists():
        print(Fore.YELLOW + "\nNo logs found." + Style.RESET_ALL)
        return []
    
    entries = {}
    with log_file.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                item = json.loads(line)
                if item.get("category") in {"moves", "corrections"}:
                    name = Path(item["file_path"]).name.lower()
                    if name not in entries or item["timestamp"] > entries[name]["timestamp"]:
                        entries[name] = item
            except (json.JSONDecodeError, KeyError):
                continue
    
    if not entries:
        print(Fore.YELLOW + "\nNo file move logs found." + Style.RESET_ALL)
        return []
        
    print("\n--- Recent File Moves ---")
    result = list(entries.values())
    for i, entry in enumerate(result):
        mark = Fore.YELLOW + " (corrected)" + Style.RESET_ALL if entry["category"] == "corrections" else ""
        print(f"  [{i}] {Path(entry['file_path']).name} → {entry['final_folder']}{mark}")
    return result

def apply_correction_action():
    """Handles the user workflow for correcting a sorted file's location."""
    entries = show_move_logs()
    if not entries: return
    
    try:
        idx_str = safe_input("\nEnter index of file to correct (or blank to cancel): ").strip()
        if not idx_str: return
        idx = int(idx_str)
        if not (0 <= idx < len(entries)):
            print(Fore.RED + "Invalid index." + Style.RESET_ALL)
            return
    except ValueError:
        print(Fore.RED + "Invalid input. Please enter a number." + Style.RESET_ALL)
        return
        
    new_folder_str = safe_input("Enter the correct folder path: ").strip()
    new_folder = Path(normalize_path(new_folder_str))
    if not new_folder.is_dir():
        print(Fore.RED + "The provided path is not a valid directory." + Style.RESET_ALL)
        return
        
    handle_correction(entries[idx]["file_path"], str(new_folder))
    print("  -> Correction applied. Running reinforcement learning...")
    reinforce()
    print(Fore.GREEN + "✅ Reinforcement complete." + Style.RESET_ALL)

# ─── Main Menu (Runs as Standard User) ────────────────────────────────────────

def main_menu():
    """The main user-facing menu, runs with standard privileges."""
    run_initializer()
    
    # --- Patched Block: Proactive Watcher Check at Startup ---
    print("\n--- System Check ---")
    if not is_watcher_task_registered():
        print(Fore.YELLOW + "Watcher is not registered to run on startup." + Style.RESET_ALL)
        choice = safe_input("Would you like to register and start it now? (y/n): ").lower()
        if choice == 'y':
            print("  -> Requesting admin rights...")
            run_as_admin('--register-and-start')
            if wait_for_watcher_online():
                print(Fore.GREEN + "  -> Watcher is now registered and online." + Style.RESET_ALL)
    elif not is_watcher_online():
        print(Fore.YELLOW + "Watcher is registered but currently offline." + Style.RESET_ALL)
    else:
        print(Fore.GREEN + "Watcher is registered and online." + Style.RESET_ALL)
    # --- End Patched Block ---

    if not get_organized_paths():
        print(Fore.YELLOW + "\nNo 'organized' paths are set up. Let's add some first." + Style.RESET_ALL)
        add_organized_paths_action()

    while True:
        print("\n" + "="*12 + " SortedPC Menu " + "="*12)
        online = is_watcher_online()
        registered = is_watcher_task_registered()
        
        # --- Contextual Menu Block ---
        print("\n--- Watcher Management ---")
        if online:
            print("  1. Stop Watcher (Admin Required)")
            print("  2. Stop and Unregister Watcher (Admin Required)")
        elif registered:
            print("  1. Start Watcher (Admin Required)")
            print("  2. Unregister Watcher (Admin Required)")
        else:
            print("  1. Register and Start Watcher (Admin Required)")
        
        print("\n--- System & Data ---")
        print("  3. Add/View Organized Paths & Rebuild Index")
        print("  4. Add/View Watch Paths")
        print("  5. View Logs & Apply Correction")
        print("  6. Run Full Reinforcement")
        print("  7. Reset Everything (Admin Required)")
        print("  8. Exit")
        print("-"*39)
        choice = safe_input("  Select: ").strip()

        # --- Menu Action Router ---
        if online:
            if choice == '1':
                print("  -> Requesting admin rights to stop the watcher...")
                run_as_admin('--stop-only')
                time.sleep(2)
            elif choice == '2':
                print("  -> Requesting admin rights to stop and unregister...")
                run_as_admin('--stop-and-unregister')
                time.sleep(2)
        elif registered:
            if choice == '1':
                print("  -> Requesting admin rights to start the watcher...")
                run_as_admin('--register-and-start')
                wait_for_watcher_online()
            elif choice == '2':
                print("  -> Requesting admin rights to unregister...")
                run_as_admin('--stop-and-unregister')
                time.sleep(2)
        else: # Not registered
            if choice == '1':
                print("  -> Requesting admin rights to register and start...")
                run_as_admin('--register-and-start')
                wait_for_watcher_online()

        # --- Other Menu Options ---
        if choice == "3": add_organized_paths_action()
        elif choice == "4": add_watch_paths_action()
        elif choice == "5": apply_correction_action()
        elif choice == "6":
            print("  -> Running full reinforcement learning on all logs...")
            reinforce()
            print(Fore.GREEN + "✅ Reinforcement complete." + Style.RESET_ALL)
        elif choice == "7":
            confirm = safe_input(Fore.RED + "  -> This is irreversible. Are you sure? (y/n): ").lower()
            if confirm == 'y':
                print("  -> Requesting admin rights to reset the system...")
                run_as_admin('--reset')
                time.sleep(4) # Wait for the admin process to finish cleaning up
                
                # --- Patched Block: Re-initialization after reset ---
                print("\n" + Fore.CYAN + "--- System Reset Complete. Now Re-initializing ---" + Style.RESET_ALL)
                run_initializer(force_reset=True) # Recreate all necessary files
                
                print("\nFirst, let's set up the paths for your organized files.")
                add_organized_paths_action()
                
                print("\nNext, let's set up the folders to watch for new files.")
                add_watch_paths_action()
                
                print("\n" + Fore.GREEN + "✅ Re-initialization complete." + Style.RESET_ALL)
                print("  -> The watcher needs to be started. Requesting admin rights...")
                run_as_admin('--register-and-start')
                wait_for_watcher_online()
                print(Fore.GREEN + "✅ System is now fully operational." + Style.RESET_ALL)
                # The loop will now continue, showing the updated menu
                
            else: print("  -> Reset cancelled.")
        elif choice == "8":
            print("Goodbye.")
            break
        # No 'else' needed for invalid choice, as the contextual block handles it.

# ─── Main Execution Router ────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if not is_admin():
            print("Error: Admin tasks must be run with administrative privileges.")
            time.sleep(3)
            sys.exit(1)
        if command == '--register-and-start': do_register_and_start()
        elif command == '--stop-only': do_stop_only()
        elif command == '--stop-and-unregister': do_stop_and_unregister()
        elif command == '--reset': do_reset()
        sys.exit(0)
    else:
        main_menu()
