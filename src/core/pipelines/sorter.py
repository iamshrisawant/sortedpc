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

    return {
        "alpha": float(config.get("alpha", 0.6)),
        "beta": float(config.get("beta", 0.3)),
        "gamma": float(config.get("gamma", 0.05)),
        "delta": float(config.get("delta", 0.05)),
    }


# --- Simple name match scorer ---
def folder_name_score(file_name: str, folder_name: str) -> float:
    return 1.0 if folder_name.lower() in file_name.lower() else 0.0


# --- File type affinity score (from learned stats) ---
def file_type_affinity_score(file_type: str, folder_path: str) -> float:
    try:
        stats_path = get_config_file().parent / "folder_type_stats.json"
        if not stats_path.exists():
            return 0.0
        with stats_path.open("r", encoding="utf-8") as f:
            stats = json.load(f)
        return float(stats.get(folder_path, {}).get(file_type.lower(), 0.0))
    except Exception as e:
        logger.warning(f"[Sorter] Failed to compute type affinity: {e}")
        return 0.0


# --- Core sorting logic ---
def sort_file(file_data: Dict) -> Dict:
    file_name = file_data["file_name"]
    file_type = file_data["file_type"]
    embeddings = file_data["embeddings"]
    total_chunks = len(embeddings)

    weights = load_scoring_weights()
    alpha, beta, gamma, delta = weights["alpha"], weights["beta"], weights["gamma"], weights["delta"]

    similar_files = retrieve_similar(embeddings)
    if not similar_files:
        logger.info("[Sorter] No similar files found. Using fallback folder.")
        return _build_output(file_data, str(get_unsorted_folder()), {}, [], embeddings, used_fallback=True)

    # --- Group by full folder paths and score ---
    folder_scores = {}
    scoring_details = {}

    for match in similar_files:
        folder_path = match.get("parent_folder_path")
        if not folder_path:
            continue
        try:
            sim = max(0.0, 1.0 - float(match["distance"]))  # Clamp similarity
        except (ValueError, TypeError):
            continue
        folder_scores.setdefault(folder_path, []).append(sim)

    final_scores = {}
    for folder_path, sims in folder_scores.items():
        folder_name = Path(folder_path).name
        mean_sim = mean(sims)
        max_sim = max(sims)
        match_count = len(sims)
        norm_count = match_count / total_chunks if total_chunks else 0.0
        name_score = folder_name_score(file_name, folder_name)
        type_score = file_type_affinity_score(file_type, folder_path)
        name_type_combo = 0.5 * name_score + 0.5 * type_score

        score = (
            alpha * mean_sim +
            beta * max_sim +
            gamma * norm_count +
            delta * name_type_combo
        )
        final_scores[folder_path] = round(score, 6)
        scoring_details[folder_path] = {
            "mean_similarity": round(mean_sim, 4),
            "max_similarity": round(max_sim, 4),
            "normalized_match_count": round(norm_count, 4),
            "name_match_score": name_score,
            "type_affinity_score": round(type_score, 4),
            "final_score": round(score, 6)
        }

    # --- Select best folder ---
    best_folder_path, best_score = max(final_scores.items(), key=lambda x: x[1])
    threshold = 0.7  # Could be made configurable later
    if best_score < threshold:
        logger.info(f"[Sorter] Best score {best_score} is below threshold. Using fallback.")
        return _build_output(file_data, str(get_unsorted_folder()), scoring_details, list(final_scores), embeddings, used_fallback=True)

    logger.info(f"[Sorter] Best folder: {Path(best_folder_path).name} | Score: {best_score}")
    return _build_output(file_data, best_folder_path, scoring_details, list(final_scores), embeddings, used_fallback=False)


# --- Format output for actor ---
def _build_output(
    file_data: Dict,
    final_folder: str,
    scoring: Dict[str, Dict],
    candidates: List[str],
    embeddings: List,
    used_fallback: bool = False
) -> Dict:
    return {
        "file_path": file_data["file_path"],
        "file_name": file_data["file_name"],
        "file_type": file_data["file_type"],
        "content_hash": file_data["content_hash"],
        "final_folder": final_folder,
        "scoring_breakdown": scoring,
        "similar_folders": candidates,
        "embeddings": embeddings,
        "used_fallback": used_fallback
    }


# --- Public Entry ---
def handle_new_file(file_data: Dict) -> Dict:
    return sort_file(file_data)


# --- CLI Test ---
if __name__ == "__main__":
    dummy = {
        "file_path": "/test/path/file.pdf",
        "file_name": "file",
        "file_type": "pdf",
        "content_hash": "abcd1234",
        "parent_folder": "misc",
        "embeddings": [[0.1] * 384]
    }
    print(json.dumps(handle_new_file(dummy), indent=2))
