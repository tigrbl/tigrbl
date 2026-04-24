from __future__ import annotations

from pathlib import Path
from common import repo_root, fail

ROOT = repo_root()

MAX_FILE_NAME_LENGTH = 64
MAX_DIRECTORY_NAME_LENGTH = 48
MAX_RELATIVE_PATH_LENGTH = 160

EXCLUDED_ROOTS = {
    ROOT / '.git',
    ROOT / '.ssot',
    ROOT / '.venv',
    ROOT / '.tmp',
    ROOT / '.uv-cache',
    ROOT / '.pip-cache',
    ROOT / '.benchmarks',
    ROOT / 'target',
}

EXCLUDED_NAMES = {
    '__pycache__',
    '.pytest_cache',
    '.ruff_cache',
    '.mypy_cache',
}

EXCLUDED_SUFFIXES = {
    '.pyc',
}


def is_excluded(path: Path) -> bool:
    if any(path == ex or ex in path.parents for ex in EXCLUDED_ROOTS):
        return True
    if any(part in EXCLUDED_NAMES for part in path.parts):
        return True
    return path.suffix in EXCLUDED_SUFFIXES


def main() -> None:
    errors: list[str] = []
    longest_path: tuple[int, str] = (0, '')
    longest_file: tuple[int, str] = (0, '')
    longest_dir: tuple[int, str] = (0, '')

    for path in ROOT.rglob('*'):
        if is_excluded(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        rel_len = len(rel)
        if rel_len > longest_path[0]:
            longest_path = (rel_len, rel)
        if rel_len > MAX_RELATIVE_PATH_LENGTH:
            errors.append(
                f"path too long ({rel_len}>{MAX_RELATIVE_PATH_LENGTH}): {rel}"
            )
        name_len = len(path.name)
        if path.is_file():
            if name_len > longest_file[0]:
                longest_file = (name_len, rel)
            if name_len > MAX_FILE_NAME_LENGTH:
                errors.append(
                    f"file name too long ({name_len}>{MAX_FILE_NAME_LENGTH}): {rel}"
                )
        elif path.is_dir():
            if name_len > longest_dir[0]:
                longest_dir = (name_len, rel)
            if name_len > MAX_DIRECTORY_NAME_LENGTH:
                errors.append(
                    f"directory name too long ({name_len}>{MAX_DIRECTORY_NAME_LENGTH}): {rel}"
                )

    fail(errors)
    print(
        'path length validation passed '
        f"(max path={longest_path[0]}, max file={longest_file[0]}, max dir={longest_dir[0]})"
    )


if __name__ == '__main__':
    main()
