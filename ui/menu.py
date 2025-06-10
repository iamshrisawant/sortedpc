import os
import json
import threading

from config import CONFIG_FILE
from extractor import extract_from_new_paths, is_extraction_running, sweep_path
from db import (
    fetch_all_files, fetch_by_extension,
    fetch_by_name, fetch_by_size_range,
    fetch_hidden_files,
    fetch_folder_summary, update_folder_org_status
)
from learner import relearn  # renamed from infer_folder_organization


def load_paths():
    if not os.path.exists(CONFIG_FILE):
        return []
    try:
        with open(CONFIG_FILE, 'r') as f:
            data = json.load(f)
            return data.get("watch_paths", [])
    except (json.JSONDecodeError, IOError) as e:
        print(f"⚠️ Error reading config: {e}")
        return []

def save_paths(paths):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"watch_paths": paths}, f, indent=4)
    print("✅ Paths saved to config.\n")

def display_paths(paths):
    if not paths:
        print("📁 No watch paths configured.")
    else:
        print("📂 Current watch paths:")
        for idx, path in enumerate(paths, 1):
            print(f"  {idx}. {path}")
    print()

def add_paths(paths):
    if is_extraction_running():
        print("🔒 Extraction in progress. Please wait before adding new paths.")
        return paths

    print("➕ Add paths (type 'done' to finish):")
    while True:
        user_input = input("Add path: ").strip()
        if user_input.lower() == 'done':
            break
        if not os.path.isdir(user_input):
            print(f"❌ Invalid directory: {user_input}")
            continue
        if user_input in paths:
            print(f"⚠️ Already added.")
            continue
        paths.append(user_input)
        print(f"✅ Added: {user_input}")
    return paths

def remove_paths(paths):
    if is_extraction_running():
        print("🔒 Extraction in progress. Cannot remove paths now.")
        return paths

    if not paths:
        print("📭 No paths to remove.")
        return paths

    display_paths(paths)
    to_remove = input("Enter number(s) to remove (e.g., 1,3): ").strip()

    try:
        indexes = sorted(set(int(i.strip()) - 1 for i in to_remove.split(',')), reverse=True)
        for idx in indexes:
            if 0 <= idx < len(paths):
                removed = paths.pop(idx)
                print(f"❌ Removed: {removed}")
            else:
                print(f"⚠️ Invalid index: {idx+1}")
    except ValueError:
        print("⚠️ Invalid input. Use numbers separated by commas.")

    return paths

def run_resweep(path):
    if is_extraction_running():
        print("🔒 Extraction already in progress.")
        return
    def _resweep():
        sweep_path(path, show_preview=True)
    threading.Thread(target=_resweep, daemon=True).start()


def view_paths_menu(paths):
    while True:
        display_paths(paths)
        print("📋 Options:")
        print("  a. Add a path")
        print("  r. Resweep a path")
        print("  d. Delete a path")
        print("  b. Back to main menu")

        choice = input("Choose an option (a/r/d/b): ").strip().lower()

        if choice == 'a':
            paths = add_paths(paths)
            save_paths(paths)
            threading.Thread(target=extract_from_new_paths, daemon=True).start()
        elif choice == 'r':
            index = input("Enter path number to resweep: ").strip()
            if index.isdigit() and 1 <= int(index) <= len(paths):
                path = paths[int(index)-1]
                run_resweep(path)
            else:
                print("❌ Invalid index.")
        elif choice == 'd':
            paths = remove_paths(paths)
            save_paths(paths)
        elif choice == 'b':
            break
        else:
            print("❌ Invalid option.")

def display_query_results(results):
    if not results:
        print("⚠️ No matching records.")
        return

    print(f"\n📄 Showing {min(10, len(results))} of {len(results)} result(s):")
    for row in results[:10]:
        print(f"  ID {row[0]}: {row[1]} | {row[3]} | {row[4]} bytes | Hidden: {'Yes' if row[9] else 'No'}")
    if len(results) > 10:
        print("  ...and more not shown.\n")

def query_database_menu():
    while True:
        print("\n🔍 Query Options:")
        print("1. Show all files")
        print("2. Search by extension")
        print("3. Search by name")
        print("4. Filter by size range")
        print("5. Show hidden files only")
        print("6. Back to main menu")

        choice = input("Choose an option (1–6): ").strip()

        if choice == "1":
            results = fetch_all_files()
            display_query_results(results)
        elif choice == "2":
            ext = input("Enter file extension (e.g. .mp4): ").strip().lower()
            results = fetch_by_extension(ext)
            display_query_results(results)
        elif choice == "3":
            name = input("Enter part of filename: ").strip()
            results = fetch_by_name(name)
            display_query_results(results)
        elif choice == "4":
            try:
                min_size = int(input("Min size (bytes): ").strip())
                max_size = int(input("Max size (bytes): ").strip())
                results = fetch_by_size_range(min_size, max_size)
                display_query_results(results)
            except ValueError:
                print("❌ Invalid size input.")
        elif choice == "5":
            results = fetch_hidden_files()
            display_query_results(results)
        elif choice == "6":
            break
        else:
            print("❌ Invalid option. Enter 1–6.")

def review_folder_organization():
    print("\n📁 Folder Summary (Learner vs User Feedback):\n")
    folders = fetch_folder_summary()

    if not folders:
        print("⚠️ No folders found.")
        return

    for i, (folder, count, org_count, feedback) in enumerate(folders, 1):
        learner_guess = 'organized' if org_count >= (count / 2) else 'unorganized'
        print(f"{i}. {folder}")
        print(f"   ↳ Files: {count}")
        print(f"   ↳ Learner guess: {learner_guess}")
        print(f"   ↳ User feedback: {feedback}")

    idx = input("\nEnter folder number to update status (or press Enter to cancel): ").strip()
    if not idx.isdigit() or not (1 <= int(idx) <= len(folders)):
        print("⏭️ Cancelled.")
        return

    folder = folders[int(idx) - 1][0]
    new_status = input("Enter new status (organized/unorganized): ").strip().lower()
    if new_status not in ['organized', 'unorganized']:
        print("❌ Invalid status entered.")
        return

    update_folder_org_status(folder, new_status)
    print(f"✅ Feedback updated for folder '{folder}'. Learner will use this info on relearn.")

def menu_with_learner_options():
    while True:
        print("\n🧠 Learner Menu:")
        print("1. Review & update folder organization feedback")
        print("2. Trigger relearn based on feedback")
        print("3. Back to main menu")

        choice = input("Choose option (1-3): ").strip()
        if choice == '1':
            review_folder_organization()
        elif choice == '2':
            print("🔄 Relearning...")
            relearn()
            print("✅ Relearn complete.")
        elif choice == '3':
            break
        else:
            print("❌ Invalid option.")

def manage_paths():
    paths = load_paths()

    if not paths:
        print("🔍 No existing paths found. Let's add some.")
        paths = add_paths(paths)
        save_paths(paths)
        threading.Thread(target=extract_from_new_paths, daemon=True).start()
        return paths

    while True:
        print("\n🧭 Path Manager Menu:")
        print("1. View paths")
        print("2. Database")
        print("3. Learner")
        print("4. Exit")

        choice = input("Choose an option (1–4): ").strip()

        if choice == '1':
            view_paths_menu(paths)
        elif choice == '2':
            print("📂 Entering database query mode...")
            query_database_menu()
        elif choice == '3':
            menu_with_learner_options()
        elif choice == '4':
            save_paths(paths)
            print("👋 Exiting Path Manager.\n")
            break
        else:
            print("❌ Invalid choice. Enter 1–4.")

    return paths
