from data.extractor import extract_metadata
from data.tokenizer import extract_text, tokenize

def build_features(file_path):
    print(f"\n[PROCESSING] {file_path}")
    metadata = extract_metadata(file_path)
    content = extract_text(file_path)
    tokens = tokenize(content)
    metadata["tokens"] = tokens
    return metadata
