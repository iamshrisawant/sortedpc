from PySide6.QtWidgets import (
    QDialog, QListWidgetItem, QFileDialog, QMessageBox, QLabel, QComboBox, QSystemTrayIcon, QStyle
)
from PySide6.QtGui import QIcon
from .ui_logWindow import Ui_logWindow
from gui.scripts.utils import load_component
from pathlib import Path
import json
from core.sorter_pipeline import move_file
from core.kb_builder import build_kb

LOG_FILE = Path("src/core/data/meta.json")  # Example source of file actions
ORGANIZED_ROOT = Path("organized_folders")

class LogWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_logWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Application Log")

        self._tray = QSystemTrayIcon(self)
        self._tray.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        self._tray.show()

        self._original_log = []
        self._current_log = []

        self._load_log()
        self._populate_log()

        # Connect dialog buttons
        self.ui.bbButtons.accepted.connect(self._save_changes)
        self.ui.bbButtons.rejected.connect(self.close)
        self.ui.bbButtons.button(self.ui.bbButtons.StandardButton.Reset).clicked.connect(self._restore_original)

    def _load_log(self):
        if LOG_FILE.exists():
            with open(LOG_FILE, 'r') as f:
                meta = json.load(f)

            self._original_log = [
                {"filename": fname, "path": info.get("folder", "")}
                for fname, info in meta.items()
            ]
            self._current_log = self._original_log.copy()

    def _populate_log(self):
        self.ui.lwLog.clear()
        for entry in self._current_log:
            self._add_log_row(entry["filename"], entry["path"])

    def _add_log_row(self, filename, predicted_path):
        row = load_component("src/gui/components/LogRow.ui")

        lbl = row.findChild(QLabel, "lblFilename")
        combo = row.findChild(QComboBox, "cbPathSuggestions")

        lbl.setText(filename)
        combo.clear()
        combo.addItems([
            predicted_path,
            "/home/user/Documents",
            "/home/user/Desktop",
            "Other..."
        ])
        combo.setEditable(True)

        combo.currentIndexChanged.connect(lambda: self._on_combo_changed(combo))

        item = QListWidgetItem()
        item.setSizeHint(row.sizeHint())
        self.ui.lwLog.addItem(item)
        self.ui.lwLog.setItemWidget(item, row)

    def _on_combo_changed(self, combo: QComboBox):
        if combo.currentText() == "Other...":
            folder = QFileDialog.getExistingDirectory(self, "Select Folder")
            if folder:
                index = combo.currentIndex()
                combo.setItemText(index, folder)
                combo.setCurrentIndex(index)

    def _show_toast(self, title: str, message: str):
        self._tray.showMessage(title, message, QSystemTrayIcon.Information, 3000)

    def _save_changes(self):
        updated_log = {}

        for i in range(self.ui.lwLog.count()):
            widget = self.ui.lwLog.itemWidget(self.ui.lwLog.item(i))
            if not widget:
                continue

            filename = widget.findChild(QLabel, "lblFilename").text()
            new_path = widget.findChild(QComboBox, "cbPathSuggestions").currentText()
            updated_log[filename] = {"folder": new_path}

            # Attempt to move and re-index
            try:
                file_path = Path(ORGANIZED_ROOT) / filename
                dest_path = Path(new_path)
                moved_path = move_file(file_path, dest_path)
                build_kb(dest_path, rebuild=False)
                self._show_toast("File Moved", f"{filename} → {new_path}")
            except Exception as e:
                print(f"[LogWindow] Error handling {filename}: {e}")

        # Save to meta.json (or wherever needed)
        with open(LOG_FILE, "w") as f:
            json.dump(updated_log, f, indent=2)

        QMessageBox.information(self, "Saved", "Log changes saved.")
        self.accept()

    def _restore_original(self):
        self._current_log = self._original_log.copy()
        self._populate_log()