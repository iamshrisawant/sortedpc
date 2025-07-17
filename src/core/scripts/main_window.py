import json
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QFileDialog, QLabel, QToolButton, QApplication
)
from PySide6.QtCore import Qt, QEvent, QThread, Signal, QObject
from PySide6.QtGui import QIcon

from gui.scripts.ui_mainWindow import Ui_MainWindow
from gui.scripts.utils import load_component
from core.utils.extractor import extract_text
from core.pipelines.query_engine import resolve_query, answer_query_on_selected_files


class MainWindow(QMainWindow):
    def __init__(self, config=None, paths=None, parent=None):
        super().__init__(parent)
        self.config = config or {}
        self.paths = paths or {}

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setAcceptDrops(True)
        self.file_contexts = []
        self.max_input_lines = 4
        self.typing_bubble = None

        self._apply_launch_position()
        self._init_connections()
        self._show_greeting()

    def _apply_launch_position(self):
        position = self.config.get("launch_position", "Center")
        screen = QApplication.primaryScreen().availableGeometry()
        window_size = self.size()

        if position == "Left Center":
            x = screen.left() + 50
        elif position == "Right Center":
            x = screen.right() - window_size.width() - 50
        else:  # Center
            x = screen.center().x() - window_size.width() // 2

        y = screen.center().y() - window_size.height() // 2
        self.move(x, y)

    def _init_connections(self):
        self.ui.btnConfig.clicked.connect(self._open_config)
        self.ui.btnLog.clicked.connect(self._open_log)
        self.ui.btnSend.clicked.connect(self._on_send)
        self.ui.btnAttach.clicked.connect(self._on_attach)
        self.ui.leMessage.textChanged.connect(self._update_send_button)
        self._update_send_button()
        self.ui.leMessage.installEventFilter(self)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if Path(file_path).is_file():
                self._add_file_card(file_path, sender="user")

    def eventFilter(self, obj, event):
        if obj == self.ui.leMessage and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                if event.modifiers() == Qt.ShiftModifier:
                    return False
                else:
                    self._on_send()
                    return True
        return super().eventFilter(obj, event)

    def _show_greeting(self):
        self.ui.stackedChatArea.setCurrentWidget(self.ui.greetingPage)

    def _switch_to_chat(self):
        self.ui.stackedChatArea.setCurrentWidget(self.ui.page)

    def _open_config(self):
        from gui.scripts.config_window import ConfigWindow
        self.config_window = ConfigWindow(self)
        self.config_window.launch_position_changed.connect(self._on_launch_position_changed)
        self.config_window.show()

    def _on_launch_position_changed(self, new_position):
        self.config["launch_position"] = new_position
        self._apply_launch_position()

    def _open_log(self):
        from gui.scripts.log_window import LogWindow
        self.log_window = LogWindow(self)
        self.log_window.show()

    def _on_send(self):
        msg = self.ui.leMessage.toPlainText().strip()
        if not msg:
            return

        self._switch_to_chat()
        self.ui.leMessage.clear()
        self.ui.leMessage.setFixedHeight(30)

        self._add_chat_bubble("user", msg)
        self.typing_bubble = self._add_chat_bubble("app", "Thinking...")

        self.thread = QThread()
        self.worker = QueryWorker(msg, self.file_contexts.copy())
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._on_llm_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def _on_attach(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Attach files")
        for file_path in files:
            self._switch_to_chat()
            self._add_file_card(file_path, sender="user")

    def _add_chat_bubble(self, sender, text):
        ui_file = self.paths.get(
            "ui_chat_user" if sender == "user" else "ui_chat_app",
            "src/gui/components/ChatBubbleUser.ui" if sender == "user"
            else "src/gui/components/ChatBubbleApp.ui"
        )
        bubble = load_component(ui_file)
        bubble.findChild(QLabel, "labelMessage").setText(text)
        self.ui.chatLayout.addWidget(bubble)
        self._scroll_to_bottom()
        return bubble

    def _add_file_card(self, file_path, sender):
        card = load_component(self.paths.get("ui_file_card", "src/gui/components/FileCard.ui"))
        name = Path(file_path).name
        card.findChild(QLabel, "lblFileName").setText(name)

        card.findChild(QToolButton, "btnOpen").clicked.connect(lambda: Path(file_path).resolve().open())

        btn_delete = card.findChild(QToolButton, "btnDelete")
        if btn_delete:
            btn_delete.clicked.connect(lambda: self._remove_file_card(card, file_path))

        self.ui.chatLayout.addWidget(card)
        self._scroll_to_bottom()

        try:
            text = extract_text(file_path)
            self.file_contexts.append((file_path, text))
        except Exception:
            pass

    def _remove_file_card(self, card, file_path):
        self.file_contexts = [pair for pair in self.file_contexts if pair[0] != file_path]
        card.setParent(None)

    def _on_llm_finished(self, result: dict):
        if self.typing_bubble:
            self.ui.chatLayout.removeWidget(self.typing_bubble)
            self.typing_bubble.deleteLater()
            self.typing_bubble = None

        self._add_chat_bubble("app", result["answer"])

        if result.get("references"):
            ref_text = "📎 Used context from:\n" + "\n".join(result["references"])
            self._add_chat_bubble("app", ref_text)

        self.file_contexts = []

    def _scroll_to_bottom(self):
        self.ui.chatArea.verticalScrollBar().setValue(
            self.ui.chatArea.verticalScrollBar().maximum())

    def _update_send_button(self):
        has_text = bool(self.ui.leMessage.toPlainText().strip())
        icon_path = "src/gui/icons/send.png" if has_text else "src/gui/icons/refresh.png"
        self.ui.btnSend.setIcon(QIcon(icon_path))
        self.ui.btnSend.setEnabled(has_text)


class QueryWorker(QObject):
    finished = Signal(dict)

    def __init__(self, message, file_contexts):
        super().__init__()
        self.message = message
        self.file_contexts = file_contexts

    def run(self):
        if self.file_contexts:
            texts = [txt for _, txt in self.file_contexts]
            refs = [Path(path).name for path, _ in self.file_contexts]
            result = answer_query_on_selected_files(self.message, texts)
            result["references"] = refs
        else:
            answer, refs = resolve_query(self.message)
            result = {"answer": answer, "references": refs}

        self.finished.emit(result)
