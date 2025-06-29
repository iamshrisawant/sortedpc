from pathlib import Path
import shutil

def move_file(src: Path, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / src.name
    return shutil.move(str(src), str(resolve_conflict(dest_path)))

def rename_file(src: Path, new_name: str) -> Path:
    new_path = src.with_name(new_name)
    return src.rename(resolve_conflict(new_path))

def resolve_conflict(path: Path) -> Path:
    counter = 1
    new_path = path
    while new_path.exists():
        new_path = path.with_stem(f"{path.stem}_{counter}")
        counter += 1
    return new_path
