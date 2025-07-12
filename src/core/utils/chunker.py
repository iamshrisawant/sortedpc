from typing import List
from nltk.tokenize.punkt import PunktSentenceTokenizer
from loguru import logger
import nltk
import re

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

_tokenizer = PunktSentenceTokenizer()

def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

def chunk_text(
    text: str,
    max_chars: int = 500,
    min_chars_per_chunk: int = 100
) -> List[str]:
    sents = _tokenizer.tokenize(clean_text(text))
    chunks = []
    current = ""

    for sent in sents:
        sent = sent.strip()
        if not sent:
            continue

        if len(current) + len(sent) > max_chars:
            if len(current.strip()) >= min_chars_per_chunk:
                chunks.append(current.strip())
            current = sent
        else:
            current += " " + sent

    if len(current.strip()) >= min_chars_per_chunk:
        chunks.append(current.strip())

    logger.debug(f"[Chunker] Chunked into {len(chunks)} segment(s).")
    return chunks
