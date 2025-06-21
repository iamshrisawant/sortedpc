# feature_builder.py

from data.extractor import extract_metadata
from data.tokenizer import extract_text, tokenize
import re

SPARSE_TOKEN_THRESHOLD = 5

def build_features(file_path):
    print(f"\n[PROCESSING] {file_path}")
    metadata = extract_metadata(file_path)

    content, source = extract_text(file_path)
    tokens = tokenize(content)

    metadata["tokens"] = tokens
    metadata["source"] = source
    metadata["augmented"] = False

    if len(tokens) < SPARSE_TOKEN_THRESHOLD:
        metadata["tokens"] += generate_augmented_tokens(metadata)
        metadata["augmented"] = True

    return metadata

def generate_augmented_tokens(meta):
    """
    Augments with:
    - filename tokens (e.g., resume, report)
    - file type (e.g., type_pdf)
    """
    name = meta['name'].lower()
    # Split name into components using non-word characters
    name_tokens = re.findall(r'\b[a-z]+\b', name)

    # File extension type token
    type_token = f"type_{meta['type'].lstrip('.')}"

    return name_tokens + [type_token]
