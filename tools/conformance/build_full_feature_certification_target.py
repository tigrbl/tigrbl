"""Build the full-feature certification target from SSOT registry truth."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import date, timezone, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / ".ssot" / "registry.json"
REPORT_PATH = ROOT / ".ssot" / "reports" / "full-feature-certification-target-2026-05-10.json"
DOC_PATH = ROOT / "docs" / "conformance" / "FULL_FEATURE_CERTIFICATION_TARGET.md"
BOUNDARY_ID = "bnd:tigrbl-full-feature-certification-001"
BOUNDARY_TITLE = "Tigrbl full-feature certification target"


CONCERNS = (
    (
        "Python/Rust runtime lanes and performance",
        (
            "python",
            "rust",
            "microbench",
            "performance",
            "throughput",
            "callgraph",
            "transaction-hot-path",
            "request-hot-path",
            "request-envelope",
            "asgi-boundary",
            "schema-readiness",
        ),
    ),
    (
        "Protocol dispatch, framing, phases, and runtime taxonomy",
        (
            "protocol-runtime",
            "protocol-",
            "binding-subevent",
            "derived-runtime-subevent",
            "dispatch-exchange",
            "message-datagram",
            "framing",
            "app-framed",
            "segment-fusion",
            "completion-fence",
            "owner-dispatch",
            "phase-tree",
            "tx-phase",
            "hook-legality",
            "extended-hook",
            "transport-dispatch",
            "c-bulk",
            "byte-layout",
        ),
    ),
    (
        "Engine, DDL, schema, and datatype surfaces",
        (
            "engine",
            "ddl",
            "schema-migration",
            "sqlite",
            "session",
            "datatype",
            "typeadapter",
            "typeregistry",
            "typelowerer",
            "reflected",
            "bootstrap_dbschema",
            "ensure_schemas",
        ),
    ),
    (
        "Kernel, plan, cache, and dispatch ownership",
        (
            "kernel",
            "opview",
            "mapping-dispatch",
            "executor-dispatch",
            "ensure_primed",
            "default-kernel",
        ),
    ),
    (
        "REST, JSON-RPC, Uvicorn, routing, and error parity",
        (
            "jsonrpc",
            "rpc",
            "rest",
            "uvicorn",
            "routing",
            "route",
            "validation",
            "error",
            "endpoint",
            "multipart",
            "uploaded",
            "success-status",
            "operation-id",
            "header-parity",
            "harness",
        ),
    ),
    (
        "Documentation, schema, UIX, and mount surfaces",
        (
            "openapi",
            "openrpc",
            "asyncapi",
            "json-schema",
            "swagger",
            "lens",
            "docs",
            "uix",
            "mount",
            "payload",
            "kernelz",
            "static-files",
            "favicon",
            "uniform-diagnostics",
        ),
    ),
    (
        "Operator, middleware, security, and request helper surfaces",
        (
            "security",
            "apikey",
            "anon",
            "depends",
            "dependency",
            "middleware",
            "cookie",
            "operator",
            "oidc",
            "backgroundtask",
        ),
    ),
    (
        "Governance, conformance, profiles, tests, and evidence",
        (
            "cli",
            "conformance",
            "gate",
            "test-suite",
            "integration-test",
            "coverage",
            "registry",
            "certification",
            "evidence",
            "ssot",
            "profile-pack",
            "feature-granularity",
        ),
    ),
    (
        "Public API, helpers, facades, compatibility, and aliases",
        (
            "alias",
            "compat",
            "legacy",
            "core-access",
            "stdapi",
            "well-known",
            "facade",
            "decorator",
            "imperative",
            "attrdict",
            "bind-helper",
            "rebind",
            "build-",
            "include_tables",
            "get_schema",
            "mount_static",
            "mount_lens",
            "mount_swagger",
            "wrap_sessionmaker",
            "tigrblapp",
            "tigrblrouter",
            "bootstrappable",
            "monotone-spec-merge",
        ),
    ),
    (
        "Canonical operation families and exports",
        ("analytical", "realtime", "transfer", "canonical-", "family-membership"),
    ),
)


def is_excluded(feature: dict[str, Any]) -> bool:
    plan = feature.get("plan", {})
    lifecycle = feature.get("lifecycle", {})
    haystack = " ".join(
        str(feature.get(key, ""))
        for key in ("id", "title", "description")
    )
    haystack = f"{haystack} {plan.get('horizon')} {plan.get('slot')}".lower()
    return (
        plan.get("horizon") == "out_of_bounds"
        or lifecycle.get("stage") in {"deprecated", "obsolete", "removed"}
        or any(token in haystack for token in ("obsolete", "deprecated", "out_of_bounds", "out of bounds", "descoped"))
    )


def concern_for(feature: dict[str, Any]) -> str:
    plan = feature.get("plan", {})
    haystack = f"{feature.get('id', '')} {feature.get('title', '')} {plan.get('slot', '')}".lower()
    for concern, tokens in CONCERNS:
        if any(token in haystack for token in tokens):
            return concern
    return "Other"


def feature_row(feature: dict[str, Any]) -> dict[str, Any]:
    plan = feature.get("plan", {})
    lifecycle = feature.get("lifecycle", {})
    spec_ids = list(feature.get("spec_ids", []))
    test_ids = list(feature.get("test_ids", []))
    claim_ids = list(feature.get("claim_ids", []))
    blockers: list[str] = []
    if not spec_ids:
        blockers.append("missing_spec_link")
    if not test_ids:
        blockers.append("missing_required_test_plan")
    if not claim_ids:
        blockers.append("missing_claim_link")
    if not plan.get("target_claim_tier"):
        blockers.append("missing_target_claim_tier")
    if lifecycle.get("stage") != "active":
        blockers.append("non_active_lifecycle")
    return {
        "id": feature["id"],
        "title": feature["title"],
        "implementation_status": feature["implementation_status"],
        "concern": concern_for(feature),
        "horizon": plan.get("horizon"),
        "slot": plan.get("slot"),
        "target_claim_tier": plan.get("target_claim_tier"),
        "target_lifecycle_stage": plan.get("target_lifecycle_stage"),
        "lifecycle_stage": lifecycle.get("stage"),
        "spec_ids": spec_ids,
        "test_ids": test_ids,
        "claim_ids": claim_ids,
        "ready_for_freeze": not blockers,
        "freeze_blockers": blockers,
    }


def update_boundary(registry: dict[str, Any], feature_ids: list[str]) -> None:
    boundaries = registry.setdefault("boundaries", [])
    boundary = next((item for item in boundaries if item.get("id") == BOUNDARY_ID), None)
    payload = {
        "id": BOUNDARY_ID,
        "title": BOUNDARY_TITLE,
        "status": "draft",
        "frozen": False,
        "feature_ids": feature_ids,
        "profile_ids": [],
        "description": (
            "Draft full-feature certification target. This boundary is intentionally "
            "not frozen until all active in-scope gaps have linked specs, required "
            "tests, claims, evidence, and executable proof."
        ),
    }
    if boundary is None:
        boundaries.append(payload)
    else:
        boundary.clear()
        boundary.update(payload)


def main() -> None:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    candidates = [
        feature
        for feature in registry["features"]
        if feature.get("implementation_status") in {"absent", "partial"} and not is_excluded(feature)
    ]
    rows = [feature_row(feature) for feature in sorted(candidates, key=lambda item: item["id"])]
    update_boundary(registry, [row["id"] for row in rows])

    by_status = Counter(row["implementation_status"] for row in rows)
    by_concern: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        by_concern[row["concern"]][row["implementation_status"]] += 1

    report = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source_registry": ".ssot/registry.json",
        "boundary_id": BOUNDARY_ID,
        "boundary_status": "draft",
        "exclusion_policy": [
            "exclude plan.horizon=out_of_bounds",
            "exclude lifecycle.stage in deprecated/obsolete/removed",
            "exclude rows with obsolete/deprecated/out-of-bounds/descoped wording",
        ],
        "summary": {
            "total_active_gaps": len(rows),
            "absent": by_status["absent"],
            "partial": by_status["partial"],
            "ready_for_freeze": sum(1 for row in rows if row["ready_for_freeze"]),
            "blocked_from_freeze": sum(1 for row in rows if not row["ready_for_freeze"]),
        },
        "concerns": [
            {
                "concern": concern,
                "absent": counts["absent"],
                "partial": counts["partial"],
                "total": counts["absent"] + counts["partial"],
            }
            for concern, counts in sorted(by_concern.items())
        ],
        "features": rows,
    }

    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REGISTRY_PATH.write_text(json.dumps(registry, separators=(",", ":"), sort_keys=True) + "\n", encoding="utf-8")

    today = date.today().isoformat()
    lines = [
        "# Full-Feature Certification Target",
        "",
        f"Generated: {today}",
        "",
        "This is a derived planning view over `.ssot/registry.json`. The registry remains authoritative.",
        "",
        f"- Boundary: `{BOUNDARY_ID}`",
        "- Boundary status: `draft`",
        f"- Active in-scope gaps: `{len(rows)}`",
        f"- Absent: `{by_status['absent']}`",
        f"- Partial: `{by_status['partial']}`",
        f"- Ready for freeze: `{report['summary']['ready_for_freeze']}`",
        f"- Blocked from freeze: `{report['summary']['blocked_from_freeze']}`",
        "",
        "Rows are excluded when they are deprecated, obsolete, removed, descoped, or explicitly out of bounds.",
        "",
        "## Concern Summary",
        "",
        "| Concern | Absent | Partial | Total |",
        "|---|---:|---:|---:|",
    ]
    for item in report["concerns"]:
        lines.append(f"| {item['concern']} | {item['absent']} | {item['partial']} | {item['total']} |")
    lines.extend(
        [
            "",
            "## Freeze Blockers",
            "",
            "The boundary must remain draft until every row has linked specs, required tests, claims, target claim tier, and executable evidence.",
            "",
            "| Feature | Status | Concern | Blockers |",
            "|---|---|---|---|",
        ]
    )
    for row in rows:
        if row["ready_for_freeze"]:
            continue
        blockers = ", ".join(row["freeze_blockers"])
        lines.append(f"| `{row['id']}` | {row['implementation_status']} | {row['concern']} | {blockers} |")
    lines.extend(
        [
            "",
            "## Full Target Feature List",
            "",
            "| Feature | Status | Concern | Tier | Specs | Tests | Claims |",
            "|---|---|---|---|---:|---:|---:|",
        ]
    )
    for row in rows:
        lines.append(
            "| "
            f"`{row['id']}` | {row['implementation_status']} | {row['concern']} | "
            f"{row['target_claim_tier'] or ''} | {len(row['spec_ids'])} | {len(row['test_ids'])} | {len(row['claim_ids'])} |"
        )
    DOC_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
