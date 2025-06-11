# ui/menu.py

from ui import core_menu  # Layer 1: file_io, db
# Future imports:
# from ui import classify_menu, organize_menu, learn_menu

def launch_menu():
    while True:
        print("\n=== Human-Like File Organizer ===")
        print("1. File Scanning & Paths")
        print("2. Classification Review (Coming Soon)")
        print("3. Organize Suggestions (Coming Soon)")
        print("4. Feedback & Learning (Coming Soon)")
        print("5. Exit")

        choice = input("> ").strip()

        if choice == "1":
            core_menu.launch_core_menu()
        elif choice == "5":
            print("Goodbye.")
            break
        else:
            print("Feature coming soon or invalid input.")
