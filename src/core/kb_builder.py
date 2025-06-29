import json
from pathlib import Path
from typing import List, Tuple

from utils.extractor import find_documents
from utils.embedder import chunk_text, embed_texts
from utils.indexer import Indexer

KB_STATE_FILE = Path("data/kb_state.json")
INDEX_FILE = Path("data/index.faiss")
META_FILE = Path("data/meta.json")

def load_kb_state() -> List[str]:
    if KB_STATE_FILE.exists():
        with open(KB_STATE_FILE, "r") as f:
            return json.load(f)
    return []

def save_kb_state(paths: List[str]):
    KB_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(KB_STATE_FILE, "w") as f:
        json.dump(paths, f, indent=2)

def build_kb(base_dir: Path, rebuild: bool = False):
    base_dir = base_dir.resolve()
    processed_paths = set(load_kb_state())

    new_dirs = []
    if rebuild:
        new_dirs = [p for p in base_dir.iterdir() if p.is_dir()]
        processed_paths.clear()
    else:
        new_dirs = [p for p in base_dir.iterdir() if p.is_dir() and str(p) not in processed_paths]

    if not new_dirs:
        print("No new folders to index.")
        return

    all_embeddings = []
    all_meta = []

    for folder in new_dirs:
        print(f"[KB] Processing folder: {folder.name}")
        files_with_text = find_documents(folder)
        for file_path, content in files_with_text:
            chunks = chunk_text(content)
            embeddings = embed_texts(chunks)
            folder_str = str(folder)
            all_embeddings.extend(embeddings)
            all_meta.extend([(folder_str, file_path.name)] * len(embeddings))

    if all_embeddings:
        indexer = Indexer(dim=len(all_embeddings[0]))

        if not rebuild and INDEX_FILE.exists():
            # Load existing and append
            indexer.load(str(INDEX_FILE), str(META_FILE))

        indexer.add(all_embeddings, all_meta)
        indexer.save(str(INDEX_FILE), str(META_FILE))

        updated_paths = list(processed_paths.union([str(p) for p in new_dirs]))
        save_kb_state(updated_paths)

        print(f"[KB] Indexed {len(all_embeddings)} new embeddings from {len(new_dirs)} folders.")
    else:
        print("[KB] No valid documents found for embedding.")
