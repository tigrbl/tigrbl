from __future__ import annotations

import hashlib
import json
from pathlib import Path
from common import repo_root

ROOT = repo_root()
MARKER_PATH = ROOT / "docs" / "conformance" / "gates" / "TARGET_FREEZE_CURRENT_CYCLE.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    marker = json.loads(MARKER_PATH.read_text())
    files = {
        rel: sha256_file(ROOT / rel)
        for rel in marker["controlled_docs"]
    }
    manifest = {
        "cycle_id": marker["cycle_id"],
        "generated_for_marker": str(MARKER_PATH.relative_to(ROOT)),
        "files": files,
    }
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
