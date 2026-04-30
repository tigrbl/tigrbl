from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from common import repo_root
from generate_feature_governance_link_matrix import (
    HIGHLIGHTED_ADR_IDS,
    HIGHLIGHTED_SPEC_IDS,
    SELECTED_FEATURE_IDS,
)


ROOT = repo_root()
REGISTRY_PATH = ROOT / ".ssot" / "registry.json"
DEFAULT_OUTPUT = ROOT / ".ssot" / "reports" / "feature-governance-tree.md"


def _load_registry(path: Path = REGISTRY_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _by_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row["id"]: row for row in rows}


def _sorted_unique(values: list[str]) -> list[str]:
    return sorted(dict.fromkeys(values))


def _normalize_ids(ids: list[str], prefix: str) -> list[str]:
    return sorted(
        value for value in ids if isinstance(value, str) and value.startswith(prefix)
    )


def _normalized_path(path: str) -> str:
    return path.replace("\\", "/")


def _doc_number(doc_id: str) -> int:
    _, _, tail = doc_id.partition(":")
    return int(tail)


def _doc_filename(doc_id: str) -> str:
    prefix = "ADR" if doc_id.startswith("adr:") else "SPEC"
    return f"{prefix}-{_doc_number(doc_id):04d}"


def _validate_doc_entry(
    entry: dict[str, Any] | None,
    doc_id: str,
    *,
    root: Path,
    expected_prefix: str,
) -> list[str]:
    errors: list[str] = []
    if entry is None:
        return [f"Missing registry entry for {doc_id}."]

    path = entry.get("path")
    if not isinstance(path, str):
        return [f"Registry entry {doc_id} is missing a string path."]

    normalized = _normalized_path(path)
    expected_dir = f".ssot/{expected_prefix}/"
    if not normalized.startswith(expected_dir):
        errors.append(
            f"Registry entry {doc_id} points to {normalized}, expected it under {expected_dir}."
        )

    doc_path = root / normalized
    if not doc_path.exists():
        errors.append(f"Document file for {doc_id} does not exist: {normalized}.")

    expected_name = _doc_filename(doc_id)
    if expected_name not in Path(normalized).name:
        errors.append(
            f"Registry entry {doc_id} points to {normalized}, expected filename containing {expected_name}."
        )
    return errors


