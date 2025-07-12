from pathlib import Path
import platform
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

from pathlib import Path
import platform
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

# Resolve base path from this file’s location (absolute path)
BASE_DIR = Path(__file__).resolve().parent.parent  # Points to `src/gui`
BASE_QSS = BASE_DIR / "stylesheets" / "base.qss"
THEME_DIR = BASE_DIR / "stylesheets" / "themes"

def apply_theme(app: QApplication, theme: str = "system"):
    """Applies the selected theme to the app."""
    resolved_theme = resolve_theme(theme)

    try:
        base = BASE_QSS.read_text(encoding="utf-8")
        theme_qss = (THEME_DIR / f"{resolved_theme}.qss").read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error loading QSS: {e}")
        return

    final_qss = merge_theme_variables(base, theme_qss)
    app.setStyleSheet(final_qss)


def resolve_theme(theme: str) -> str:
    """Handles 'system' theme detection fallback."""
    if theme.lower() != "system":
        return theme.lower()

    # Simple system theme guess based on palette or OS
    palette = QGuiApplication.palette()
    bg_color = palette.window().color().lightness()

    return "dark" if bg_color < 128 else "light"

def merge_theme_variables(base_qss: str, theme_qss: str) -> str:
    """Replaces @variable values in base with values from theme file."""
    replacements = {}
    for line in theme_qss.splitlines():
        if ":" not in line:
            continue
        key, value = line.strip().split(":", 1)
        key = key.strip().lstrip("@")
        value = value.strip(" ;")
        replacements[f"@{key}"] = value

    for k, v in replacements.items():
        base_qss = base_qss.replace(k, v)

    return base_qss
