# main.py

import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow  # Adjust path if your MainWindow file is elsewhere

def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
