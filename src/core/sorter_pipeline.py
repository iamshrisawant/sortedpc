from pathlib import Path
from typing import List, Tuple

from utils.extractor import extract_text
from utils.embedder import chunk_text, embed_texts
from utils.retriever import Retriever
from llm_interface import classify_document
from utils.file_ops import move_file
from utils.logger import log_move

INDEX_PATH = "kb_data/index.faiss"
META_PATH = "kb_data/meta.json"
ORGANIZED_ROOT = Path("organized_folders")  # Base of all known folders

def get_all_folder_labels() -> List[str]:
    return [f.name for f in ORGANIZED_ROOT.iterdir() if f.is_dir()]

def sort_file(file_path: Path):
    try:
        file_path = Path(file_path).resolve()
        print(f"[Sorter] Processing: {file_path.name}")

        # Step 1: Extract content
        content = extract_text(file_path)
        if not content.strip():
            raise ValueError("Empty or unreadable content.")

        # Step 2: Embed and retrieve similar docs
        chunks = chunk_text(content)
        embeddings = embed_texts(chunks)
        if not embeddings:
            raise ValueError("Failed to generate embeddings.")

        retriever = Retriever(INDEX_PATH, META_PATH)
        top_docs: List[Tuple[str, float]] = retriever.search(embeddings[0], k=5)

        # Step 3: Build doc list for LLM
        retrieved = []
        for (folder, file), _ in top_docs:
            path = Path(ORGANIZED_ROOT) / Path(folder) / file
            if path.exists():
                doc_text = extract_text(path)
                retrieved.append((str(path), doc_text))

        # Step 4: LLM classification
        folder_labels = get_all_folder_labels()
        selected_folder_name, referenced_files = classify_document(content, folder_labels, retrieved)

        # Step 5: Move file and log
        selected_folder = ORGANIZED_ROOT / selected_folder_name
        similar_folder_suggestions = list({folder for (folder, _) in top_docs})

        final_path = move_file(file_path, selected_folder, similar_dirs=similar_folder_suggestions)
        log_move(file_path.name, selected_folder, similar_folder_suggestions)

        print(f"[Sorter] Moved to: {selected_folder}")
        return {
            "file": str(file_path),
            "moved_to": str(final_path),
            "referenced_files": referenced_files,
            "suggested_folders": similar_folder_suggestions
        }

    except Exception as e:
        print(f"[Sorter] Error while sorting {file_path.name}: {e}")
        return {
            "file": str(file_path),
            "error": str(e)
        }