def build_report(
    registry: dict[str, Any],
    *,
    selected_feature_ids: list[str] | None = None,
    highlighted_adr_ids: list[str] | None = None,
    highlighted_spec_ids: list[str] | None = None,
    root: Path = ROOT,
) -> dict[str, Any]:
    selected_feature_ids = selected_feature_ids or SELECTED_FEATURE_IDS
    highlighted_adr_ids = highlighted_adr_ids or HIGHLIGHTED_ADR_IDS
    highlighted_spec_ids = highlighted_spec_ids or HIGHLIGHTED_SPEC_IDS

    features_by_id = _by_id(registry.get("features", []))
    specs_by_id = _by_id(registry.get("specs", []))
    adrs_by_id = _by_id(registry.get("adrs", []))

    errors: list[str] = []
    selected_features: list[dict[str, Any]] = []
    for feature_id in selected_feature_ids:
        feature = features_by_id.get(feature_id)
        if feature is None:
            errors.append(f"Missing selected feature {feature_id}.")
            continue
        if not feature_id.startswith("feat:"):
            errors.append(f"Selected row {feature_id} is not a feature id.")
            continue
        selected_features.append(feature)

    selected_features.sort(key=lambda item: item["id"])

    feature_rows = [
        {
            "feature_id": feature["id"],
            "title": str(feature.get("title", "")),
            "implementation_status": str(feature.get("implementation_status", "")),
            "adr_ids": _normalize_ids(feature.get("adr_ids", []), "adr:"),
            "spec_ids": _normalize_ids(feature.get("spec_ids", []), "spc:"),
        }
        for feature in selected_features
    ]

    selected_spec_ids = _sorted_unique(
        list(highlighted_spec_ids)
        + [spec_id for row in feature_rows for spec_id in row["spec_ids"]]
    )
    selected_adr_ids = _sorted_unique(
        list(highlighted_adr_ids)
        + [adr_id for row in feature_rows for adr_id in row["adr_ids"]]
    )

    spec_rows: list[dict[str, Any]] = []
    for spec_id in selected_spec_ids:
        spec = specs_by_id.get(spec_id)
        if spec is None:
            errors.append(f"Missing selected spec {spec_id}.")
            continue
        errors.extend(
            _validate_doc_entry(spec, spec_id, root=root, expected_prefix="specs")
        )
        spec_rows.append(
            {
                "spec_id": spec_id,
                "title": str(spec.get("title", "")),
                "adr_ids": _normalize_ids(spec.get("adr_ids", []), "adr:"),
            }
        )

    for adr_id in selected_adr_ids:
        adr = adrs_by_id.get(adr_id)
        if adr is None:
            errors.append(f"Missing selected ADR {adr_id}.")
            continue
        errors.extend(
            _validate_doc_entry(adr, adr_id, root=root, expected_prefix="adr")
        )

    if errors:
        raise ValueError("\n".join(errors))

    spec_rows.sort(key=lambda item: item["spec_id"])
    specs_by_selected_adr: dict[str, list[dict[str, Any]]] = {
        adr_id: [] for adr_id in selected_adr_ids
    }
    orphan_specs: list[dict[str, Any]] = []
    for spec_row in spec_rows:
        attached = False
        for adr_id in spec_row["adr_ids"]:
            if adr_id in specs_by_selected_adr:
                specs_by_selected_adr[adr_id].append(spec_row)
                attached = True
        if not attached:
            orphan_specs.append(spec_row)

    features_by_spec: dict[str, list[dict[str, Any]]] = {spec_row["spec_id"]: [] for spec_row in spec_rows}
    direct_adr_features: dict[str, list[dict[str, Any]]] = {adr_id: [] for adr_id in selected_adr_ids}
    feature_orphans: list[dict[str, Any]] = []

    for feature_row in feature_rows:
        attached_to_spec = False
        for spec_id in feature_row["spec_ids"]:
            if spec_id in features_by_spec:
                features_by_spec[spec_id].append(feature_row)
                attached_to_spec = True
        if attached_to_spec:
            continue
        attached_to_adr = False
        for adr_id in feature_row["adr_ids"]:
            if adr_id in direct_adr_features:
                direct_adr_features[adr_id].append(feature_row)
                attached_to_adr = True
        if not attached_to_adr:
            feature_orphans.append(feature_row)

    for feature_list in features_by_spec.values():
        feature_list.sort(key=lambda item: item["feature_id"])
    for feature_list in direct_adr_features.values():
        feature_list.sort(key=lambda item: item["feature_id"])
    feature_orphans.sort(key=lambda item: item["feature_id"])

    return {
        "source_registry": ".ssot/registry.json",
        "selection_rule": (
            "Use the previously selected runtime/protocol feature set, plus the earlier highlighted ADR and SPEC set. "
            "Attach nodes only through direct declared links: spec.adr_ids and feature.spec_ids or feature.adr_ids."
        ),
        "adrs": [
            {
                "adr_id": adr_id,
                "title": str(adrs_by_id[adr_id].get("title", "")),
                "specs": specs_by_selected_adr.get(adr_id, []),
                "direct_features": direct_adr_features.get(adr_id, []),
            }
            for adr_id in selected_adr_ids
        ],
        "orphan_specs": orphan_specs,
        "features_by_spec": features_by_spec,
        "feature_orphans": feature_orphans,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Feature Governance Tree",
        "",
        "This report is generated from `.ssot/registry.json`.",
        "",
        "- `source file`: `.ssot/registry.json`",
        f"- `selection rule`: {report['selection_rule']}",
        "- `edge rule`: `ADR -> SPEC` only from `spec.adr_ids`; `SPEC -> feature` only from `feature.spec_ids`; `ADR -> feature` fallback only from direct `feature.adr_ids` when no included spec link is present.",
        "",
        "## ADR -> SPEC -> Feature",
        "",
    ]

    for adr in report["adrs"]:
        lines.append(f"- `{adr['adr_id']}` {adr['title']}")
        if adr["specs"]:
            for spec in adr["specs"]:
                lines.append(f"  - `{spec['spec_id']}` {spec['title']}")
                features = report["features_by_spec"].get(spec["spec_id"], [])
                if features:
                    for feature in features:
                        lines.append(
                            f"    - `{feature['feature_id']}` {feature['title']} (`{feature['implementation_status']}`)"
                        )
                else:
                    lines.append("    - `(no selected features link directly to this spec)`")
        else:
            lines.append("  - `(no included specs declare this ADR)`")

        if adr["direct_features"]:
            lines.append("  - Direct feature links without an included spec parent:")
            for feature in adr["direct_features"]:
                lines.append(
                    f"    - `{feature['feature_id']}` {feature['title']} (`{feature['implementation_status']}`)"
                )

    lines.extend(["", "## Included Specs Without Included ADR Parents", ""])
    if report["orphan_specs"]:
        for spec in report["orphan_specs"]:
            lines.append(f"- `{spec['spec_id']}` {spec['title']}")
            features = report["features_by_spec"].get(spec["spec_id"], [])
            if features:
                for feature in features:
                    lines.append(
                        f"  - `{feature['feature_id']}` {feature['title']} (`{feature['implementation_status']}`)"
                    )
            else:
                lines.append("  - `(no selected features link directly to this spec)`")
    else:
        lines.append("- `(none)`")

    lines.extend(["", "## Selected Features Without Included ADR or SPEC Parents", ""])
    if report["feature_orphans"]:
        for feature in report["feature_orphans"]:
            lines.append(
                f"- `{feature['feature_id']}` {feature['title']} (`{feature['implementation_status']}`)"
            )
    else:
        lines.append("- `(none)`")

    return "\n".join(lines) + "\n"


def write_report(markdown: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    report = build_report(_load_registry())
    write_report(render_markdown(report), args.output)


if __name__ == "__main__":
    main()
