import logging
from pathlib import Path
from typing import Dict, Optional

from src.core.utils.paths import get_faiss_index_path, get_faiss_metadata_path
from src.core.utils.logger import log_move, log_correction, get_latest_log_entry
from src.core.utils.mover import move_file
from src.core.utils.indexer import index_file
from src.core.utils.notifier import notify_file_sorted

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")


# ─── Handle Normal File Sort ────────────────────────────────────────────────
def handle_sorted_file(sorted_data: Dict):
    file_path = Path(sorted_data["file_path"]).resolve()
    final_folder = Path(sorted_data["final_folder"]).resolve()
    embeddings = sorted_data.get("embeddings", [])
    used_fallback = sorted_data.get("used_fallback", False)

    # 1. Log the move
    log_move(sorted_data)

    # 2. Move the file to final folder
    new_path = Path(move_file(file_path, final_folder)).resolve()

    # 3. Index the moved file
    index_file(
        embeddings=embeddings,
        file_metadata={
            "file_path": str(new_path),
            "file_name": new_path.stem,
            "parent_folder": final_folder.name,
            "parent_folder_path": str(final_folder),
            "file_type": new_path.suffix.lstrip(".").lower(),
            "content_hash": sorted_data.get("content_hash"),
        },
        faiss_index_path=get_faiss_index_path(),
        metadata_store_path=get_faiss_metadata_path()
    )

    # 4. Notify the user
    notify_file_sorted(
        file_path=str(new_path),
        final_folder=final_folder.name,
        similar_folders=sorted_data.get("similar_folders", [])
    )

    move_status = "with fallback" if used_fallback else "normally"
    logger.info(f"[Actor] File moved {move_status}: {file_path.name} → {final_folder}")


# ─── Handle Manual Correction ───────────────────────────────────────────────
def handle_correction(file_path: str, corrected_folder: str):
    corrected_folder = Path(corrected_folder).resolve()

    # 1. Resolve actual source file location based on log
    latest_entry = get_latest_log_entry(file_path)
    if latest_entry:
        file_name = Path(file_path).name
        file_path = Path(latest_entry["final_folder"]) / file_name
    else:
        file_path = Path(file_path).resolve()

    # 2. Log correction
    log_correction(str(file_path), str(corrected_folder))

    # 3. Move file
    new_path = Path(move_file(file_path, corrected_folder)).resolve()

    # 4. Reindex with updated location, no embeddings
    index_file(
        embeddings=None,
        file_metadata={
            "file_path": str(new_path),
            "file_name": new_path.stem,
            "parent_folder": corrected_folder.name,
            "parent_folder_path": str(corrected_folder),
            "file_type": new_path.suffix.lstrip(".").lower(),
            "content_hash": None
        },
        faiss_index_path=get_faiss_index_path(),
        metadata_store_path=get_faiss_metadata_path()
    )

    # 5. Notify user
    notify_file_sorted(
        file_path=str(new_path),
        final_folder=corrected_folder.name,
        similar_folders=[]
    )

    logger.info(f"[Actor] Correction applied and reindexed: {new_path.name}")


# ─── Entrypoint for Sorter ──────────────────────────────────────────────────
def act_on_file(sorted_data: Dict):
    handle_sorted_file(sorted_data)


# ─── Standalone Test ────────────────────────────────────────────────────────
if __name__ == "__main__":
    dummy = {
        "file_path": "/some/path/sample.pdf",
        "file_name": "sample",
        "file_type": "pdf",
        "content_hash": "dummyhash",
        "final_folder": str(Path.home() / "Documents" / "sortedpc" / "reports"),
        "similar_folders": ["reports", "memos"],
        "scoring_breakdown": {
            "reports": {
                "mean_similarity": 0.83,
                "max_similarity": 0.92,
                "match_count": 4,
                "name_match_score": 1.0
            },
            "memos": {
                "mean_similarity": 0.62,
                "max_similarity": 0.70,
                "match_count": 2,
                "name_match_score": 0.0
            }
        },
        "embeddings": [[0.1] * 384],
        "used_fallback": False
    }

    act_on_file(dummy)
