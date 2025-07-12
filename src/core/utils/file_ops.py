from pathlib import Path
import shutil
from datetime import datetime

from utils.logger import log_move
from utils.path_utils import resolve_relative_to_kb_roots


def move_file(
    src: Path,
    dest_dir: Path,
    similar_dirs: list[str] = [],
    manual_dir: Path = None
) -> Path:
    """
    Copies a file from `src` to `dest_dir` (or `manual_dir` if specified).
    Creates parent directories if missing. If file exists, only overwrites
    if `src` is newer than existing target.

    Logs move with KB-relative folder and similarity metadata.

    Returns the full path to the destination file.
    """
    src = Path(src).resolve(strict=True)
    target_dir = Path(manual_dir or dest_dir).expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    dest_path = target_dir / src.name
    replaced = False

    if dest_path.exists():
        if dest_path.stat().st_mtime < src.stat().st_mtime:
            shutil.copy2(src, dest_path)
            replaced = True
    else:
        shutil.copy2(src, dest_path)

    rel_folder = resolve_relative_to_kb_roots(target_dir)

    log_move(
        file_name=src.name,
        final_folder=rel_folder,
        similar_folders=similar_dirs,
        replaced=replaced
    )

    return dest_path
