from __future__ import annotations

import json
from pathlib import Path

from common import fail
from ssot_legacy_authority import assert_claims_passing, legacy_claim_rows, validate_claim_links

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / ".ssot" / "registry.json"
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

    rows = legacy_claim_rows(data)
    errors.extend(assert_claims_passing(REQUIRED_CLAIMS, rows))
    errors.extend(validate_claim_links(REQUIRED_CLAIMS, data))

    if not BOUNDARY_SNAPSHOT.exists():
        errors.append(".ssot boundary snapshot for transport-dispatch track is missing")
    if not SETUP_NOTE.exists():
        errors.append("transport-dispatch setup note is missing")

    if errors:
        fail(errors)
    print("transport-dispatch track validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
