import os

VALID_EXTENSIONS = {'.txt', '.pdf', '.docx', '.pptx'}
IGNORED_DIRS = {'node_modules', '__pycache__', '.git', 'venv'}

def get_valid_files(input_dir):
    valid_files = []
    for root, dirs, files in os.walk(input_dir):
        # Modify dirs in-place to skip ignored folders
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in VALID_EXTENSIONS:
                valid_files.append(os.path.join(root, file))
    print(f"[INFO] Found {len(valid_files)} valid files.")
    return valid_files


