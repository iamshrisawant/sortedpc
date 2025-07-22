# sorter.py

import json
import logging
from pathlib import Path
from typing import Dict, List
from statistics import mean

# --- MODIFIED IMPORTS ---
# Import the new processor, and the actor which will be called at the end.
from src.core.utils.processor import process_file
from src.core.pipelines.actor import act_on_file
from src.core.utils.paths import get_config_file, get_unsorted_folder
from src.core.utils.retriever import retrieve_similar
# --- END MODIFIED IMPORTS ---

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
    return {
        "alpha": float(config.get("alpha", 0.6)),
        "beta": float(config.get("beta", 0.3)),
        "gamma": float(config.get("gamma", 0.05)),
        "delta": float(config.get("delta", 0.05)),
    }


# --- Scoring Helpers (Unchanged) ---
def folder_name_score(file_name: str, folder_name: str) -> float:
    return 1.0 if folder_name.lower() in file_name.lower() else 0.0

def file_type_affinity_score(file_type: str, folder_path: str) -> float:
    try:
        stats_path = get_config_file().parent / "folder_type_stats.json"
        if not stats_path.exists(): return 0.0
        with stats_path.open("r", encoding="utf-8") as f: stats = json.load(f)
        return float(stats.get(folder_path, {}).get(file_type.lower(), 0.0))
    except Exception as e:
        logger.warning(f"[Sorter] Failed to compute type affinity: {e}")
        return 0.0

# --- Format output for actor ---
def _build_output(
    file_data: Dict,
    final_folder: str,
    scoring: Dict[str, Dict],
    candidates: List[str],
    used_fallback: bool = False
) -> Dict:
    # This function now prepares the dictionary that will be passed to the actor
    return {
        "file_path": file_data["file_path"],
        "file_name": file_data["file_name"],
        "file_type": file_data["file_type"],
        "content_hash": file_data["content_hash"],
        "embeddings": file_data["embeddings"],
        "final_folder": final_folder,
        "scoring_breakdown": scoring,
        "similar_folders": candidates,
        "used_fallback": used_fallback
    }

# --- MODIFIED Core Sorting Logic ---
def sort_file(processed_data: Dict) -> Dict:
    """This function now takes the fully processed data as input."""
    file_name = processed_data["file_name"]
    file_type = processed_data["file_type"]
    embeddings = processed_data["embeddings"]
    total_chunks = len(embeddings)

    weights = load_scoring_weights()
    alpha, beta, gamma, delta = weights["alpha"], weights["beta"], weights["gamma"], weights["delta"]

    similar_files = retrieve_similar(embeddings)
    if not similar_files:
        logger.info("[Sorter] No similar files found. Using fallback folder.")
        return _build_output(processed_data, str(get_unsorted_folder()), {}, [], used_fallback=True)

    folder_scores, scoring_details = {}, {}
    for match in similar_files:
        folder_path = match.get("parent_folder_path")
        if not folder_path: continue
        try:
            sim = max(0.0, 1.0 - float(match["distance"]))
            folder_scores.setdefault(folder_path, []).append(sim)
        except (ValueError, TypeError): continue

    final_scores = {}
    for folder_path, sims in folder_scores.items():
        folder_name = Path(folder_path).name
        mean_sim, max_sim, match_count = mean(sims), max(sims), len(sims)
        norm_count = match_count / total_chunks if total_chunks else 0.0
        name_score = folder_name_score(file_name, folder_name)
        type_score = file_type_affinity_score(file_type, folder_path)
        name_type_combo = 0.5 * name_score + 0.5 * type_score
        score = (alpha * mean_sim + beta * max_sim + gamma * norm_count + delta * name_type_combo)
        final_scores[folder_path] = round(score, 6)
        scoring_details[folder_path] = {
            "mean_similarity": round(mean_sim, 4), "max_similarity": round(max_sim, 4),
            "normalized_match_count": round(norm_count, 4), "name_match_score": name_score,
            "type_affinity_score": round(type_score, 4), "final_score": round(score, 6)
        }

    best_folder_path, best_score = max(final_scores.items(), key=lambda x: x[1])
    threshold = 0.7
    if best_score < threshold:
        logger.info(f"[Sorter] Best score {best_score} is below threshold. Using fallback.")
        return _build_output(processed_data, str(get_unsorted_folder()), scoring_details, list(final_scores), used_fallback=True)

    logger.info(f"[Sorter] Best folder: {Path(best_folder_path).name} | Score: {best_score}")
    return _build_output(processed_data, best_folder_path, scoring_details, list(final_scores), used_fallback=False)


# --- MODIFIED Public Entry Point ---
def handle_new_file(file_path: str) -> None:
    """
    Public entry point that orchestrates the entire sorting pipeline for a new file.
    """
    try:
        # 1. Process the file to get embeddings and metadata
        logger.info(f"[Sorter] Processing new file: {file_path}")
        processed_data = process_file(file_path)

        # Abort if processing failed
        if not processed_data or not processed_data.get("embeddings"):
            logger.error(f"[Sorter] Aborting sort for {file_path} due to processing failure.")
            return

        # 2. Sort the file to determine the final destination
        logger.info(f"[Sorter] Sorting file: {processed_data.get('file_name')}")
        sorted_data = sort_file(processed_data)

        # 3. Call the actor to execute the file move and indexing
        logger.info(f"[Sorter] Handing off to actor: {processed_data.get('file_name')}")
        act_on_file(sorted_data)

    except Exception as e:
        logger.error(f"[Sorter] Unhandled exception in sorting pipeline for {file_path}: {e}")


# --- CLI Test (Updated to reflect new flow) ---
if __name__ == "__main__":
    # This CLI test can't fully replicate the new flow as it requires a real file
    # and a FAISS index, but it demonstrates the intended structure.
    print("Sorter CLI test is conceptual. Use the main application to test the full pipeline.")
    # To test, you would call:
    # from sorter import handle_new_file
    # handle_new_file("/path/to/your/test/file.pdf")