import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict

from src.core.utils.paths import get_logs_path

logger = logging.getLogger(__name__)


# ─── Internal: Load Logs While Optionally Filtering ──────────────────────────
def _load_existing_logs(
    log_file: Path,
    target_file_path: str,
    category_to_replace: Optional[str] = None
) -> List[dict]:
    entries = []
    if not log_file.exists():
        return entries

    target_file_path = str(Path(target_file_path).resolve())

    with log_file.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
                if not (
                    entry.get("file_path") == target_file_path and
                    entry.get("category") == category_to_replace
                ):
                    entries.append(entry)
            except json.JSONDecodeError:
                continue
    return entries


# ─── Log a System Move (from Sorter/Actor) ───────────────────────────────────
def log_move(sorted_data: dict, log_file: Optional[Path] = None):
    log_file = log_file or get_logs_path()
    file_path = str(Path(sorted_data["file_path"]).resolve())

    log_entries = _load_existing_logs(log_file, file_path, category_to_replace="moves")

    new_entry = {
        "category": "moves",
        "file_path": file_path,
        "file_name": sorted_data["file_name"],
        "file_type": sorted_data["file_type"],
        "content_hash": sorted_data.get("content_hash", ""),
        "final_folder": str(Path(sorted_data["final_folder"]).resolve()),
        "similar_folders": sorted_data.get("similar_folders", []),
        "scoring_breakdown": sorted_data.get("scoring_breakdown", {}),
        "timestamp": datetime.now().isoformat()
    }

    log_entries.append(new_entry)

    with log_file.open("w", encoding="utf-8") as f:
        for entry in log_entries:
            f.write(json.dumps(entry) + "\n")

    logger.info(f"[Logger] Logged system move for {file_path}")


# ─── Log a Manual Correction (from GUI/Main) ─────────────────────────────────
def log_correction(file_path: str, corrected_folder: str, log_file: Optional[Path] = None):
    log_file = log_file or get_logs_path()
    file_path = str(Path(file_path).resolve())
    corrected_folder = str(Path(corrected_folder).resolve())

    log_entries = _load_existing_logs(log_file, file_path, category_to_replace="corrections")

    new_entry = {
        "category": "corrections",
        "file_path": file_path,
        "file_name": Path(file_path).stem,
        "file_type": Path(file_path).suffix.lstrip("."),
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


# ─── Check If a File Has Been Handled ────────────────────────────────────────
def has_been_handled(file_path: str, content_hash: Optional[str] = None) -> bool:
    log_file = get_logs_path()
    if not log_file.exists():
        return False

    file_path = str(Path(file_path).resolve())

    with log_file.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
                if entry.get("category") in {"moves", "corrections"}:
                    logged_path = str(Path(entry.get("file_path", "")).resolve())
                    if logged_path == file_path:
                        return True
                    if content_hash and entry.get("content_hash") == content_hash:
                        return True
            except json.JSONDecodeError:
                continue
    return False


# ─── Get Latest Move or Correction Log Entry for a File ──────────────────────
def get_latest_log_entry(file_path: str) -> Optional[Dict]:
    log_file = get_logs_path()
    if not log_file.exists():
        return None

    file_name = Path(file_path).name

    with log_file.open("r", encoding="utf-8") as f:
        lines = [
            json.loads(line)
            for line in f
            if line.strip()
        ]

    # Return the most recent move/correction entry with matching file name
    for entry in reversed(lines):
        if entry.get("file_path", "").endswith(file_name) and entry.get("category") in {"moves", "corrections"}:
            return entry
    return None
