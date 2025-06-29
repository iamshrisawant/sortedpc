from loguru import logger
from pathlib import Path
from datetime import datetime
import json

LOG_PATH = Path("logs/moves.log")
LOG_PATH.parent.mkdir(exist_ok=True)

# Configure the logger
logger.add(
    str(LOG_PATH),
    rotation="1 MB",
    enqueue=True,
    backtrace=False,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

def log_move(file_name: str, final_folder: Path, similar_folders: list[str]):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": "file_moved",
        "file": file_name,
        "final_folder": str(final_folder),
        "similar_folders": similar_folders
    }
    logger.info(json.dumps(log_entry))
