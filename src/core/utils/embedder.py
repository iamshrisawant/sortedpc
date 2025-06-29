from typing import List
from sentence_transformers import SentenceTransformer
from nltk.tokenize import sent_tokenize

model = SentenceTransformer("all-MiniLM-L6-v2")

def chunk_text(text: str, max_chars: int = 500) -> List[str]:
    sents = sent_tokenize(text)
    chunks, chunk = [], ""
    for sent in sents:
        if len(chunk) + len(sent) > max_chars:
            chunks.append(chunk.strip())
            chunk = sent
        else:
            chunk += " " + sent
    if chunk:
        chunks.append(chunk.strip())
    return chunks

def embed_texts(texts: List[str]) -> List[List[float]]:
    return model.encode(texts, convert_to_numpy=True).tolist()
