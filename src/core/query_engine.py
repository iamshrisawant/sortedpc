from typing import List, Dict, Tuple
from pathlib import Path

from utils.embedder import embed_texts
from utils.retriever import Retriever
from utils.extractor import extract_text
from llm_interface import answer_query, answer_query_on_selected_files

INDEX_PATH = "kb_data/index.faiss"
META_PATH = "kb_data/meta.json"
ORGANIZED_ROOT = Path("organized_folders")

def resolve_query(query: str, top_k: int = 5) -> Tuple[str, List[str]]:
    """
    Resolves a user query by retrieving relevant documents and generating a response.

    Returns:
        (answer, list of source file paths used)
    """
    query_embedding = embed_texts([query])[0]

    retriever = Retriever(INDEX_PATH, META_PATH)
    top_matches = retriever.search(query_embedding, k=top_k)

    retrieved_docs = []
    for (folder, filename), _ in top_matches:
        file_path = ORGANIZED_ROOT / folder / filename
        if file_path.exists():
            text = extract_text(file_path)
            retrieved_docs.append((str(file_path), text))

    if not retrieved_docs:
        return "No relevant information found.", []

    answer, sources = answer_query(query, retrieved_docs)
    return answer, sources

def resolve_query_on_selected_files(query: str, selected_file_paths: List[str]) -> Tuple[str, List[str]]:
    """
    Resolves a query using only the content from explicitly selected files.
    """
    file_texts: Dict[str, str] = {}

    for file_path in selected_file_paths:
        path = Path(file_path)
        if path.exists():
            content = extract_text(path)
            if content.strip():
                file_texts[str(path)] = content

    if not file_texts:
        return "No valid documents provided for answering.", []

    answer, sources = answer_query_on_selected_files(query, file_texts)
    return answer, sources
