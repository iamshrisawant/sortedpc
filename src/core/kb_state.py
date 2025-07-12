# src/core/kb_state.py

import json
from pathlib import Path
from typing import List

STATE_FILE = Path("src/core/data/state.json")


def _load_state() -> dict:
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}


def _save_state(data: dict):
    with open(STATE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_processed_paths() -> List[str]:
    return _load_state().get("processed_kb_paths", [])


def is_processed(folder: Path) -> bool:
    return str(folder.resolve()) in get_processed_paths()


def mark_processed(folder: Path):
    data = _load_state()
    paths = set(data.get("processed_kb_paths", []))
    paths.add(str(folder.resolve()))
    data["processed_kb_paths"] = sorted(paths)
    _save_state(data)
