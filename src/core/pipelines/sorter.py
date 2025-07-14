import json
import logging
from pathlib import Path
from typing import Dict, List
from statistics import mean

from src.core.utils.paths import get_config_file, get_unsorted_folder
from src.core.utils.retriever import retrieve_similar

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")


# --- Load scoring weights from config ---
def load_scoring_weights() -> Dict[str, float]:
    config_path = get_config_file()
    if not config_path.exists():
        logger.warning("[Sorter] Config file not found. Using default weights.")
        return {"alpha": 0.6, "beta": 0.3, "gamma": 0.05, "delta": 0.05}

    with config_path.open("r", encoding="utf-8") as f:
        config = json.load(f)

    weights = config.get("weights", {})
    return {
        "alpha": float(weights.get("alpha", 0.6)),
        "beta": float(weights.get("beta", 0.3)),
        "gamma": float(weights.get("gamma", 0.05)),
        "delta": float(weights.get("delta", 0.05)),
    }


# --- Simple folder name relevance to file name ---
def folder_name_score(file_name: str, folder_name: str) -> float:
    return 1.0 if folder_name.lower() in file_name.lower() else 0.0


# --- Sort logic ---
def sort_file(file_data: Dict) -> Dict:
    file_name = file_data["file_name"]
    embeddings = file_data["embeddings"]

    weights = load_scoring_weights()
    alpha = weights["alpha"]
    beta = weights["beta"]
    gamma = weights["gamma"]
    delta = weights["delta"]

    similar_files = retrieve_similar(embeddings)
    if not similar_files:
        logger.info("[Sorter] No similar files found. Using fallback.")
        return _build_output(file_data, str(get_unsorted_folder()), {}, [], embeddings)

    # Group by folders
    folder_groups = {}
    for match in similar_files:
        folder = match["parent_folder"]
        sim = 1.0 - float(match["distance"])
        folder_groups.setdefault(folder, []).append(sim)

    # Score folders
    scoring = {}
    for folder, sims in folder_groups.items():
        score = (
            alpha * mean(sims) +
            beta * max(sims) +
            gamma * len(sims) +
            delta * folder_name_score(file_name, folder)
        )
        scoring[folder] = round(score, 6)

    # Final decision
    best_folder, best_score = max(scoring.items(), key=lambda x: x[1])
    if best_score < 0.7:
        logger.info(f"[Sorter] Best score {best_score} below threshold. Using fallback.")
        final_folder = str(get_unsorted_folder())
    else:
        final_folder = best_folder

    return _build_output(file_data, final_folder, scoring, list(scoring.keys()), embeddings)


# --- Output Formatter ---
def _build_output(
    file_data: Dict,
    final_folder: str,
    scoring: Dict[str, float],
    candidates: List[str],
    embeddings: List
) -> Dict:
    return {
        "file_path": file_data["file_path"],
        "file_name": file_data["file_name"],
        "file_type": file_data["file_type"],
        "content_hash": file_data["content_hash"],
        "new_parent_folder": final_folder,
        "scoring_breakdown": scoring,
        "similar_folders": candidates,
        "embeddings": embeddings,
    }


# --- Public Entry Point ---
def handle_new_file(file_data: Dict) -> Dict:
    return sort_file(file_data)


# --- For testing ---
if __name__ == "__main__":
    dummy = {
        "file_path": "/test/path/file.pdf",
        "file_name": "file",
        "file_type": "pdf",
        "content_hash": "abcd1234",
        "parent_folder": "misc",
        "embeddings": [[0.1]*768]
    }
    print(json.dumps(handle_new_file(dummy), indent=2))
