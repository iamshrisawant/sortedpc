from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QListWidget, QLineEdit,
    QTabWidget, QComboBox, QRadioButton, QButtonGroup,
    QFileDialog, QListWidgetItem, QApplication
)
from PySide6.QtCore import Qt, Signal
import sys


class ConfigWindow(QMainWindow):
    config_saved = Signal(dict)
    config_cancelled = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        self.resize(500, 400)
        self.old_pos = None

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)
        self.layout.setContentsMargins(10, 10, 10, 10)

        self._create_title_bar()

        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #444;
                background: #2e2e2e;
            }
            QTabBar::tab {
                background: #3a3a3a;
                padding: 8px 14px;
                color: white;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                background: #505050;
                font-weight: bold;
            }
        """)

        self._create_paths_tab()
        self._create_preferences_tab()
        self.layout.addWidget(self.tabs)

        # Save & Cancel buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.save_btn = QPushButton("💾 Save")
        self.cancel_btn = QPushButton("❌ Cancel")

        for btn in (self.save_btn, self.cancel_btn):
            btn.setFixedHeight(32)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3a3a3a;
                    border: 1px solid #555;
                    border-radius: 6px;
                    color: white;
                    padding: 5px 15px;
                }
                QPushButton:hover {
                    background-color: #4c4c4c;
                }
            """)

        self.save_btn.clicked.connect(self._on_save)
        self.cancel_btn.clicked.connect(self._on_cancel)

        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        self.layout.addLayout(button_layout)

    def _create_title_bar(self):
        title_bar = QWidget()
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet("background-color: #2e2e2e;")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)

        title_label = QLabel("⚙️ Configurations")
        title_label.setStyleSheet("font-size: 14px; color: white;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        close_btn = QPushButton("×")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #ff5c5c;
            }
        """)
        close_btn.clicked.connect(self._on_cancel)
        title_layout.addWidget(close_btn)

        self.layout.addWidget(title_bar)

    def _create_paths_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)

        # Organized paths
        layout.addWidget(QLabel("Organized Paths:"))
        self.organized_list = QListWidget()
        layout.addWidget(self.organized_list)

        add_org = QPushButton("➕ Add")
        add_org.clicked.connect(lambda: self._add_path(self.organized_list))
        layout.addWidget(add_org)

        # Monitored paths
        layout.addWidget(QLabel("Paths to Monitor:"))
        self.monitor_list = QListWidget()
        layout.addWidget(self.monitor_list)

        add_mon = QPushButton("➕ Add")
        add_mon.clicked.connect(lambda: self._add_path(self.monitor_list))
        layout.addWidget(add_mon)

        self.tabs.addTab(tab, "📂 Paths")

    def _create_preferences_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Learning Schedule
        layout.addWidget(QLabel("Learning Schedule:"))
        self.schedule_group = QButtonGroup(tab)
        for i, label in enumerate(["Daily", "Weekly", "Monthly"]):
            btn = QRadioButton(label)
            btn.setStyleSheet("color: white;")
            if i == 0: btn.setChecked(True)
            self.schedule_group.addButton(btn)
            layout.addWidget(btn)

        # Theme
        layout.addWidget(QLabel("Theme:"))
        self.theme_select = QComboBox()
        self.theme_select.addItems(["Dark", "Light"])
        self.theme_select.setStyleSheet("""
            QComboBox {
                background-color: #3c3c3c;
                color: white;
                padding: 5px;
                border: 1px solid #555;
            }
        """)
        layout.addWidget(self.theme_select)

        self.tabs.addTab(tab, "🛠 Preferences")

    def _add_path(self, list_widget):
        path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if path:
            item = QListWidgetItem(path)
            list_widget.addItem(item)

    def _on_save(self):
        config_data = {
            "organized_paths": [self.organized_list.item(i).text() for i in range(self.organized_list.count())],
            "monitor_paths": [self.monitor_list.item(i).text() for i in range(self.monitor_list.count())],
            "schedule": self.schedule_group.checkedButton().text(),
            "theme": self.theme_select.currentText()
        }
        self.config_saved.emit(config_data)
        self.close()

    def _on_cancel(self):
        self.config_cancelled.emit()
        self.close()

    # Enable dragging
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConfigWindow()
    window.show()
    sys.exit(app.exec())
