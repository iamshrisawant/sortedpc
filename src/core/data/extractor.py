# data/extractor.py
import os
import datetime

def extract_metadata(file_path):
    stat_info = os.stat(file_path)
    metadata = {
        "name": os.path.basename(file_path),
        "directory": os.path.dirname(file_path),
        "type": os.path.splitext(file_path)[1].lstrip('.'),
        "size": stat_info.st_size,
        "created": datetime.datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
        "parent_folder": os.path.basename(os.path.dirname(file_path))
    }
    return metadata