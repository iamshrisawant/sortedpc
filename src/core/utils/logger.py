import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional

from src.core.utils.paths import get_logs_path

import logging
logger = logging.getLogger(__name__)


# --- Internal: Load log entries except current file ---
def _load_existing_logs(log_file: Path, target_file_path: str) -> List[dict]:
    entries = []
    if not log_file.exists():
        return entries

    with log_file.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
                if entry.get("file_path") != target_file_path:
                    entries.append(entry)
            except json.JSONDecodeError:
                continue
    return entries


# --- Public: Log move (from sorter) ---
def log_move(
    sorted_data: dict,
    log_file: Optional[Path] = None
):
    log_file = log_file or get_logs_path()
    file_path = str(Path(sorted_data["file_path"]).resolve())

    log_entries = _load_existing_logs(log_file, file_path)

    new_entry = {
        "category": "move",
        "file_path": file_path,
        "file_name": sorted_data["file_name"],
        "file_type": sorted_data["file_type"],
        "content_hash": sorted_data.get("content_hash", ""),
        "final_folder": str(Path(sorted_data["new_parent_folder"]).resolve()),
        "similar_folders": sorted_data.get("similar_folders", []),
        "scoring_breakdown": sorted_data.get("scoring_breakdown", {}),
        "timestamp": datetime.now().isoformat()
    }

    log_entries.append(new_entry)

    with log_file.open("w", encoding="utf-8") as f:
        for entry in log_entries:
            f.write(json.dumps(entry) + "\n")

    logger.info(f"[Logger] Logged system move for {file_path}")


# --- Public: Log correction (from GUI) ---
def log_correction(
    file_path: str,
    corrected_folder: str,
    log_file: Optional[Path] = None
):
    log_file = log_file or get_logs_path()
    file_path = str(Path(file_path).resolve())
    corrected_folder = str(Path(corrected_folder).resolve())

    log_entries = _load_existing_logs(log_file, file_path)

    new_entry = {
        "category": "correction",
        "file_path": file_path,
        "file_name": Path(file_path).stem,
        "file_type": Path(file_path).suffix.lstrip('.'),
        "final_folder": corrected_folder,
        "similar_folders": [],
        "scoring_breakdown": {},
        "timestamp": datetime.now().isoformat()
    }

    log_entries.append(new_entry)

    with log_file.open("w", encoding="utf-8") as f:
        for entry in log_entries:
            f.write(json.dumps(entry) + "\n")

    logger.info(f"[Logger] Logged correction for {file_path}")
