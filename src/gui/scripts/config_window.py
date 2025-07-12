from PySide6.QtWidgets import (
    QDialog, QListWidgetItem, QFileDialog, QMessageBox, QLabel, QToolButton,
    QPushButton, QApplication, QVBoxLayout, QProgressBar, QListWidget
)
from PySide6.QtCore import Signal, Qt, QThread, QObject
from pathlib import Path
import json

from gui.scripts.themes import apply_theme
from .ui_configWindow import Ui_Dialog
from gui.scripts.utils import load_component
from core.kb_builder import build_kb, INDEX_FILE, META_FILE
from core.file_watcher import reset_and_run_watcher

CONFIG_FILE = Path("src/core/data/state.json")


class KBBuildDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Building Knowledge Base")
        self.setModal(True)
        self.setMinimumWidth(300)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        self.label = QLabel("Please wait while the KB is being built...", self)
        self.progress = QProgressBar(self)
        self.progress.setRange(0, 0)  # Indeterminate

        layout.addWidget(self.label)
        layout.addWidget(self.progress)


class KBBuildWorker(QObject):
    finished = Signal()

    def __init__(self, kb_paths):
        super().__init__()
        self.kb_paths = kb_paths

    def run(self):
        for folder in self.kb_paths:
            build_kb(Path(folder), rebuild=False)
        self.finished.emit()


