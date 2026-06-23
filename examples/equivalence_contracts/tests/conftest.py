from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / "examples" / "equivalence_contracts"


def _add(path: Path) -> None:
    text = str(path)
    if text not in sys.path:
        sys.path.insert(0, text)


_add(PROJECT / "src")

for base in (ROOT / "pkgs" / "core", ROOT / "pkgs" / "engines", ROOT / "pkgs" / "apps"):
    if not base.is_dir():
        continue
    for child in sorted(base.iterdir()):
        if not child.is_dir():
            continue
        _add(child)
        src = child / "src"
        if src.is_dir():
            _add(src)
