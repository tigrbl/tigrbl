from __future__ import annotations

import hashlib
import json
from pathlib import Path
from common import repo_root, fail

ROOT = repo_root()
MARKER_PATH = ROOT / "docs" / "conformance" / "gates" / "TARGET_FREEZE_CURRENT_CYCLE.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    errors: list[str] = []
    if not MARKER_PATH.is_file():
        fail([f"missing boundary freeze marker {MARKER_PATH.relative_to(ROOT)}"])

    marker = json.loads(MARKER_PATH.read_text())
    manifest_rel = marker.get("manifest_path")
    if not manifest_rel:
        errors.append("boundary freeze marker missing manifest_path")
        fail(errors)
    manifest_path = ROOT / manifest_rel
    if not manifest_path.is_file():
        errors.append(f"boundary freeze manifest missing: {manifest_rel}")
        fail(errors)

    actual_manifest_sha = sha256_file(manifest_path)
    if marker.get("manifest_sha256") != actual_manifest_sha:
        errors.append(
            "boundary freeze marker manifest_sha256 does not match the current manifest content"
        )

    manifest = json.loads(manifest_path.read_text())
    marker_controlled = list(marker.get("controlled_docs", []))
    manifest_files = manifest.get("files", {})

    if sorted(marker_controlled) != sorted(manifest_files.keys()):
        errors.append(
            "controlled_docs in target freeze marker do not match the files recorded in the freeze manifest"
        )

    for rel, expected in manifest_files.items():
        file_path = ROOT / rel
        if not file_path.is_file():
            errors.append(f"freeze-controlled file missing: {rel}")
            continue
        actual = sha256_file(file_path)
        if actual != expected:
            errors.append(
                f"freeze manifest hash mismatch for {rel}; expected {expected}, got {actual}"
            )

    for rel in marker.get("boundary_docs", []):
        if rel not in marker_controlled:
            errors.append(f"boundary doc {rel} is not included in controlled_docs")

    claim_registry = marker.get("claim_registry_path")
    if claim_registry and claim_registry not in marker_controlled:
        errors.append("claim_registry_path must also appear in controlled_docs")

    fail(errors)
    print("boundary freeze manifest validation passed")


if __name__ == "__main__":
    main()
