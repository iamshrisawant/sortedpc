import logging
from pathlib import Path
from typing import Dict

from src.core.utils.logger import log_move, log_correction
from src.core.utils.mover import move_file
from src.core.utils.indexer import index_file
from src.core.utils.notifier import notify_user
from src.core.utils.paths import get_logs_path

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")


# --- Handle sorter decision ---
def handle_sorted_file(sorted_data: Dict):
    file_path = Path(sorted_data["file_path"]).resolve()
    final_folder = Path(sorted_data["new_parent_folder"]).resolve()
    embeddings = sorted_data["embeddings"]

    # 1. Log move decision
    log_move(sorted_data)

    # 2. Move file
    new_path = move_file(file_path, final_folder)

    # 3. Index embeddings
    index_file(
        embedding=embeddings,
        file_path=str(new_path),
        file_name=sorted_data["file_name"],
        parent_folder=final_folder.name,
        file_type=sorted_data["file_type"]
    )

    # 4. Send user notification
    notify_user(
        file_path=str(new_path),
        final_folder=final_folder.name,
        similar_folders=sorted_data.get("similar_folders", [])
    )

    logger.info(f"[Actor] File moved and indexed: {file_path.name} → {final_folder}")


# --- Handle correction from GUI ---
def handle_correction(file_path: str, corrected_folder: str):
    file_path = Path(file_path).resolve()
    corrected_folder = Path(corrected_folder).resolve()

    # 1. Log the correction
    log_correction(str(file_path), str(corrected_folder))

    # 2. Move again
    new_path = move_file(file_path, corrected_folder)

    # 3. Re-index with updated metadata
    index_file(
        embedding=None,  # Let indexer decide if embedding already exists
        file_path=str(new_path),
        file_name=new_path.stem,
        parent_folder=corrected_folder.name,
        file_type=new_path.suffix.lstrip('.').lower()
    )

    # 4. Notify correction
    notify_user(
        file_path=str(new_path),
        final_folder=corrected_folder.name,
        similar_folders=[]
    )

    logger.info(f"[Actor] Correction applied and reindexed for: {new_path}")


# --- Entrypoint for system ---
def act_on_file(sorted_data: Dict):
    handle_sorted_file(sorted_data)


# --- CLI or script test ---
if __name__ == "__main__":
    dummy = {
        "file_path": "/some/path/sample.pdf",
        "file_name": "sample",
        "file_type": "pdf",
        "content_hash": "dummyhash",
        "new_parent_folder": str(Path.home() / "Documents" / "sortedpc" / "reports"),
        "similar_folders": ["reports", "memos"],
        "scoring_breakdown": {"reports": 0.83, "memos": 0.62},
        "embeddings": [[0.1]*768]
    }

    act_on_file(dummy)
