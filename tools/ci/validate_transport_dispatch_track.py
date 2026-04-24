from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / ".ssot" / "registry.json"
NEXT_TARGETS = ROOT / "docs" / "conformance" / "NEXT_TARGETS.md"
CLAIM_REGISTRY = ROOT / "docs" / "conformance" / "CLAIM_REGISTRY.md"
EVIDENCE_REGISTRY = ROOT / "docs" / "conformance" / "EVIDENCE_REGISTRY.json"
BOUNDARY_SNAPSHOT = ROOT / ".ssot" / "releases" / "boundaries" / "bnd_transport-dispatch-track-001.snapshot.json"
SETUP_NOTE = ROOT / ".ssot" / "reports" / "transport-dispatch-track-setup.md"

REQUIRED_ADRS = {
    "adr:1045",
    "adr:1046",
    "adr:1047",
}
REQUIRED_SPECS = {
    "spc:2013",
    "spc:2014",
    "spc:2015",
    "spc:2016",
}
REQUIRED_CLAIMS = {
    "NEXT-006",
    "NEXT-007",
    "NEXT-008",
    "NEXT-009",
    "NEXT-010",
    "NEXT-011",
    "NEXT-012",
}


def _claim_rows() -> set[str]:
    rows: set[str] = set()
    for line in CLAIM_REGISTRY.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 4 or cells[0] in {"Claim ID", "---"}:
            continue
        rows.add(cells[0])
    return rows


def main() -> int:
    errors: list[str] = []

    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    if data.get("program", {}).get("active_boundary_id") != "bnd:transport-dispatch-track-001":
        errors.append("active SSOT boundary must be bnd:transport-dispatch-track-001")

    boundaries = {row["id"]: row for row in data.get("boundaries", [])}
    boundary = boundaries.get("bnd:transport-dispatch-track-001")
    if boundary is None:
        errors.append("transport-dispatch boundary row is missing from .ssot/registry.json")
    else:
        if boundary.get("status") != "frozen":
            errors.append("transport-dispatch boundary must be frozen")
        if boundary.get("frozen") is not True:
            errors.append("transport-dispatch boundary frozen flag must be true")

    if not REQUIRED_ADRS.issubset({row["id"] for row in data.get("adrs", [])}):
        errors.append("transport-dispatch ADR rows are incomplete")
    if not REQUIRED_SPECS.issubset({row["id"] for row in data.get("specs", [])}):
        errors.append("transport-dispatch spec rows are incomplete")

    next_targets = NEXT_TARGETS.read_text(encoding="utf-8")
    for marker in (
        "Transport-dispatch track",
        "single-dispatch transport flow",
        "endpoint-keyed JSON-RPC ingress",
        "ssot-registry 0.2.6",
    ):
        if marker not in next_targets:
            errors.append(f"NEXT_TARGETS.md missing marker: {marker}")

    claim_rows = _claim_rows()
    missing_claims = sorted(REQUIRED_CLAIMS - claim_rows)
    if missing_claims:
        errors.append(f"CLAIM_REGISTRY.md missing rows: {', '.join(missing_claims)}")

    evidence_claims = json.loads(EVIDENCE_REGISTRY.read_text(encoding="utf-8")).get("claims", {})
    for claim_id in REQUIRED_CLAIMS:
        if claim_id not in evidence_claims:
            errors.append(f"EVIDENCE_REGISTRY.json missing claim mapping for {claim_id}")

    if not BOUNDARY_SNAPSHOT.exists():
        errors.append(".ssot boundary snapshot for transport-dispatch track is missing")
    if not SETUP_NOTE.exists():
        errors.append("transport-dispatch setup note is missing")

    if errors:
        raise SystemExit("\n".join(errors))
    print("transport-dispatch track validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
