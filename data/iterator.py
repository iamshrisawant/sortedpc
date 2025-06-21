import os
from pathlib import Path

VALID_EXTENSIONS = {
    '.txt', '.pdf', '.docx', '.pptx', '.xlsx', '.csv', '.json'
}

IGNORED_DIRS = {
    'node_modules', '__pycache__', '.git', 'venv',
    '.vscode', '.idea', 'build', 'dist', '.cache'
}

def is_hidden(path):
    return any(part.startswith('.') for part in Path(path).parts)

def get_valid_files(input_dir):
    valid_files = []
    for root, dirs, files in os.walk(input_dir):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith('.')]
        for file in files:
            full_path = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            if ext in VALID_EXTENSIONS and not is_hidden(full_path):
                valid_files.append(full_path)
    print(f"[INFO] Found {len(valid_files)} valid files.")
    return valid_files
