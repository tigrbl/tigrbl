from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from registry_model import REGISTRY_DIR, build_universal_registry


def flatten(value: Any) -> str:
    if isinstance(value, list):
        return ";".join(str(item) for item in value)
    return str(value)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: flatten(row.get(key, "")) for key in fieldnames})


def main() -> None:
    registry = build_universal_registry()

    write_csv(
        REGISTRY_DIR / "feature_registry.csv",
        [
            "feature_registry_row_id",
            "feature_id",
            "feature_name",
            "feature_description",
            "feature_state",
            "feature_phase",
            "feature_owner",
            "feature_package",
            "feature_crate",
            "feature_test_class",
            "mapped_claim_id",
            "mapped_claim_state",
            "mapped_claim_lifecycle",
            "mapped_claim_tier_target",
            "mapped_claim_status",
            "evidence_bundle_ids",
            "evidence_artifact_ids",
            "evidence_pointers",
            "test_case_ids",
            "test_pointers",
        ],
        registry["features"],
    )
    write_csv(
        REGISTRY_DIR / "claims_registry.csv",
        [
            "claim_registry_row_id",
            "claim_id",
            "claim_title",
            "claim_state",
            "claim_public",
            "claim_certified_boundary",
            "claim_owner",
            "claim_profile_or_phase",
            "claim_lifecycle",
            "claim_tier_target",
            "claim_status",
            "mapped_feature_ids",
            "required_test_pointers",
            "evidence_bundle_ids",
            "evidence_artifact_ids",
            "evidence_pointers",
        ],
        registry["claims"],
    )
    write_csv(
        REGISTRY_DIR / "test_registry.csv",
        [
            "test_registry_row_id",
            "test_case_id",
            "test_case_pointer",
            "test_set_id",
            "test_set_pointer",
            "mapped_feature_id",
            "mapped_claim_id",
            "mapped_claim_state",
            "mapped_claim_lifecycle",
            "evidence_bundle_id",
            "evidence_artifact_id",
            "evidence_pointer",
        ],
        registry["test_registry"],
    )
    write_csv(
        REGISTRY_DIR / "naming_conventions.csv",
        [
            "entity_type",
            "source_id_format",
            "generated_registry_id_format",
            "example",
            "notes",
        ],
        registry["naming_conventions"],
    )

    print(f"Wrote CSV registries to {REGISTRY_DIR}")


if __name__ == "__main__":
    main()
