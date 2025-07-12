# src/main.py

import sys
import json
from pathlib import Path
from PySide6.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from gui.scripts.main_window import MainWindow
from gui.scripts.themes import apply_theme
from core.scheduler import run_kb_scheduler
from core.file_watcher import reset_and_run_watcher

# -- Global App State --
STATE_FILE = Path("src/core/data/state.json")  # Renamed from kb_state.json
PATHS_FILE = Path("src/core/paths.json")

CONFIG = {}
PATHS = {}

DEFAULT_CONFIG = {
    "theme": "system",
    "watch_paths": [],
    "kb_paths": [],
    "launch_position": "Center"
}

DEFAULT_PATHS = {
    "splash_image": "src/gui/assets/splash.png",
    "ui_file_card": "src/gui/components/FileCard.ui",
    "ui_chat_user": "src/gui/components/ChatBubbleUser.ui",
    "ui_chat_app": "src/gui/components/ChatBubbleApp.ui"
}

def load_config():
    global CONFIG
    try:
        with open(STATE_FILE) as f:
            data = json.load(f)
            CONFIG = {**DEFAULT_CONFIG, **data}
    except Exception:
        CONFIG = DEFAULT_CONFIG.copy()

def load_paths():
    global PATHS
    try:
        with open(PATHS_FILE) as f:
            data = json.load(f)
            PATHS = {**DEFAULT_PATHS, **data}
    except Exception:
        PATHS = DEFAULT_PATHS.copy()

def get_config(key, default=None):
    return CONFIG.get(key, default)

def get_path(key):
    return PATHS.get(key)

def show_error_dialog(message: str):
    QMessageBox.critical(None, "Startup Error", message)
    sys.exit(1)

def main():
    app = QApplication(sys.argv)

    # Load config and paths
    load_config()
    load_paths()

    # Show splash screen
    splash_path = get_path("splash_image")
    if splash_path and Path(splash_path).exists():
        splash_pix = QPixmap(splash_path)
    else:
        splash_pix = QPixmap(400, 200)
        splash_pix.fill(Qt.black)

    splash = QSplashScreen(splash_pix)
    splash.showMessage("Loading, please wait...", Qt.AlignBottom | Qt.AlignCenter, Qt.white)
    splash.show()
    app.processEvents()

    # Apply theme
    apply_theme(app, get_config("theme"))

    # Run weekly KB rebuild scheduler
    try:
        run_kb_scheduler()
    except Exception as e:
        show_error_dialog(f"Failed to start KB scheduler:\n{e}")

    # Run file watcher if index is ready
    try:
        index_file = Path("src/core/data/index.faiss")
        if index_file.exists():
            watch_paths = get_config("watch_paths", [])
            if watch_paths:
                reset_and_run_watcher(watch_paths)
    except Exception as e:
        show_error_dialog(f"Failed to start file watcher:\n{e}")

    # Launch main window
    window = MainWindow(CONFIG, PATHS)
    splash.finish(window)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
