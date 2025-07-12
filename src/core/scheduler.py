# src/core/scheduler.py

import threading
import time
import json
from datetime import datetime, timedelta
from pathlib import Path

from .kb_builder import build_kb
from loguru import logger

STATE_FILE = Path("src/core/data/state.json")
REBUILD_INTERVAL_DAYS = 7
CHECK_INTERVAL_SECONDS = 60 * 60 * 6  # Check every 6 hours


def _load_state():
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"[Scheduler] Failed to read state: {e}")
    return {}


def _save_state(state):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        logger.warning(f"[Scheduler] Failed to write state: {e}")


def _should_rebuild(last_rebuild: str) -> bool:
    try:
        last_time = datetime.fromisoformat(last_rebuild)
        return datetime.now() - last_time >= timedelta(days=REBUILD_INTERVAL_DAYS)
    except Exception:
        return True  # If malformed or missing


def _rebuild_kb_loop():
    logger.info("[Scheduler] Background KB rebuild scheduler started.")
    while True:
        state = _load_state()
        last_rebuild = state.get("last_kb_rebuild", "")
        kb_paths = state.get("kb_paths", [])

        if _should_rebuild(last_rebuild):
            logger.info("[Scheduler] Triggering weekly KB rebuild.")
            for folder in kb_paths:
                build_kb(Path(folder), rebuild=True)

            state["last_kb_rebuild"] = datetime.now().isoformat()
            _save_state(state)
            logger.info("[Scheduler] KB rebuild completed and state updated.")
        else:
            logger.info("[Scheduler] No rebuild needed. Skipping.")

        time.sleep(CHECK_INTERVAL_SECONDS)


def run_kb_scheduler():
    thread = threading.Thread(target=_rebuild_kb_loop, daemon=True)
    thread.start()
