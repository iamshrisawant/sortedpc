from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QWidget

def load_component(path: str) -> QWidget:
    file = QFile(path)

    if not file.exists():
        raise FileNotFoundError(f"[UI Loader] File does not exist: {path}")

    if not file.open(QFile.ReadOnly):
        raise IOError(f"[UI Loader] Cannot open file: {path}")

    loader = QUiLoader()
    widget = loader.load(file)
    file.close()

    if widget is None:
        raise RuntimeError(f"[UI Loader] Failed to load widget from: {path}")

    return widget
