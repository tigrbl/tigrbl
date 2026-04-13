from __future__ import annotations

from pathlib import Path
from typing import Any

from common import repo_root
from simple_yaml import load_yaml


ROOT = repo_root()
CERT = ROOT / "certification"
REGISTRY_DIR = CERT / "registries"

CLAIM_FILES = {
    "current": CERT / "claims" / "current.yaml",
    "target": CERT / "claims" / "target.yaml",
    "blocked": CERT / "claims" / "blocked.yaml",
    "evidenced": CERT / "claims" / "evidenced.yaml",
}


def load_yaml_file(path: Path) -> Any:
    return load_yaml(path.read_text(encoding="utf-8"))


def norm(path: str) -> str:
    return path.replace("\\", "/")


def id_sort_key(value: str) -> tuple[str, int]:
    head, _, tail = value.rpartition("-")
    if tail.isdigit():
        return head, int(tail)
    return value, 0


def classify_bundle(path: str) -> str:
    path = norm(path)
    parts = path.split("/")
    if path.startswith("docs/conformance/releases/") and len(parts) >= 4:
        return "/".join(parts[:4])
    if path.startswith("docs/conformance/dev/") and len(parts) >= 4:
        return "/".join(parts[:4])
    if path.startswith("reports/current_state/"):
        return "reports/current_state"
    if path.startswith("reports/certification_state/profiles/"):
        return "reports/certification_state/profiles"
    if path.startswith("reports/certification_state/negative_corpora/"):
        return "reports/certification_state/negative_corpora"
    if path.startswith("reports/certification_state/"):
        return "reports/certification_state"
    if path.startswith(".github/workflows/"):
        return ".github/workflows"
    if "/tests/" in path:
        return path.split("/tests/")[0] + "/tests"
    if path.startswith("pkgs/") and len(parts) >= 3:
        return "/".join(parts[:3])
    if path.startswith("crates/") and len(parts) >= 2:
        return "/".join(parts[:2])
    if path.startswith("docs/") and len(parts) >= 2:
        return "/".join(parts[:2])
    if path.startswith("tools/") and len(parts) >= 2:
        return "/".join(parts[:2])
    if path.startswith("specs/"):
        return "specs"
    if path.startswith("adr/"):
        return "adr"
    return parts[0]


def classify_test_set(path: str) -> str:
    path = norm(path)
    if "/tests/" in path:
        return path.rsplit("/", 1)[0]
    return f"misc/{path.rsplit('/', 1)[0]}"


def is_test_pointer(path: str) -> bool:
    path = norm(path)
    return "/tests/" in path and (path.endswith(".py") or path.endswith(".rs"))


def claim_tier_target(claim_state: str, claim: dict[str, Any], lifecycle: str | None) -> str:
    if claim_state == "blocked":
        return "tier_0_blocked"
    if claim_state == "target":
        return "tier_2_checkpoint_target"
    if claim_state == "evidenced":
        return "tier_3_evidenced_release" if claim.get("certified_boundary") else "tier_2_evidenced_nonrelease"
    if claim_state == "current":
        if claim.get("certified_boundary") and lifecycle == "certified":
            return "tier_3_certified_release"
        if claim.get("certified_boundary"):
            return "tier_2_current_boundary"
        return "tier_1_governed_nonrelease"
    return "tier_unknown"


def claim_status(claim_state: str, lifecycle: str | None) -> str:
    if claim_state == "blocked":
        return "blocked"
    if lifecycle == "certified":
        return "certified"
    if lifecycle == "evidenced":
        return "evidenced"
    if lifecycle == "implemented":
        return "implemented"
    if lifecycle == "mapped":
        return "mapped"
    return claim_state


def feature_description(feature: dict[str, Any], claim_title: str) -> str:
    name = feature["name"]
    package = feature["package"]
    crate = feature["crate"]
    if name.startswith("Canonical op "):
        op = name.replace("Canonical op ", "", 1)
        return f"Tracks the canonical `{op}` surface as a governed feature with package/crate ownership and executable evidence pointers."
    return f"{claim_title} Package owner `{package}` and crate owner `{crate}` define the tracked implementation surface."


