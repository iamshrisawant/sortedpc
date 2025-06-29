from pathlib import Path
import shutil
from datetime import datetime

from logger import log_move

def move_file(src: Path, dest_dir: Path, similar_dirs: list[str] = [], manual_dir: Path = None) -> Path:

    target_dir = manual_dir or dest_dir
    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    dest = target_dir / src.name

    if dest.exists():
        if dest.stat().st_mtime < src.stat().st_mtime:
            shutil.copy2(src, dest)  # Replace (preserve metadata)
            log_move(src.name, target_dir, similar_dirs, replaced=True)
        else:
            log_move(src.name, target_dir, similar_dirs, replaced=False)
    else:
        shutil.copy2(src, dest)
        log_move(src.name, target_dir, similar_dirs, replaced=False)

    return dest
