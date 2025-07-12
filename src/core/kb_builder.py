from pathlib import Path
from typing import List, Tuple, Dict
import hashlib
import json

from loguru import logger

from utils.extractor import find_documents
from utils.chunker import chunk_text
from utils.embedder import embed_texts
from utils.indexer import Indexer
from utils.path_utils import resolve_relative_to_kb_roots
from utils.config import load_state_json, STATE_PATH, _normalize_paths
import kb_state

# ─────────────────────────────────────────────
# Constants

INDEX_FILE = Path("src/core/data/index.faiss")
META_FILE = Path("src/core/data/meta.json")


# ─────────────────────────────────────────────
# Helpers

def compute_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def add_kb_path_to_state(folder: Path):
    state = load_state_json()
    kb_paths = state.get("kb_paths", [])

    folder = folder.expanduser().resolve(strict=False)
    existing = _normalize_paths(kb_paths)

    if folder not in existing:
        kb_paths.append(str(folder))
        state["kb_paths"] = list({str(p) for p in _normalize_paths(kb_paths)})

        with STATE_PATH.open("w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

        logger.info(f"[KB] Registered KB path: {folder}")
    else:
        logger.debug(f"[KB] KB path already registered: {folder}")


# ─────────────────────────────────────────────
# Core logic

def process_folder(folder: Path) -> Tuple[List[List[float]], List[Dict]]:
    logger.info(f"[KB] Processing folder: {folder}")
    files_with_text = find_documents(folder)

    if not files_with_text:
        logger.warning(f"[KB] No valid documents found in {folder}")
        return [], []

    all_embeddings, all_metadata = [], []
    seen_hashes = set()

    for file_path, content in files_with_text:
        doc_hash = compute_sha256(content)
        if doc_hash in seen_hashes:
            logger.debug(f"[KB] Skipping duplicate: {file_path.name}")
            continue

        seen_hashes.add(doc_hash)
        chunks = chunk_text(content)
        embeddings = embed_texts(chunks)

        if not embeddings:
            logger.warning(f"[KB] Skipping: {file_path.name} — no embeddings.")
            continue

        avg_embedding = [sum(x) / len(x) for x in zip(*embeddings)]
        rel_folder = resolve_relative_to_kb_roots(file_path.parent)

        all_embeddings.append(avg_embedding)
        all_metadata.append({
            "folder": rel_folder,
            "filename": file_path.name,
            "preview": content[:300],
            "hash": doc_hash
        })

        logger.info(f"[KB] Indexed: {file_path.name} ({len(chunks)} chunks)")

    logger.info(f"[KB] Completed {len(all_embeddings)} documents from {folder}")
    return all_embeddings, all_metadata


def build_kb(folder: Path, rebuild: bool = False):
    folder = folder.expanduser().resolve(strict=False)

    if not folder.exists() or not folder.is_dir():
        logger.error(f"[KB] Invalid folder path: {folder}")
        return

    if not rebuild and kb_state.is_processed(folder):
        logger.info(f"[KB] Already processed: {folder}")
        return

    # Register KB path in state.json
    add_kb_path_to_state(folder)

    embeddings, metadata = process_folder(folder)
    if not embeddings:
        logger.warning(f"[KB] No embeddings extracted from: {folder}")
        return

    indexer = Indexer(dim=len(embeddings[0]))

    if not rebuild and INDEX_FILE.exists() and META_FILE.exists():
        indexer.load(str(INDEX_FILE), str(META_FILE))

    indexer.add(embeddings, metadata)
    indexer.save(str(INDEX_FILE), str(META_FILE))
    kb_state.mark_processed(folder)

    logger.success(f"[KB] Indexed {len(embeddings)} documents from '{folder}'.")


def build_kb_batch(folders: List[Path], rebuild: bool = False):
    for folder in folders:
        build_kb(folder, rebuild=rebuild)


# ─────────────────────────────────────────────
# CLI Entry Point

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Build semantic knowledge base from folder(s)")
    parser.add_argument("folder", type=str, nargs="+", help="Path(s) to folder(s) to index")
    parser.add_argument("--rebuild", action="store_true", help="Rebuild instead of incrementally updating")

    args = parser.parse_args()
    folders = [Path(p) for p in args.folder]

    for folder_path in folders:
        if not folder_path.exists() or not folder_path.is_dir():
            logger.error(f"[CLI] Invalid folder: {folder_path}")
        else:
            build_kb(folder_path, rebuild=args.rebuild)
