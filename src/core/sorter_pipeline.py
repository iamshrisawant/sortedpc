from pathlib import Path
from typing import List, Dict
from collections import defaultdict
import numpy as np
import math

from utils.extractor import extract_text
from utils.chunker import chunk_text
from utils.embedder import embed_texts
from utils.retriever import Retriever
from utils.indexer import Indexer
from utils.file_ops import move_file
from utils.logger import log_move
from utils.path_utils import resolve_relative_to_kb_roots
from utils.config import load_kb_paths

from loguru import logger

# ─────────────────────────────────────────────
INDEX_PATH = "src/core/data/index.faiss"
META_PATH = "src/core/data/meta.json"
TEMP_UNSORTED_FOLDER_NAME = "temp_unsorted"
CONFIDENCE_THRESHOLD = 0.65
FILE_MATCH_THRESHOLD = 0.08
STRONG_MATCH_DISTANCE = 0.25
TOP_K = 25

# ─────────────────────────────────────────────
# Utility functions

def mean_pool(embeddings: List[List[float]]) -> List[float]:
    return np.mean(np.array(embeddings, dtype=np.float32), axis=0).tolist()

def soft_score(distance: float, tau: float = 0.6) -> float:
    return math.exp(- (distance ** 2) / (2 * tau ** 2))

def find_existing_folder(target_rel_path: str, kb_roots: List[Path]) -> Path:
    for root in kb_roots:
        candidate = (root / target_rel_path).resolve()
        if candidate.exists() and candidate.is_dir():
            return candidate
    return None

# ─────────────────────────────────────────────
# Indexing logic

def index_file_to_kb(file_path: Path, chunks: List[str], embeddings: List[List[float]]):
    if not embeddings or not chunks:
        logger.warning(f"[Indexing] Skipping: {file_path.name}")
        return

    rel_folder = resolve_relative_to_kb_roots(file_path.parent)
    metadata = [
        {
            "folder": rel_folder,
            "filename": file_path.name,
            "chunk_index": i,
            "chunk_text": chunk
        }
        for i, chunk in enumerate(chunks)
    ]

    indexer = Indexer(dim=len(embeddings[0]))
    indexer.load(INDEX_PATH, META_PATH)
    indexer.add(embeddings, metadata)
    indexer.save(INDEX_PATH, META_PATH)
    logger.info(f"[Indexing] {file_path.name} → {len(embeddings)} chunks")

# ─────────────────────────────────────────────
# Main sorting logic

def sort_file(file_path: Path) -> Dict:
    try:
        file_path = file_path.resolve()
        logger.info(f"[Sorter] Processing: {file_path.name}")

        content = extract_text(file_path)
        if not content.strip():
            raise ValueError("Empty or unreadable content.")

        chunks = chunk_text(content)
        embeddings = embed_texts(chunks)
        if not embeddings:
            raise ValueError("No valid embeddings.")

        query_embedding = mean_pool(embeddings)
        retriever = Retriever(INDEX_PATH, META_PATH)
        top_docs = retriever.search(query_embedding, k=TOP_K)

        logger.debug("[Sorter] Top results:")
        for meta, dist in top_docs:
            logger.debug(f"↪ Folder: {meta.get('folder')}, File: {meta.get('filename')}, Distance: {dist:.4f}")

        top_match_meta, top_match_dist = top_docs[0]
        top_folder = top_match_meta.get("folder")

        # ─────────────────────────────────────────────
        # STRONG file-level override
        if top_folder and top_folder != TEMP_UNSORTED_FOLDER_NAME and top_match_dist < STRONG_MATCH_DISTANCE:
            target_rel_folder = top_folder
            confidence = 1.0
            logger.info(f"[Sorter] Direct override: Strong top file match → {top_match_meta['filename']} ({top_match_dist:.4f})")
        else:
            # Aggregated folder-level classification
            folder_scores = defaultdict(float)
            for meta, dist in top_docs:
                folder = meta.get("folder")
                if folder and folder != TEMP_UNSORTED_FOLDER_NAME:
                    folder_scores[folder] += soft_score(dist)

            if not folder_scores:
                target_rel_folder = TEMP_UNSORTED_FOLDER_NAME
                confidence = 0.0
            else:
                sorted_scores = sorted(folder_scores.items(), key=lambda x: x[1], reverse=True)
                target_rel_folder, top_score = sorted_scores[0]

                gap = top_score - (sorted_scores[1][1] if len(sorted_scores) > 1 else 0)
                agreement_ratio = sum(
                    1 for meta, _ in top_docs
                    if meta.get("folder") == target_rel_folder
                ) / len(top_docs)
                top_similarity = soft_score(top_match_dist)

                confidence = round(min(
                    0.5 * agreement_ratio + 0.3 * top_similarity + 0.2 * gap,
                    1.0
                ), 4)

            logger.debug(f"[Sorter] Folder Scores: {dict(folder_scores)}")
            logger.debug(f"[Sorter] Best folder: {target_rel_folder}")
            logger.debug(f"[Sorter] Confidence score: {confidence:.4f}")

        # ─────────────────────────────────────────────
        # Resolve real folder path from KB roots
        kb_roots = load_kb_paths()
        target_folder = find_existing_folder(target_rel_folder, kb_roots)

        if target_folder and confidence >= CONFIDENCE_THRESHOLD:
            logger.info(f"[Sorter] Selected folder: {target_folder} (Confident)")
        else:
            target_folder = (kb_roots[0] / TEMP_UNSORTED_FOLDER_NAME).resolve()
            target_folder.mkdir(parents=True, exist_ok=True)
            logger.warning(f"[Sorter] Fallback to unsorted: {target_folder} (Low confidence or missing folder)")

        # ─────────────────────────────────────────────
        similar_folders = {
            meta.get("folder")
            for meta, _ in top_docs
            if meta.get("folder") and meta.get("folder") != TEMP_UNSORTED_FOLDER_NAME
        }

        final_path = move_file(file_path, target_folder, similar_dirs=list(similar_folders))
        log_move(file_path.name, target_folder, list(similar_folders))

        logger.info(f"[Sorter] Similar folders used for decision: {list(similar_folders)}")

        # Re-index the moved file
        re_content = extract_text(final_path)
        re_chunks = chunk_text(re_content)
        re_embeddings = embed_texts(re_chunks)
        index_file_to_kb(final_path, re_chunks, re_embeddings)

        logger.success(f"[Sorter] Moved → {target_folder}")
        return {
            "file": str(file_path),
            "moved_to": str(final_path),
            "confidence": confidence,
            "confident": confidence >= CONFIDENCE_THRESHOLD,
            "suggested_folders": list(similar_folders)
        }

    except Exception as e:
        logger.error(f"[Sorter] Failed on {file_path.name}: {e}")
        return {
            "file": str(file_path),
            "error": str(e)
        }
