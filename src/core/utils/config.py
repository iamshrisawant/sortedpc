# src/core/utils/config.py

import json
from pathlib import Path
from typing import List, Union

STATE_PATH = Path("src/core/data/state.json")


def load_state_json() -> dict:
    if not STATE_PATH.exists():
        return {}
    try:
        with STATE_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def _normalize_paths(paths: List[Union[str, Path]]) -> List[Path]:
    seen = set()
    resolved_paths = []

    for raw in paths:
        try:
            p = Path(raw).expanduser().resolve(strict=False)
            if p.exists() and str(p) not in seen:
                resolved_paths.append(p)
                seen.add(str(p))
        except Exception:
            continue

    return resolved_paths


def load_kb_paths() -> List[Path]:
    state = load_state_json()
    kb_paths = state.get("kb_paths", [])
    if not isinstance(kb_paths, list):
        return []

    normalized = _normalize_paths(kb_paths)
    assert all(isinstance(p, Path) for p in normalized)
    return normalized




def get_organized_roots() -> List[Path]:
    return load_kb_paths()
