# [main.py] — Final Production Version
# Implements a robust batch-file-based launcher for the watcher.

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

# --- Application Imports ---
from src.core.pipelines.initializer import run_initializer
from src.core.pipelines.builder import build_from_paths
from src.core.pipelines.actor import handle_correction
from src.core.pipelines.reinforcer import reinforce
from src.core.utils.paths import (
    get_watch_paths, get_organized_paths, get_paths_file,
    get_config_file, get_logs_path, get_xml, ROOT_DIR, normalize_path
)
from src.core.pipelines.watcher import get_pid_file, is_pid_alive

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# --- System Constants ---
SYSTEM32_PATH = Path(os.environ.get("SystemRoot", "C:\\Windows")) / "System32"
SCHTASKS_EXE = SYSTEM32_PATH / "schtasks.exe"
TASKKILL_EXE = SYSTEM32_PATH / "taskkill.exe"
TASK_NAME = "SortedPC_Watcher"
# --- NEW: Path for our generated launcher script ---
WATCHER_LAUNCHER_BAT = ROOT_DIR / "src" / "launch_watcher.bat"

# ─── Launcher Generation (The Core Fix) ─────────────────────────────────────

def generate_watcher_launcher_bat(venv_python_exe: str) -> bool:
    """
    Creates a batch file with hardcoded paths to ensure the watcher
    runs in the correct environment. This is the most reliable method.
    """
    try:
        pythonw_exe = Path(venv_python_exe).parent / "python.exe"
        if not pythonw_exe.exists():
            pythonw_exe = venv_python_exe

        # The content of our launcher script.
        # 1. Set PYTHONPATH to the project root, solving the 'src' module not found error.
        # 2. Use the absolute path to the venv's pythonw.exe to run the watcher.
        bat_content = f"""@echo off
set PYTHONPATH={ROOT_DIR}
start "SortedPC Watcher" /B "{pythonw_exe}" -m src.core.pipelines.watcher
"""
        WATCHER_LAUNCHER_BAT.write_text(bat_content)
        logger.info("Successfully generated watcher launcher script.")
        return True
    except Exception as e:
        logger.error(f"FATAL: Could not generate watcher launcher script: {e}")
        return False

def generate_watcher_xml() -> bool:
    """Dynamically creates the config.xml to point to our new batch launcher."""
    # The command is now the batch file itself.
    command = str(WATCHER_LAUNCHER_BAT.resolve())
    working_directory = str(ROOT_DIR)
    
    xml_template = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo><Author>SortedPC</Author><URI>\\{TASK_NAME}</URI></RegistrationInfo>
  <Principals><Principal id="Author"><LogonType>InteractiveToken</LogonType><RunLevel>HighestAvailable</RunLevel></Principal></Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy><DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries><StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <StartWhenAvailable>true</StartWhenAvailable><AllowHardTerminate>true</AllowHardTerminate><ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Enabled>true</Enabled><Hidden>true</Hidden>
  </Settings>
  <Triggers><LogonTrigger><Enabled>true</Enabled></LogonTrigger></Triggers>
  <Actions Context="Author">
    <Exec>
      <Command>"{command}"</Command>
      <WorkingDirectory>"{working_directory}"</WorkingDirectory>
    </Exec>
  </Actions>
