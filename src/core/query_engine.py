# src/core/query_engine.py

from typing import List, Dict, Tuple
from pathlib import Path
from loguru import logger

from core.utils.embedder import embed_texts
from core.utils.retriever import Retriever
from core.utils.extractor import extract_text
from core.llm_interface import answer_query, answer_query_on_selected_files

# Constants
INDEX_PATH = "src/core/data/index.faiss"
META_PATH = "src/core/data/meta.json"


def resolve_query(query: str, top_k: int = 5) -> Tuple[str, List[str]]:
    """
    Handles a user query using full RAG flow:
    - Embeds query
    - Retrieves top-k chunks from FAISS
    - Extracts full file content
    - Sends prompt to LLM with context

    Returns:
        Tuple of (answer text, list of file paths used)
    """
    cleaned = query.strip()
    if not cleaned or len(cleaned) < 3:
        return "Query too short. Please enter at least a few words.", []

    embeddings = embed_texts([cleaned])
    if not embeddings:
        return "Query could not be embedded. Please rephrase or retry.", []

    query_embedding = embeddings[0]
    try:
        retriever = Retriever(INDEX_PATH, META_PATH)
        top_matches = retriever.search(query_embedding, k=top_k)
    except Exception as e:
        logger.error(f"[QueryEngine] Retrieval error: {e}")
        return "Unable to access the knowledge base. Please try again later.", []

    retrieved_docs = _gather_retrieved_documents(top_matches)

    if not retrieved_docs:
        logger.warning("[QueryEngine] No valid documents extracted. Falling back to context-less query.")
        return answer_query(query, [] if top_matches else [])

    return answer_query(query, retrieved_docs)


def resolve_query_on_selected_files(query: str, selected_file_paths: List[str]) -> Tuple[str, List[str]]:
    """
    Handles a user query using only selected files (bypasses FAISS).
    """
    file_texts = _extract_texts_from_files(selected_file_paths)
    if not file_texts:
        logger.warning("[QueryEngine] No valid content found in selected files.")
        return "No valid content found in selected files.", []

    return answer_query_on_selected_files(query, file_texts)


# ─────────────────────────────────────────────
# Internal Helpers
# ─────────────────────────────────────────────

def _gather_retrieved_documents(top_matches: List[Tuple[Dict, float]]) -> List[Tuple[str, str]]:
    """
    Converts FAISS metadata into [(file_path, extracted_text)] tuples.
    Handles both absolute and relative folder paths.
    """
    results = []

    for meta, _ in top_matches:
        folder = meta.get("folder")
        filename = meta.get("filename")

        if not folder or not filename:
            continue

        folder_path = Path(folder)
        file_path = folder_path / filename

        if not file_path.exists():
            logger.warning(f"[QueryEngine] File not found: {file_path}")
            continue

        content = extract_text(file_path)
        if content and content.strip():
            results.append((str(file_path), content))

    return results


def _extract_texts_from_files(file_paths: List[str]) -> Dict[str, str]:
    """
    Extracts full content from user-selected files (for direct-query mode).
    Returns:
        Dict mapping absolute file paths to extracted text
    """
    result = {}

    for file_path in file_paths:
        path = Path(file_path)
        if path.exists():
            content = extract_text(path)
            if content and content.strip():
                result[str(path)] = content

    return result