class ConfigWindow(QDialog):
    launch_position_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle("Configuration")
        self.setMinimumWidth(400)

        self.kb_paths = []
        self.watch_paths = []

        self._load_config()
        self._populate_list(self.ui.lwKBPaths, self.kb_paths, is_kb=True)
        self._populate_list(self.ui.lwWatch, self.watch_paths, is_kb=False)

        self.ui.cbTheme.currentTextChanged.connect(self._apply_selected_theme)
        self.ui.cbTheme.setCurrentText(self._theme)
        self.ui.cbLaunchPos.setCurrentText(self._launch_position)
        apply_theme(QApplication.instance(), self._theme)

        self.ui.bbButtons.accepted.connect(self._save_config)
        self.ui.bbButtons.rejected.connect(self.close)
        self.ui.bbButtons.button(self.ui.bbButtons.StandardButton.RestoreDefaults).clicked.connect(self._restore_defaults)

    def _apply_selected_theme(self):
        theme = self.ui.cbTheme.currentText()
        apply_theme(QApplication.instance(), theme)

    def _load_config(self):
        self._theme = "System"
        self._launch_position = "Center"
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                self.kb_paths = data.get("kb_paths", [])
                self.watch_paths = data.get("watch_paths", [])
                self._theme = data.get("theme", "System")
                self._launch_position = data.get("launch_position", "Center")

    def _save_config(self):
        self.kb_paths = self._collect_paths_from_list(self.ui.lwKBPaths)
        self.watch_paths = self._collect_paths_from_list(self.ui.lwWatch)

        self.state_data = {
            "kb_paths": [str(p) for p in self.kb_paths],
            "watch_paths": [str(p) for p in self.watch_paths],
            "theme": self.ui.cbTheme.currentText(),
            "launch_position": self.ui.cbLaunchPos.currentText(),
        }

        self.launch_position_changed.emit(self.state_data["launch_position"])

        # Show progress dialog
        self.kb_dialog = KBBuildDialog(self)
        self.kb_dialog.show()

        # Start thread to build KB
        self.kb_thread = QThread()
        self.kb_worker = KBBuildWorker(self.kb_paths)
        self.kb_worker.moveToThread(self.kb_thread)

        self.kb_thread.started.connect(self.kb_worker.run)
        self.kb_worker.finished.connect(self.kb_thread.quit)
        self.kb_worker.finished.connect(self.kb_worker.deleteLater)
        self.kb_thread.finished.connect(self.kb_thread.deleteLater)
        self.kb_worker.finished.connect(self._on_kb_build_complete)

        self.kb_thread.start()

    def _on_kb_build_complete(self):
        self.kb_dialog.accept()

        if Path(INDEX_FILE).exists() and Path(META_FILE).exists():
            reset_and_run_watcher(self.watch_paths)

        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.state_data, f, indent=2)

        QMessageBox.information(self, "Saved", "Configuration saved successfully.")
        self.accept()

    def _restore_defaults(self):
        self.kb_paths = []
        self.watch_paths = []
        self.ui.cbTheme.setCurrentIndex(0)
        self.ui.cbLaunchPos.setCurrentIndex(1)
        self.ui.lwKBPaths.clear()
        self.ui.lwWatch.clear()
        self._add_add_button(self.ui.lwKBPaths, is_kb=True)
        self._add_add_button(self.ui.lwWatch, is_kb=False)

    def _populate_list(self, list_widget, paths, is_kb):
        list_widget.clear()
        for path in paths:
            self._add_path_row(list_widget, path)
        self._add_add_button(list_widget, is_kb)

    def _add_path_row(self, list_widget, path):
        if not path or path in self._get_all_paths_from_list(list_widget):
            return

        row = load_component("src/gui/components/PathRow.ui")
        row.setObjectName("PathRow")

        label = row.findChild(QLabel, "label")
        delete_btn = row.findChild(QToolButton, "toolButton")

        label.setText(path)
        delete_btn.clicked.connect(lambda: self._remove_row(list_widget, row))

        item = QListWidgetItem()
        item.setSizeHint(row.sizeHint())
        list_widget.insertItem(list_widget.count() - 1, item)
        list_widget.setItemWidget(item, row)

    def _add_add_button(self, list_widget, is_kb):
        row = load_component("src/gui/components/AddPathRow.ui")
        row.setObjectName("AddPathRow")

        btn = row.findChild(QPushButton, "btnAddPath")
        if not btn:
            label = row.findChild(QLabel, "label")
            label.setText("➕ Add new")
            label.setCursor(Qt.PointingHandCursor)
            label.mousePressEvent = lambda event: self._on_add_clicked(list_widget)
        else:
            btn.setText("➕ Add new")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda: self._on_add_clicked(list_widget))

        item = QListWidgetItem()
        item.setSizeHint(row.sizeHint())
        list_widget.addItem(item)
        list_widget.setItemWidget(item, row)

    def _on_add_clicked(self, list_widget):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            existing = self._get_all_paths_from_list(list_widget)
            if folder in existing:
                QMessageBox.warning(self, "Duplicate", "This folder is already added.")
                return
            self._add_path_row(list_widget, folder)

    def _remove_row(self, list_widget, row_widget):
        for i in range(list_widget.count()):
            if list_widget.itemWidget(list_widget.item(i)) == row_widget:
                list_widget.takeItem(i)
                break

    def _get_all_paths_from_list(self, list_widget):
        paths = []
        for i in range(list_widget.count()):
            widget = list_widget.itemWidget(list_widget.item(i))
            if widget and widget.objectName() == "PathRow":
                label = widget.findChild(QLabel, "label")
                if label:
                    paths.append(label.text())
        return paths

    def _collect_paths_from_list(self, list_widget: QListWidget) -> list[Path]:
        raw_paths = self._get_all_paths_from_list(list_widget)
        resolved_paths = []
        seen = set()

        for p in raw_paths:
            try:
                resolved = Path(p).expanduser().resolve(strict=False)
                if resolved.exists() and str(resolved) not in seen:
                    resolved_paths.append(resolved)
                    seen.add(str(resolved))
                elif not resolved.exists():
                    QMessageBox.warning(self, "Warning", f"Skipping invalid path:\n{p}")
            except Exception as e:
                QMessageBox.critical(self, "Path Error", f"Failed to process path:\n{p}\n\n{e}")

        return resolved_paths