</Task>"""
    try:
        get_xml().write_text(xml_template, encoding="utf-16")
        return True
    except Exception as e:
        logger.error(f"Failed to generate config.xml: {e}")
        return False

# ─── Elevation and Admin Tasks ──────────────────────────────────────────────

def run_as_admin(command_to_run: str):
    """Elevates a command using ShellExecuteW for UAC prompt."""
    try:
        # We now directly execute the command (e.g., the batch file) as admin.
        ctypes.windll.shell32.ShellExecuteW(None, "runas", command_to_run, None, None, 1)
        logger.info(f"Requesting admin rights to run: {command_to_run}")
        return True
    except Exception as e:
        print(Fore.RED + f"Error: Elevation failed. {e}" + Style.RESET_ALL)
        return False

def do_register():
    """Admin task: Creates the scheduled task."""
    print("--- Admin: Registering Watcher Task ---")
    if not generate_watcher_xml():
        return
    xml_file = get_xml()
    try:
        subprocess.run([str(SCHTASKS_EXE), '/Create', '/TN', TASK_NAME, '/XML', str(xml_file.resolve()), '/F'], check=True, capture_output=True, text=True)
        print(Fore.GREEN + "✅ Task registered successfully.")
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"ERROR: Task registration failed!\n{e.stderr}")

def do_unregister():
    """Admin task: Deletes the scheduled task."""
    print("--- Admin: Unregistering Watcher Task ---")
    try:
        subprocess.run([str(SCHTASKS_EXE), '/Delete', '/TN', TASK_NAME, '/F'], check=True, capture_output=True, text=True)
        print(Fore.GREEN + "✅ Task unregistered successfully.")
    except subprocess.CalledProcessError:
        print(Fore.YELLOW + "NOTE: Task was not registered.")

def do_stop_watcher():
    """Admin task: Kills the watcher process."""
    print("--- Admin: Stopping Watcher Process ---")
    pid_file = get_pid_file()
    if not pid_file.exists():
        print(Fore.YELLOW + "Watcher is not running.")
        return
    try:
        pid = int(pid_file.read_text())
        subprocess.run([str(TASKKILL_EXE), '/PID', str(pid), '/F', '/T'], check=True, capture_output=True, text=True)
        print(Fore.GREEN + "✅ Watcher process stopped.")
    except (ValueError, subprocess.CalledProcessError):
        print(Fore.YELLOW + "Watcher process may have already been stopped.")
    finally:
        pid_file.unlink(missing_ok=True)

# ─── Standard User Functions & Menu ─────────────────────────────────────────
# ... (These functions remain largely the same, but the admin calls are simplified)

def safe_input(prompt: str = "") -> str:
    try: return input(prompt)
    except (EOFError, KeyboardInterrupt): sys.exit(0)

def is_watcher_online() -> bool:
    pid_file = get_pid_file()
    if not pid_file.exists(): return False
    try:
        pid = int(pid_file.read_text())
        return is_pid_alive(pid)
    except (ValueError, FileNotFoundError): return False

def is_watcher_task_registered() -> bool:
    try:
        subprocess.check_output([str(SCHTASKS_EXE), '/Query', '/TN', TASK_NAME], stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError): return False

def wait_for_watcher_online(timeout: int = 10) -> bool:
    print("  -> Waiting for watcher to confirm it is online...", end="", flush=True)
    for _ in range(timeout * 2):
        if is_watcher_online():
            print(Fore.GREEN + " Confirmed!" + Style.RESET_ALL)
            return True
        time.sleep(0.5)
    print(Fore.RED + " Timed out. Check 'src/watcher_launch.log' for errors." + Style.RESET_ALL)
    return False

# ... (Menu Action functions like add_paths, etc. are omitted for brevity but should be kept)

def main_menu():
    run_initializer()
    
    while True:
        print("\n" + "="*12 + " SortedPC Menu " + "="*12)
        online = is_watcher_online()
        registered = is_watcher_task_registered()
        
        print("\n--- Watcher Management ---")
        if online:
            print(f"  1. {Fore.RED}Stop Watcher{Style.RESET_ALL} (Admin Required)")
        else:
            print(f"  1. {Fore.GREEN}Start Watcher{Style.RESET_ALL} (Admin Required)")

        if registered:
            print(f"  2. {Fore.RED}Unregister from Startup{Style.RESET_ALL} (Admin Required)")
        else:
            print(f"  2. {Fore.GREEN}Register for Startup{Style.RESET_ALL} (Admin Required)")
        
        print("\n  8. Exit")
        print("-"*39)
        choice = safe_input("  Select: ").strip()

        if choice == '1':
            if online:
                # We create a temporary script to stop the watcher
                stop_bat = ROOT_DIR / "src" / "stop_watcher.bat"
                stop_bat.write_text(f'@echo off\ntaskkill /PID {get_pid_file().read_text()} /F /T\ndel "{stop_bat}"')
                run_as_admin(str(stop_bat))
            else:
                # Generate and run the launcher script
                if generate_watcher_launcher_bat(sys.executable):
                    run_as_admin(str(WATCHER_LAUNCHER_BAT))
                    wait_for_watcher_online()
        
        elif choice == '2':
            if registered:
                if online:
                    print(Fore.YELLOW + "Please stop the watcher first.")
                else:
                    # We need to elevate the schtasks command itself
                    run_as_admin(f'"{SCHTASKS_EXE}" /Delete /TN "{TASK_NAME}" /F')
            else:
                if generate_watcher_launcher_bat(sys.executable):
                    do_register() # This can now run directly as it just generates XML
                    run_as_admin(f'"{SCHTASKS_EXE}" /Create /TN "{TASK_NAME}" /XML "{get_xml().resolve()}" /F')
            time.sleep(2)
        
        elif choice == '8':
            if is_watcher_online():
                print("Stopping watcher...")
                do_stop_watcher()
            print("Goodbye.")
            break

if __name__ == "__main__":
    # The main script no longer needs the complex admin router
    main_menu()
