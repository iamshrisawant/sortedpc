# src/utils/logger.py

from loguru import logger
from pathlib import Path
from datetime import datetime
import json

from utils.path_utils import resolve_relative_to_kb_roots

LOG_PATH = Path("src/core/logs/moves.log")
LOG_PATH.parent.mkdir(exist_ok=True)

# Configure the logger
logger.add(
    str(LOG_PATH),
    rotation="1 MB",
    enqueue=True,
    backtrace=False,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

def log_move(file_name: str, final_folder: Path, similar_folders: list[str], replaced: bool = False):
    rel_folder = resolve_relative_to_kb_roots(final_folder)

    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": "file_moved",
        "file": file_name,
        "final_folder": rel_folder,
        "similar_folders": similar_folders,
        "replaced": replaced
    }

    logger.info(json.dumps(log_entry))
