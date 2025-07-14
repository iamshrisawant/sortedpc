import json
import logging
from collections import defaultdict
from pathlib import Path

from src.core.utils.paths import get_logs_path, get_config_file

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")


# --- Load corrections from logs.jsonl ---
def load_corrections() -> list:
    log_path = get_logs_path()
    if not log_path.exists():
        raise FileNotFoundError("[Reinforcer] logs.jsonl not found.")

    corrections = []
    with log_path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
                if entry.get("category") == "correction":
                    corrections.append(entry)
            except json.JSONDecodeError:
                continue
    return corrections


# --- Load scoring weights from config.json ---
def load_weights() -> dict:
    config_path = get_config_file()
    if not config_path.exists():
        return {"alpha": 0.6, "beta": 0.3, "gamma": 0.05, "delta": 0.05}

    with config_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    return {
        "alpha": float(data.get("alpha", 0.6)),
        "beta": float(data.get("beta", 0.3)),
        "gamma": float(data.get("gamma", 0.05)),
        "delta": float(data.get("delta", 0.05)),
    }


# --- Save updated weights to config.json ---
def save_weights(weights: dict):
    config_path = get_config_file()

    # Load existing config if it exists
    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as f:
            config = json.load(f)
    else:
        config = {}

    config.update(weights)

    with config_path.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    logger.info(f"[Reinforcer] Updated weights saved to {config_path.name}")


# --- Normalize weights to sum to 1 ---
def normalize_weights(w: dict) -> dict:
    total = sum(w.values())
    return {k: round(v / total, 6) for k, v in w.items()}


# --- Compute adjustments from corrections ---
def compute_adjustments(corrections: list, current_weights: dict) -> dict:
    over_weight = defaultdict(float)
    under_weight = defaultdict(float)

    for entry in corrections:
        scoring = entry.get("scoring_breakdown", {})
        if not scoring:
            continue

        corrected = Path(entry["final_folder"]).name
        original = None
        for folder in scoring:
            if folder != corrected:
                original = folder
                break

        if not original or original == corrected:
            continue

        orig_score = scoring.get(original, 0.0)
        corr_score = scoring.get(corrected, 0.0)

        if corr_score > orig_score:
            diff = corr_score - orig_score
            under_weight["alpha"] += diff * 0.6
            under_weight["beta"] += diff * 0.3
            under_weight["gamma"] += diff * 0.05
            under_weight["delta"] += diff * 0.05
        else:
            diff = orig_score - corr_score
            over_weight["alpha"] += diff * 0.6
            over_weight["beta"] += diff * 0.3
            over_weight["gamma"] += diff * 0.05
            over_weight["delta"] += diff * 0.05

    # Apply learning rate
    learning_rate = 0.05
    new_weights = current_weights.copy()

    for k in new_weights:
        delta = learning_rate * (under_weight[k] - over_weight[k])
        new_weights[k] += delta

    for k in new_weights:
        new_weights[k] = max(0.01, min(1.0, new_weights[k]))

    return normalize_weights(new_weights)


# --- Weight change summary ---
def print_weight_diff(before: dict, after: dict):
    logger.info("[Reinforcer] Weight update summary:")
    for k in before:
        delta = round(after[k] - before[k], 6)
        logger.info(f"  {k}: {before[k]} → {after[k]}  ({'+' if delta >= 0 else ''}{delta})")


# --- Reinforcement entrypoint ---
def reinforce():
    corrections = load_corrections()
    if not corrections:
        logger.info("[Reinforcer] No corrections to learn from.")
        return

    current_weights = load_weights()
    updated_weights = compute_adjustments(corrections, current_weights)

    print_weight_diff(current_weights, updated_weights)
    save_weights(updated_weights)


# --- Programmatic Entry ---
def run_reinforcer():
    reinforce()


# --- CLI ---
if __name__ == "__main__":
    run_reinforcer()
