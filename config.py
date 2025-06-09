import os

# Root of your project (where main.py lives)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Config folder inside your project
CONFIG_DIR = os.path.join(BASE_DIR, 'config')

# Full path to config.json
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')
