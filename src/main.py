# [main.py] — SortedPC Launcher (Fixed & Portable)
# ✅ Dynamically generates config.xml for portability.
# ✅ Provides clear instructions if not run as an administrator.
# ✅ Implements a complete system reset.

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
# These files do not need to be changed.
from src.core.pipelines.watcher import get_pid_file, is_pid_alive
from src.core.pipelines.initializer import run_initializer
from src.core.pipelines.builder import build_from_paths
from src.core.pipelines.actor import handle_correction
from src.core.pipelines.reinforcer import reinforce
from src.core.utils.paths import (
    get_watch_paths, get_organized_paths, get_paths_file,
    get_config_file, get_faiss_index_path, get_faiss_metadata_path,
    get_logs_path, get_xml, ROOT_DIR
)
from src.core.utils.notifier import notify_system_event

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

SYSTEM32_PATH = Path(os.environ.get("SystemRoot", "C:\\Windows")) / "System32"
SCHTASKS_EXE = SYSTEM32_PATH / "schtasks.exe"
TASKKILL_EXE = SYSTEM32_PATH / "taskkill.exe"

# ─── Admin Check ───
def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

# ─── Dynamic XML Generation ───────────────────────────────────
def generate_watcher_xml():
    """
    Dynamically creates the config.xml file with paths for the current machine.
    This makes the application portable.
    """
    python_executable = sys.executable
    working_directory = str(ROOT_DIR)
    
    # Using an f-string for templating. The curly braces for XML are escaped by doubling them.
    xml_template = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>2025-07-21T00:00:00</Date>
    <Author>SortedPC</Author>
    <URI>\\SortedPC_Watcher</URI>
  </RegistrationInfo>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <AllowHardTerminate>true</AllowHardTerminate>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Enabled>true</Enabled>
    <Hidden>true</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>true</WakeToRun>
    <Priority>7</Priority>
    <RestartOnFailure>
      <Interval>PT1M</Interval>
      <Count>3</Count>
    </RestartOnFailure>
  </Settings>
  <Triggers>
    <BootTrigger>
      <Enabled>true</Enabled>
    </BootTrigger>
    <LogonTrigger>
      <Enabled>true</Enabled>
    </LogonTrigger>
  </Triggers>
  <Actions Context="Author">
    <Exec>
      <Command>{python_executable}</Command>
      <Arguments>-m src.core.pipelines.watcher</Arguments>
      <WorkingDirectory>{working_directory}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"""
    try:
        xml_path = get_xml()
        xml_path.parent.mkdir(exist_ok=True, parents=True)
        xml_path.write_text(xml_template, encoding="utf-16")
        logger.info(f"Successfully generated config.xml at {xml_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to generate config.xml: {e}")
        return False

# ─── Utility: Safe Input ───
def safe_input(prompt: str = "") -> str:
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print(f"\nExiting due to user interrupt.")
        if is_watcher_online():
            kill_watcher_process()
        sys.exit(0)

# ─── Watcher Management ───
def is_watcher_online() -> bool:
    try:
        pid_file = get_pid_file()
        if not pid_file.exists():
            return False
        pid = int(pid_file.read_text())
        return is_pid_alive(pid)
    except (ValueError, FileNotFoundError):
        return False

def is_watcher_task_registered() -> bool:
    try:
        command = [str(SCHTASKS_EXE), '/Query', '/TN', 'SortedPC_Watcher']
        subprocess.check_output(command, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def wait_for_watcher_online(timeout: int = 15) -> bool:
    print("  -> Waiting for watcher to come online...", end="", flush=True)
    for _ in range(timeout):
        if is_watcher_online():
            print(Fore.GREEN + " Online!" + Style.RESET_ALL)
            return True
        time.sleep(1)
        print(".", end="", flush=True)
    print(Fore.RED + " Timeout!" + Style.RESET_ALL)
    logger.warning("[Main] Timed out waiting for watcher to start.")
    return False

def start_watcher_process():
    if is_watcher_online():
        return True
    
    print("  -> Launching watcher process...")
    try:
        # Use pythonw.exe to run in the background without a console window
        pythonw_exe = Path(sys.executable).parent / "pythonw.exe"
        if not pythonw_exe.exists():
            # Fallback to python.exe if pythonw.exe is not found
            pythonw_exe = sys.executable

        subprocess.Popen(
            [str(pythonw_exe), "-m", "src.core.pipelines.watcher"],
            cwd=str(ROOT_DIR),
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return wait_for_watcher_online()
    except Exception as e:
        logger.error(f"[Main] Failed to launch watcher process: {e}")
        return False

def kill_watcher_process():
    if not is_watcher_online():
        print("  -> Watcher is already offline.")
        return

    pid_file = get_pid_file()
    try:
        pid = int(pid_file.read_text())
        print(f"  -> Killing watcher process with PID: {pid}...")
        command = [str(TASKKILL_EXE), '/PID', str(pid), '/F']
        subprocess.run(command, check=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        print("  -> Process killed.")
    except (ValueError, FileNotFoundError, subprocess.CalledProcessError) as e:
        logger.warning(f"Failed to kill watcher process (it may have already closed): {e}")
    finally:
        if pid_file.exists():
            pid_file.unlink()

def register_watcher_task():
    task_name = "SortedPC_Watcher"
    
    # Dynamically generate the XML file first
    if not generate_watcher_xml():
        print(Fore.RED + "  -> CRITICAL: Could not generate config.xml. Task registration aborted." + Style.RESET_ALL)
        return

    xml_file = get_xml()
    command = [str(SCHTASKS_EXE), '/Create', '/TN', task_name, '/XML', str(xml_file.resolve()), '/F']
    try:
        print("  -> Registering startup task...")
        subprocess.run(command, check=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        print(Fore.GREEN + "  -> Task registered successfully." + Style.RESET_ALL)
        start_watcher_process()
    except subprocess.CalledProcessError as e:
        error_output = e.stderr.decode('utf-8', errors='ignore')
        print(Fore.RED + f"  -> Task registration failed. Error: {error_output}" + Style.RESET_ALL)
    except FileNotFoundError:
        print(Fore.RED + "  -> Task registration failed. schtasks.exe not found." + Style.RESET_ALL)


def unregister_watcher_task():
    if not is_watcher_task_registered():
        print("  -> Watcher is not registered for startup.")
        return
        
    command = [str(SCHTASKS_EXE), '/Delete', '/TN', 'SortedPC_Watcher', '/F']
    try:
        print("  -> Unregistering startup task...")
        subprocess.run(command, check=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        print("  -> Task unregistered.")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        logger.warning(f"Could not unregister task: {e}")

# ─── Menu Actions ───
def add_organized_paths():
    # This is a placeholder function
    print("Functionality for adding organized paths is not fully implemented.")

def add_watch_paths():
    # This is a placeholder function
    print("Functionality for adding watch paths is not fully implemented.")

def reset_everything():
    print(Fore.RED + "\nWARNING: This will delete all configuration, logs, and the search index.")
    confirm = safe_input("Are you sure you want to reset everything? This cannot be undone. (y/n): ").strip().lower()
    if confirm == 'y':
        print("  -> Stopping and unregistering watcher...")
        kill_watcher_process()
        unregister_watcher_task()
        
        # **FIXED**: Added FAISS index and metadata paths to the deletion list.
        paths_to_delete = [
            get_paths_file(),
            get_config_file(),
            get_config_file().with_name("watcher.pid"),
            get_faiss_index_path(),
            get_faiss_metadata_path(),
            get_xml() # Also delete the generated XML
        ]
        
        for p in paths_to_delete:
            try:
                if p.is_file():
                    p.unlink()
                    print(f"  -> Deleted file: {p}")
            except Exception as e:
                print(f"  -> Could not delete {p}: {e}")

        # Delete the logs directory
        try:
            log_dir = get_logs_path().parent # Get the directory containing the log file
            if log_dir.exists() and log_dir.is_dir():
                shutil.rmtree(log_dir)
                print(f"  -> Deleted directory: {log_dir}")
        except Exception as e:
            print(f"  -> Could not delete logs directory: {e}")

        print(Fore.GREEN + "\n✅ System has been reset. Please restart the application." + Style.RESET_ALL)
        sys.exit(0)
    else:
        print("Reset cancelled.")


def print_watcher_status():
    online = is_watcher_online()
    registered = is_watcher_task_registered()
    print()
    if online:
        print(Fore.GREEN + "🟢 Watcher is online and running." + Style.RESET_ALL)
    elif registered:
        print(Fore.YELLOW + "🟡 Watcher is registered for startup but is currently offline." + Style.RESET_ALL)
    else:
        print(Fore.RED + "🔴 Watcher is not registered for startup." + Style.RESET_ALL)

def menu():
    run_initializer()

    print("\n--- System Initialized (Running as Administrator) ---")
    if not is_watcher_task_registered():
        print(Fore.YELLOW + "\nWarning: The file watcher is not registered to run on startup." + Style.RESET_ALL)
        choice = safe_input("Would you like to register it now? (y/n): ").strip().lower()
        if choice == 'y':
            register_watcher_task()
        else:
            print("You can register it later from the main menu.")
    else:
        if not is_watcher_online():
            print("  -> Watcher is registered, attempting to bring it online...")
            start_watcher_process()

    while True:
        print("\n====== SortedPC Menu ======")
        print_watcher_status()
        print("1. Add organized path(s) (Not Implemented)")
        print("2. Add watch path(s) (Not Implemented)")
        print("3. Kill watcher")
        print("4. View / apply correction (Not Implemented)")
        print("5. Run full reinforcement (Not Implemented)")
        print("6. Reset everything")
        print("7. Exit")
        choice = safe_input("Select: ").strip()

        if choice == "1":
            add_organized_paths()
        elif choice == "2":
            add_watch_paths()
        elif choice == "3":
            kill_watcher_process()
        elif choice == "4":
            handle_correction()
        elif choice == "5":
            reinforce()
        elif choice == "6":
            reset_everything()
        elif choice == "7":
            print("Shutting down...")
            kill_watcher_process()
            print("Goodbye.")
            break
        else:
            print(Fore.YELLOW + "Invalid choice." + Style.RESET_ALL)

if __name__ == "__main__":
    # **FIXED**: Replaced the confusing self-elevation with a clear check and instructions.
    if not is_admin():
        print(Fore.RED + "Error: Administrative privileges are required to manage startup tasks.")
        print(Fore.YELLOW + "Please re-run this script from a terminal that has been opened 'As Administrator'.")
        safe_input("Press Enter to exit...")
        sys.exit(1)
    
    # If we get here, we are running as an administrator.
    menu()
