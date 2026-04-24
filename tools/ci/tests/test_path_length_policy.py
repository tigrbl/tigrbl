from __future__ import annotations

import importlib.util
import sys
sys.dont_write_bytecode = True
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
CI_ROOT = REPO_ROOT / 'tools' / 'ci'
if str(CI_ROOT) not in sys.path:
    sys.path.insert(0, str(CI_ROOT))

MODULE_PATH = CI_ROOT / 'validate_path_lengths.py'
spec = importlib.util.spec_from_file_location('validate_path_lengths', MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

def _excluded(path: Path) -> bool:
    return module.is_excluded(path)


def test_repository_conforms_to_declared_path_limits() -> None:
    max_path = 0
    max_file = 0
    max_dir = 0

    for path in REPO_ROOT.rglob('*'):
        if _excluded(path):
            continue
        rel = path.relative_to(REPO_ROOT).as_posix()
        max_path = max(max_path, len(rel))
        assert len(rel) <= module.MAX_RELATIVE_PATH_LENGTH, rel
        if path.is_file():
            max_file = max(max_file, len(path.name))
            assert len(path.name) <= module.MAX_FILE_NAME_LENGTH, rel
        elif path.is_dir():
            max_dir = max(max_dir, len(path.name))
            assert len(path.name) <= module.MAX_DIRECTORY_NAME_LENGTH, rel

    assert max_path > 0
    assert max_file > 0
    assert max_dir > 0