def sequence_map(keys: list[str], prefix: str) -> dict[str, str]:
    return {key: f"{prefix}-{index:04d}" for index, key in enumerate(sorted(keys), start=1)}


def build_universal_registry() -> dict[str, Any]:
    next_target = load_yaml_file(CERT / "targets" / "next_target.yaml")
    lifecycle = load_yaml_file(CERT / "claims" / "lifecycle.yaml")

    claims_by_id: dict[str, dict[str, Any]] = {}
    claim_state_by_id: dict[str, str] = {}
    for state, path in CLAIM_FILES.items():
        payload = load_yaml_file(path)
        for claim in payload["claims"]:
            claims_by_id[claim["id"]] = claim
            claim_state_by_id[claim["id"]] = state

    lifecycle_by_id = {entry["id"]: entry for entry in lifecycle["claims"]}
    features = sorted(next_target["features"], key=lambda item: id_sort_key(item["id"]))

    feature_ids_by_claim: dict[str, list[str]] = {}
    for feature in features:
        feature_ids_by_claim.setdefault(feature["claim_target"], []).append(feature["id"])

    all_artifacts: set[str] = set()
    for feature in features:
        all_artifacts.update(norm(item) for item in feature.get("evidence_artifacts", []))
    for claim_id, claim in claims_by_id.items():
        entry = lifecycle_by_id.get(claim_id, {})
        for key in ("evidence", "public_contract_artifacts", "preserved_evidence", "owning_modules", "required_test_classes"):
            for item in entry.get(key, claim.get(key, [])) or []:
                if isinstance(item, str):
                    all_artifacts.add(norm(item))
        for item in claim.get("evidence", []) or []:
            if isinstance(item, str):
                all_artifacts.add(norm(item))

    bundle_roots = sorted({classify_bundle(path) for path in all_artifacts})
    bundle_ids = sequence_map(bundle_roots, "EBND")
    artifact_ids = sequence_map(list(all_artifacts), "EART")

    all_tests: set[str] = set()
    for entry in lifecycle_by_id.values():
        for item in entry.get("required_test_classes", []) or []:
            if isinstance(item, str):
                all_tests.add(norm(item))
    for feature in features:
        for item in feature.get("evidence_artifacts", []):
            if isinstance(item, str) and is_test_pointer(item):
                all_tests.add(norm(item))

    test_case_ids = sequence_map(list(all_tests), "TCASE")
    test_set_roots = sorted({classify_test_set(path) for path in all_tests})
    test_set_ids = sequence_map(test_set_roots, "TSET")

    evidence_bundles = [
        {
            "evidence_bundle_id": bundle_ids[bundle_root],
            "bundle_root": bundle_root,
        }
        for bundle_root in bundle_roots
    ]
    evidence_artifacts = [
        {
            "evidence_artifact_id": artifact_ids[path],
            "bundle_id": bundle_ids[classify_bundle(path)],
            "artifact_pointer": path,
            "artifact_kind": "test_case" if path in test_case_ids else "artifact",
        }
        for path in sorted(all_artifacts)
    ]
    test_sets = [
        {
            "test_set_id": test_set_ids[test_set_root],
            "test_set_pointer": test_set_root,
        }
        for test_set_root in test_set_roots
    ]
    test_cases = [
        {
            "test_case_id": test_case_ids[path],
            "test_case_pointer": path,
            "test_set_id": test_set_ids[classify_test_set(path)],
            "evidence_artifact_id": artifact_ids[path],
            "evidence_bundle_id": bundle_ids[classify_bundle(path)],
        }
        for path in sorted(all_tests)
    ]

    feature_rows: list[dict[str, Any]] = []
    for index, feature in enumerate(features, start=1):
        claim_id = feature["claim_target"]
        claim = claims_by_id[claim_id]
        claim_state = claim_state_by_id[claim_id]
        lifecycle_entry = lifecycle_by_id.get(claim_id, {})
        artifact_paths = [norm(item) for item in feature.get("evidence_artifacts", [])]
        feature_rows.append(
            {
                "feature_registry_row_id": f"FREG-{index:04d}",
                "feature_id": feature["id"],
                "feature_name": feature["name"],
                "feature_description": feature_description(feature, claim["title"]),
                "feature_state": feature["state"],
                "feature_phase": feature["phase"],
                "feature_owner": feature["owner"],
                "feature_package": feature["package"],
                "feature_crate": feature["crate"],
                "feature_test_class": feature["test_class"],
                "mapped_claim_id": claim_id,
                "mapped_claim_state": claim_state,
                "mapped_claim_lifecycle": lifecycle_entry.get("lifecycle", ""),
                "mapped_claim_tier_target": claim_tier_target(claim_state, claim, lifecycle_entry.get("lifecycle")),
                "mapped_claim_status": claim_status(claim_state, lifecycle_entry.get("lifecycle")),
                "evidence_bundle_ids": [bundle_ids[classify_bundle(path)] for path in artifact_paths],
                "evidence_artifact_ids": [artifact_ids[path] for path in artifact_paths],
                "evidence_pointers": artifact_paths,
                "test_case_ids": [test_case_ids[path] for path in artifact_paths if path in test_case_ids],
                "test_pointers": [path for path in artifact_paths if path in test_case_ids],
            }
        )

    claim_rows: list[dict[str, Any]] = []
    for index, claim_id in enumerate(sorted(claims_by_id, key=id_sort_key), start=1):
        claim = claims_by_id[claim_id]
        claim_state = claim_state_by_id[claim_id]
        lifecycle_entry = lifecycle_by_id.get(claim_id, {})
        feature_ids = sorted(feature_ids_by_claim.get(claim_id, []), key=id_sort_key)
        pointers: list[str] = []
        for item in claim.get("evidence", []) or []:
            if isinstance(item, str):
                pointers.append(norm(item))
        for key in ("public_contract_artifacts", "preserved_evidence", "owning_modules"):
            pointers.extend(norm(item) for item in lifecycle_entry.get(key, []) or [] if isinstance(item, str))
        pointers = sorted(dict.fromkeys(pointers))
        claim_rows.append(
            {
                "claim_registry_row_id": f"CREG-{index:04d}",
                "claim_id": claim_id,
                "claim_title": claim["title"],
                "claim_state": claim_state,
                "claim_public": claim.get("public", ""),
                "claim_certified_boundary": claim.get("certified_boundary", ""),
                "claim_owner": claim["owner"],
                "claim_profile_or_phase": claim.get("profile") or claim.get("phase") or lifecycle_entry.get("target_mapping", ""),
                "claim_lifecycle": lifecycle_entry.get("lifecycle", ""),
                "claim_tier_target": claim_tier_target(claim_state, claim, lifecycle_entry.get("lifecycle")),
                "claim_status": claim_status(claim_state, lifecycle_entry.get("lifecycle")),
                "mapped_feature_ids": feature_ids,
                "required_test_pointers": [norm(item) for item in lifecycle_entry.get("required_test_classes", []) or [] if isinstance(item, str)],
                "evidence_bundle_ids": [bundle_ids[classify_bundle(path)] for path in pointers],
                "evidence_artifact_ids": [artifact_ids[path] for path in pointers],
                "evidence_pointers": pointers,
            }
        )

    test_rows: list[dict[str, Any]] = []
    row_index = 1
    for claim_id in sorted(lifecycle_by_id, key=id_sort_key):
        claim = claims_by_id.get(claim_id)
        if claim is None:
            continue
        claim_state = claim_state_by_id[claim_id]
        lifecycle_entry = lifecycle_by_id[claim_id]
        feature_ids = feature_ids_by_claim.get(claim_id, [""])
        for test_path in sorted(norm(item) for item in lifecycle_entry.get("required_test_classes", []) or [] if isinstance(item, str)):
            for feature_id in feature_ids:
                test_rows.append(
                    {
                        "test_registry_row_id": f"TREG-{row_index:04d}",
                        "test_case_id": test_case_ids[test_path],
                        "test_case_pointer": test_path,
                        "test_set_id": test_set_ids[classify_test_set(test_path)],
                        "test_set_pointer": classify_test_set(test_path),
                        "mapped_feature_id": feature_id,
                        "mapped_claim_id": claim_id,
                        "mapped_claim_state": claim_state,
                        "mapped_claim_lifecycle": lifecycle_entry.get("lifecycle", ""),
                        "evidence_bundle_id": bundle_ids[classify_bundle(test_path)],
                        "evidence_artifact_id": artifact_ids[test_path],
                        "evidence_pointer": test_path,
                    }
                )
                row_index += 1

    naming_conventions = [
        {
            "entity_type": "feature",
            "source_id_format": "NEXT-FEAT-NNN",
            "generated_registry_id_format": "FREG-NNNN",
            "example": "NEXT-FEAT-009 / FREG-0009",
            "notes": "Feature rows in certification/targets/next_target.yaml.",
        },
        {
            "entity_type": "claim",
            "source_id_format": "<FAMILY>-NNN",
            "generated_registry_id_format": "CREG-NNNN",
            "example": "NEXT-011 / CREG-0015",
            "notes": "Claim families include CUR, NEXT, BLK, and EVD.",
        },
        {
            "entity_type": "evidence_bundle",
            "source_id_format": "derived from normalized bundle root",
            "generated_registry_id_format": "EBND-NNNN",
            "example": "docs/conformance/releases/0.3.18 -> EBND-0001",
            "notes": "Bundle roots group related evidence artifacts.",
        },
        {
            "entity_type": "evidence_artifact",
            "source_id_format": "derived from normalized artifact path",
            "generated_registry_id_format": "EART-NNNN",
            "example": "pkgs/core/tigrbl_atoms/tests/test_sys_atoms.py -> EART-0001",
            "notes": "Artifact IDs are stable for a given sorted path set.",
        },
        {
            "entity_type": "test_case",
            "source_id_format": "derived from normalized test file path",
            "generated_registry_id_format": "TCASE-NNNN",
            "example": "pkgs/core/tigrbl_atoms/tests/test_sys_atoms.py -> TCASE-0001",
            "notes": "One row per test case in the universal registry.",
        },
        {
            "entity_type": "test_set",
            "source_id_format": "derived from normalized test directory",
            "generated_registry_id_format": "TSET-NNNN",
            "example": "pkgs/core/tigrbl_atoms/tests -> TSET-0001",
            "notes": "Groups related test cases by containing set directory.",
        },
    ]

    return {
        "schema_version": 1,
        "authority_model": {
            "name": "universal-certification-registry",
            "description": "Single normalized registry artifact for features, claims, tests, and evidence.",
            "source_roots": {
                "targets": "certification/targets/next_target.yaml",
                "claims": [norm(str(path.relative_to(ROOT))) for path in CLAIM_FILES.values()],
                "lifecycle": "certification/claims/lifecycle.yaml",
            },
            "output_roots": {
                "universal_registry": "certification/registries/universal_registry.json",
                "feature_registry_csv": "certification/registries/feature_registry.csv",
                "claims_registry_csv": "certification/registries/claims_registry.csv",
                "test_registry_csv": "certification/registries/test_registry.csv",
                "naming_conventions_csv": "certification/registries/naming_conventions.csv",
            },
        },
        "naming_conventions": naming_conventions,
        "evidence_bundles": evidence_bundles,
        "evidence_artifacts": evidence_artifacts,
        "test_sets": test_sets,
        "test_cases": test_cases,
        "features": feature_rows,
        "claims": claim_rows,
        "test_registry": test_rows,
    }
