from __future__ import annotations

from pathlib import Path
import re
from common import repo_root, fail

ROOT = repo_root()
CLAIM_REGISTRY = ROOT / "docs" / "conformance" / "CLAIM_REGISTRY.md"
RELEASE_NOTE_BASES = [
    ROOT / "docs" / "release-notes",
    ROOT / "docs" / "conformance" / "releases",
]
CLAIM_LINE_RE = re.compile(r"^(?:Supported claim ids|Claim IDs):\s*(.+)$", flags=re.IGNORECASE | re.MULTILINE)
TIER3_RE = re.compile(r"\b(certified|certifiably|conformant|fully[- ]featured|fully compliant)\b", flags=re.IGNORECASE)
UNSUPPORTED_STATUSES = {
    "not achieved",
    "missing",
    "partial",
    "deferred",
    "oob",
    "de-scoped",
    "de-scoped by RFC/security boundary review",
    "de-scoped by docs/operator closure",
}


def parse_claim_registry() -> dict[str, tuple[str, str]]:
    claims: dict[str, tuple[str, str]] = {}
    for line in CLAIM_REGISTRY.read_text().splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 5 or cells[0] in {"Claim ID", "---"}:
            continue
        claim_id, _, status, tier = cells[:4]
        claims[claim_id] = (status.lower(), tier)
    return claims


def iter_release_note_files() -> list[Path]:
    files: list[Path] = []
    for base in RELEASE_NOTE_BASES:
        if not base.exists():
            continue
        files.extend(p for p in base.rglob("*.md") if p.name.lower() != "readme.md")
    return sorted(files)


def normalize_ids(raw: str) -> list[str]:
    cleaned = raw.strip()
    if cleaned.lower() in {"none", "n/a"}:
        return []
    return [part.strip() for part in cleaned.split(",") if part.strip()]


def main() -> None:
    errors: list[str] = []
    claims = parse_claim_registry()

    for file in iter_release_note_files():
        rel = file.relative_to(ROOT)
        text = file.read_text()
        claim_lines = [normalize_ids(match.group(1)) for match in CLAIM_LINE_RE.finditer(text)]
        claim_ids = [claim_id for line in claim_lines for claim_id in line]

        if not claim_lines:
            errors.append(
                f"{rel} is a release-note file but does not declare Supported claim ids: <CLAIM_ID,...>"
            )
            continue

        for claim_id in claim_ids:
            if claim_id not in claims:
                errors.append(f"{rel} references unknown claim id {claim_id}")
                continue
            status, _tier = claims[claim_id]
            if status in UNSUPPORTED_STATUSES:
                errors.append(
                    f"{rel} references unsupported claim id {claim_id} with status {status}"
                )

        if TIER3_RE.search(text):
            for claim_id in claim_ids:
                if claim_id not in claims:
                    continue
                _status, tier = claims[claim_id]
                if not tier.lower().startswith("tier 3") and not tier.lower().startswith("tier 4"):
                    errors.append(
                        f"{rel} uses Tier 3+ wording while referencing non-Tier-3 claim {claim_id} ({tier})"
                    )

    fail(errors)
    print("release note claim lint passed")


if __name__ == "__main__":
    main()
