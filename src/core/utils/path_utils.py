from pathlib import Path
from utils.config import load_kb_paths


def resolve_relative_to_kb_roots(path: Path) -> str:
    path = Path(path).expanduser().resolve(strict=False)  # ensure path is a Path

    for root in load_kb_paths():
        try:
            root = root.expanduser().resolve(strict=False)
            rel_path = path.relative_to(root)
            return rel_path.as_posix()
        except ValueError:
            continue

    return path.stem if path.is_file() else path.name
