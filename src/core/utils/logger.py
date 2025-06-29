from loguru import logger
from pathlib import Path

logger.add("logs/moves.log", rotation="1 MB", enqueue=True, backtrace=False)

def log_move(file_name: str, final_folder: Path, similar_folders: list[str]):
    log_entry = {
        "file": file_name,
        "final_folder": str(final_folder),
        "similar_folders": similar_folders
    }
    logger.info(log_entry)