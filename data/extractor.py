import os
from datetime import datetime

def extract_metadata(file_path):
    stat = os.stat(file_path)
    return {
        "name": os.path.basename(file_path),
        "path": file_path,
        "parent": os.path.dirname(file_path),
        "date": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "type": os.path.splitext(file_path)[1].lower()
    }
