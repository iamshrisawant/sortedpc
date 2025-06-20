from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel, QTextEdit
)
from PySide6.QtCore import Qt, QPoint, QTimer
import sys

from config_window import ConfigWindow


class FramelessWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        self.setMinimumWidth(600)
        self.resize(600, 120)  # Initial size (height = width/5)

        self.old_pos = None

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Title bar
        self._create_title_bar()

        # Content area
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(15, 10, 15, 10)
        content_layout.setSpacing(10)

        # Welcome message
        welcome_label = QLabel("👋 Welcome to sortedPC!")
        welcome_label.setStyleSheet("font-size: 16px; color: white;")
        content_layout.addWidget(welcome_label)

        # Button row
        button_row = QHBoxLayout()
        button_row.setSpacing(10)

        self.config_button = QPushButton("⚙️ Config Window")
        self.config_button.clicked.connect(self.open_config_window)
        self.log_button = QPushButton("📝 Log Window")

        for btn in (self.config_button, self.log_button):
            btn.setFixedHeight(32)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3c3c3c;
                    color: white;
                    font-size: 13px;
                    border: 1px solid #555;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #505050;
                }
            """)

        button_row.addWidget(self.config_button)
        button_row.addWidget(self.log_button)
        content_layout.addLayout(button_row)

        # Input area (Text editor + buttons)
        input_panel = QVBoxLayout()
        input_panel.setSpacing(8)

        # Text editor
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("Ask your question here...")
        self.content_edit.setStyleSheet("""
            QTextEdit {
                background-color: #2e2e2e;
                border: 1px solid #444;
                padding: 8px;
                font-size: 14px;
                color: white;
                border-radius: 6px;
            }
        """)
        self.content_edit.textChanged.connect(self._adjust_height)
        input_panel.addWidget(self.content_edit)

        input_buttons = QHBoxLayout()
        input_buttons.setSpacing(10)

        self.attach_button = QPushButton("📎 Attach")
        self.voice_button = QPushButton("🎤 Voice")
        self.send_button = QPushButton("📤 Send Query")
        self.new_chat_button = QPushButton("🆕 New Chat")

        for btn in [self.attach_button, self.voice_button, self.send_button, self.new_chat_button]:
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(30)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3a3a3a;
                    color: white;
                    border: 1px solid #555;
                    border-radius: 5px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #4c4c4c;
                }
            """)
            input_buttons.addWidget(btn)

        input_panel.addLayout(input_buttons)
        content_layout.addLayout(input_panel)
        self.layout.addWidget(content_container)

        # Initial height adjustment
        QTimer.singleShot(0, self._adjust_height)

    def _create_title_bar(self):
        title_bar = QWidget()
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet("background-color: #2e2e2e;")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)

        label = QLabel("SortedPC")
        label.setStyleSheet("color: white; font-size: 14px;")
        title_layout.addWidget(label)
        title_layout.addStretch()

        minimize_btn = QPushButton("-")
        minimize_btn.setFixedSize(30, 30)
        minimize_btn.setStyleSheet(self._button_style())
        minimize_btn.clicked.connect(self.showMinimized)

        close_btn = QPushButton("×")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet(self._button_style(close=True))
        close_btn.clicked.connect(self.close)

        title_layout.addWidget(minimize_btn)
        title_layout.addWidget(close_btn)

        self.layout.addWidget(title_bar)

    def _button_style(self, close=False):
        if close:
            return """
                QPushButton {
                    background-color: transparent;
                    color: white;
                    border: none;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #ff5c5c;
                }
            """
        return """
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #444;
            }
        """

    def _adjust_height(self):
        try:
            if not hasattr(self, "content_edit") or self.content_edit is None:
                return

            screen_geometry = QApplication.primaryScreen().availableGeometry()
            screen_center = screen_geometry.center()
            width = self.width()
            min_height = width // 5
            max_height = (6 * width) // 5

            document_height = self.content_edit.document().size().height()
            content_height = int(document_height * 1.8) + 100  # scaling + title bar space

            new_height = max(min_height, min(content_height, max_height))
            self.resize(width, new_height)

            # Recenter window
            new_x = screen_center.x() - width // 2
            new_y = screen_center.y() - new_height // 2
            self.move(new_x, new_y)
        except RuntimeError:
            return

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(0, self._adjust_height)

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
    
    def open_config_window(self):
        self.config_window = ConfigWindow()
        self.config_window.config_saved.connect(self.handle_config_saved)
        self.config_window.config_cancelled.connect(self.handle_config_cancelled)
        self.config_window.show()
    
    def handle_config_saved(self, config):
        print("Config saved:", config)

    def handle_config_cancelled(self):
        print("Config cancelled.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FramelessWindow()
    window.show()
    sys.exit(app.exec())
