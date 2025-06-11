# main.py

from core.db import init_db
from ui import menu
import core.config

import logging

logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more verbosity
    format='[%(asctime)s] %(levelname)s - %(name)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

def main():
    init_db()
    print("📦 Human-Like File Organizer Initialized")
    menu.launch_menu()

if __name__ == "__main__":
    main()
