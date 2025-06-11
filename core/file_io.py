# file_io.py

from pathlib import Path
from typing import Generator
import datetime
import uuid
import os

import logging
logger = logging.getLogger(__name__)

def scan_directory(path: str, config: dict) -> Generator[dict, None, None]:
    """
    Yields metadata dicts for all valid files under the provided path.
    Config controls skip rules (e.g., hidden, zero-byte, etc.).
    """
    base_path = Path(path)
    if not base_path.exists() or not base_path.is_dir():
        logger.error(f"Invalid directory path: {path}")
        raise ValueError(f"Invalid directory path: {path}")

    scan_id = uuid.uuid4().hex  # Optional: attach to logs/DB if needed

    for file_path in base_path.rglob('*'):
        try:
            stat = file_path.stat()
        except (PermissionError, FileNotFoundError):
            continue  # Skip files we can't access

        if file_path.is_file() and is_valid_file(file_path, stat, config):
            yield extract_metadata(file_path, stat, scan_id)

def is_valid_file(file_path: Path, stat: os.stat_result, config: dict) -> bool:
    """
    Checks file against skip criteria (hidden, zero-byte, etc.).
    """
    
    if config.get('skip_hidden', True):
        if file_path.name.startswith('.') or any(part.startswith('.') for part in file_path.parts):
            logger.debug(f"Skipping hidden file: {file_path}")
            return False

    if config.get('skip_zero_byte', True) and stat.st_size == 0:
        logger.debug(f"Skipping zero-byte file: {file_path}")
        return False

    max_size = config.get('max_file_size_bytes')
    if max_size and stat.st_size > max_size:
        return False

    return True

def extract_metadata(file_path: Path, stat: os.stat_result, scan_id: str = None) -> dict:
    """
    Extracts file path, size, timestamps, extension, parent folders, etc.
    """
    return {
        'scan_id': scan_id,
        'path': str(file_path.resolve()),
        'name': file_path.name,
        'extension': file_path.suffix.lower(),
        'size_bytes': stat.st_size,
        'created': datetime.datetime.fromtimestamp(stat.st_ctime).isoformat(),
        'modified': datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
        'accessed': datetime.datetime.fromtimestamp(stat.st_atime).isoformat(),
        'parent_dirs': list(file_path.resolve().parents)[::-1][1:]  # root → immediate parent
    }
