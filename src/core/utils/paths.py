import json
from pathlib import Path
from typing import List, Union, Dict

# --- Base paths ---
ROOT_DIR = Path(__file__).resolve().parents[3]  # from src/core/utils -> ROOT
DATA_DIR = ROOT_DIR / "src/data"
FAISS_DIR = DATA_DIR / "faiss"

# --- Data files ---
PATHS_FILE = DATA_DIR / "paths.json"
CONFIG_FILE = DATA_DIR / "config.json"
LOGS_FILE = DATA_DIR / "logs.jsonl"

# --- FAISS files ---
FAISS_INDEX_FILE = FAISS_DIR / "index.faiss"
FAISS_METADATA_FILE = FAISS_DIR / "index_meta.jsonl"


# --- Path normalization ---
def normalize_path(p: Union[str, Path]) -> str:
    return str(Path(p).expanduser().resolve())


# --- File path accessors ---
def get_paths_file() -> Path:
    return PATHS_FILE

def get_config_file() -> Path:
    return CONFIG_FILE

def get_logs_path() -> Path:
    return LOGS_FILE

def get_faiss_dir() -> Path:
    return FAISS_DIR

def get_faiss_index_path() -> Path:
    return FAISS_INDEX_FILE

def get_faiss_metadata_path() -> Path:
    return FAISS_METADATA_FILE

def get_unsorted_folder() -> Path:
    return Path.home() / "Documents" / "sortedpc" / "unsorted"


# --- Paths.json accessors ---
def get_watch_paths() -> List[str]:
    return _load_list_from_json(PATHS_FILE, "watch_paths")

def get_organized_paths() -> List[str]:
    return _load_list_from_json(PATHS_FILE, "organized_paths")


# --- Config.json accessors ---
def get_builder_state() -> bool:
    return _load_config_flag("builder_busy")

def get_faiss_state() -> bool:
    return _load_config_flag("faiss_built")

def get_watcher_state() -> bool:
    return _load_config_flag("watcher_online")

def get_scoring_weights() -> Dict[str, float]:
    return _load_dict_from_json(CONFIG_FILE, keys=["alpha", "beta", "gamma", "delta"])


# --- Log access helpers ---
def load_all_logs() -> List[Dict]:
    if not LOGS_FILE.exists():
        return []
    with LOGS_FILE.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def get_move_logs() -> Dict[str, Dict]:
    logs = load_all_logs()
    return {
        log["file_path"]: log for log in logs if log.get("category", "moves") == "moves"
    }

def get_correction_logs() -> Dict[str, Dict]:
    logs = load_all_logs()
    return {
        log["file_path"]: log for log in logs if log.get("category") == "corrections"
    }


# --- Internal shared loaders ---
def _load_list_from_json(path: Path, key: str) -> List[str]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return [normalize_path(p) for p in data.get(key, [])]

def _load_dict_from_json(path: Path, keys: List[str]) -> Dict[str, float]:
    if not path.exists():
        return {k: 0.0 for k in keys}
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return {k: float(data.get(k, 0.0)) for k in keys}

def _load_config_flag(key: str) -> bool:
    if not CONFIG_FILE.exists():
        return False
    with CONFIG_FILE.open("r", encoding="utf-8") as f:
        config = json.load(f)
    return bool(config.get(key, False))
