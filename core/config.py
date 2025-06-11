# core/config.py

import json
from pathlib import Path

DEFAULT_CONFIG = {
    "skip_hidden": True,
    "skip_zero_byte": True,
    "allowed_extensions": [],  # empty = all
}

CONFIG_FILE = Path("config.json")

def load_config() -> dict:
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            try:
                data = json.load(f)
                return {**DEFAULT_CONFIG, **data}
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in config file: {e}")
    return DEFAULT_CONFIG

def save_config(config: dict) -> None:
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
