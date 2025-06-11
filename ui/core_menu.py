# ui/core_menu.py

import threading
import uuid
from datetime import datetime
from core.db import (
    add_scan_path, remove_scan_path, get_scan_paths,
    save_file_record, record_scan
)
from core.file_io import scan_directory
import core.config

import logging
logger = logging.getLogger(__name__)


LOCK = threading.Lock()

def launch_core_menu():
    while True:
        print("\n[📁 File Scanning & Paths]")
        print("1. Add Scan Path")
        print("2. Remove Scan Path")
        print("3. List Scan Paths")
        print("4. Start Scan")
        print("5. Back")

        choice = input("> ").strip()

        if choice == "1":
            add_path()
        elif choice == "2":
            remove_path()
        elif choice == "3":
            list_paths()
        elif choice == "4":
            trigger_scan()
        elif choice == "5":
            break
        else:
            print("Invalid input.")

def add_path():
    path = input("Enter full path to scan: ").strip()
    if path:
        add_scan_path(path)
        print(f"✅ Added: {path}")

def remove_path():
    path = input("Enter path to remove: ").strip()
    if path:
        remove_scan_path(path)
        print(f"❎ Removed: {path}")

def list_paths():
    paths = get_scan_paths()
    print("🔍 Watched Paths:")
    if not paths:
        print("  (None)")
    for i, p in enumerate(paths, 1):
        print(f"  {i}. {p}")

def trigger_scan():
    
    if LOCK.locked():
        print("⚠️ Scan already in progress.")
        logger.warning("Scan already running.")
        return

    threading.Thread(target=run_scan_thread).start()

def run_scan_thread():
    with LOCK:
        scan_id = str(uuid.uuid4())
        started = datetime.now().isoformat()
        print(f"🔄 Starting scan {scan_id[:8]}")

        try:
            for path in get_scan_paths():
                logger.info(f"Starting scan on user path: {path}")
                for file_meta in scan_directory(path, core.config.DEFAULT_CONFIG):
                    file_meta['scan_id'] = scan_id
                    save_file_record(file_meta)
            record_scan(scan_id, started, datetime.now().isoformat())
            print("✅ Scan complete.")
            logger.info("Scan completed.")

        except Exception as e:
            print(f"❌ Scan failed: {e}")
