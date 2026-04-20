from __future__ import annotations

import json
import re
from pathlib import Path

from common import repo_root


FEATURE_ID_RE = re.compile(r"\bfeat:[A-Za-z0-9._-]+\b")
ADR_ID_RE = re.compile(r"\badr:\d+\b")
ADR_FILE_RE = re.compile(r"\bADR-(\d+)\b", re.IGNORECASE)
SPEC_FILE_RE = re.compile(r"\bSPEC-(\d+)\b", re.IGNORECASE)
TEST_FILE_SUFFIXES = (
    "_test.py",
    ".test.py",
    ".spec.py",
    ".test.ts",
    ".test.tsx",
    ".spec.ts",
    ".spec.tsx",
    ".test.js",
    ".test.jsx",
    ".spec.js",
    ".spec.jsx",
)
DOC_PREFIXES = ("docs/", ".ssot/", "reports/", "certification/")
CODE_PREFIXES = ("pkgs/", "crates/", "tools/", ".github/", "apps/", "scripts/")
ROOT_CODE_FILES = {
    "pyproject.toml",
    "package.json",
    "package-lock.json",
    "Cargo.toml",
    "Cargo.lock",
    "Makefile",
    "uv.lock",
}


def load_registry() -> dict:
    registry_path = repo_root() / ".ssot" / "registry.json"
    return json.loads(registry_path.read_text(encoding="utf-8"))


def parse_yaml_body(text: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if re.match(r"^body:\s*[|>][-+]?\s*$", line):
            body_lines: list[str] = []
            block_indent: int | None = None
            for body_line in lines[index + 1 :]:
                if not body_line.strip():
                    body_lines.append("")
                    continue
                current_indent = len(body_line) - len(body_line.lstrip(" "))
                if block_indent is None:
                    block_indent = current_indent
                if current_indent < block_indent:
                    break
                body_lines.append(body_line[block_indent:])
            return "\n".join(body_lines).strip()
    return ""


def load_doc_bodies(entries: list[dict]) -> dict[str, str]:
    bodies: dict[str, str] = {}
    root = repo_root()
    for entry in entries:
        path = entry.get("path")
        doc_id = entry.get("id")
        if not isinstance(path, str) or not isinstance(doc_id, str):
            continue
        text = (root / path).read_text(encoding="utf-8")
        bodies[doc_id] = parse_yaml_body(text)
    return bodies


def normalize_paths(paths: set[str]) -> list[str]:
    return sorted(path.replace("\\", "/") for path in paths if path)


def classify_path(path: str) -> str:
    normalized = path.replace("\\", "/")
    name = Path(normalized).name
    if (
        normalized.startswith("tests/")
        or normalized.startswith("tools/ci/tests/")
        or "/tests/" in normalized
        or name.endswith(TEST_FILE_SUFFIXES)
    ):
        return "test"
    if normalized.startswith(CODE_PREFIXES) or name in ROOT_CODE_FILES:
        return "code"
    if normalized.startswith(DOC_PREFIXES):
        return "doc"
    if name.upper().startswith("README"):
        return "doc"
    if Path(name).suffix.lower() in {".md", ".rst", ".txt"}:
        return "doc"
    return "code"


def doc_id_from_text(text: str, prefix: str) -> set[str]:
    ids: set[str] = set()
    if prefix == "adr":
        ids.update(ADR_ID_RE.findall(text))
        ids.update(f"adr:{number}" for number in ADR_FILE_RE.findall(text))
        return ids
    ids.update(f"spc:{number}" for number in SPEC_FILE_RE.findall(text))
    return ids


def referenced_adr_ids(spec_bodies: dict[str, str], spec_ids: set[str]) -> set[str]:
    adr_ids: set[str] = set()
    for spec_id in spec_ids:
        body = spec_bodies.get(spec_id, "")
        adr_ids.update(doc_id_from_text(body, "adr"))
    return adr_ids


def doc_id_from_path(path: str, prefix: str) -> str | None:
    normalized = path.replace("\\", "/")
    name = Path(normalized).name
    if prefix == "adr":
        match = ADR_FILE_RE.search(name)
        return f"adr:{match.group(1)}" if match else None
    match = SPEC_FILE_RE.search(name)
    return f"spc:{match.group(1)}" if match else None


def related_ids(
    feature: dict,
    claims_by_id: dict[str, dict],
    tests_by_id: dict[str, dict],
    evidence_by_id: dict[str, dict],
) -> tuple[set[str], set[str]]:
    test_ids = set(feature.get("test_ids", []))
    evidence_ids: set[str] = set()

    for claim_id in feature.get("claim_ids", []):
        claim = claims_by_id.get(claim_id, {})
        test_ids.update(claim.get("test_ids", []))
        evidence_ids.update(claim.get("evidence_ids", []))

    previous_state: tuple[int, int] | None = None
    while previous_state != (len(test_ids), len(evidence_ids)):
        previous_state = (len(test_ids), len(evidence_ids))
        for test_id in tuple(test_ids):
            test = tests_by_id.get(test_id, {})
            evidence_ids.update(test.get("evidence_ids", []))
        for evidence_id in tuple(evidence_ids):
            evidence = evidence_by_id.get(evidence_id, {})
            test_ids.update(evidence.get("test_ids", []))

    return test_ids, evidence_ids


def feature_cell(
    feature: dict,
    claims_by_id: dict[str, dict],
    tests_by_id: dict[str, dict],
    evidence_by_id: dict[str, dict],
    specs_by_id: dict[str, dict],
    adrs_by_id: dict[str, dict],
    spec_bodies: dict[str, str],
    adr_bodies: dict[str, str],
) -> dict:
    feature_id = feature["id"]

    spec_ids = set(feature.get("spec_ids", []))
    spec_ids.update(
        spec_id for spec_id, body in spec_bodies.items() if feature_id in body
    )

    adr_ids = {adr_id for adr_id, body in adr_bodies.items() if feature_id in body}
    adr_ids.update(referenced_adr_ids(spec_bodies, spec_ids))

    test_ids, evidence_ids = related_ids(feature, claims_by_id, tests_by_id, evidence_by_id)

    code_paths: set[str] = set()
    doc_paths: set[str] = set()
    test_paths: set[str] = set()

    for spec_id in spec_ids:
        spec_path = specs_by_id.get(spec_id, {}).get("path")
        if isinstance(spec_path, str):
            doc_paths.add(spec_path)

    for adr_id in adr_ids:
        adr_path = adrs_by_id.get(adr_id, {}).get("path")
        if isinstance(adr_path, str):
            doc_paths.add(adr_path)

    for test_id in test_ids:
        test_path = tests_by_id.get(test_id, {}).get("path")
        if isinstance(test_path, str):
            test_paths.add(test_path)

    for evidence_id in evidence_ids:
        evidence_path = evidence_by_id.get(evidence_id, {}).get("path")
        if not isinstance(evidence_path, str):
            continue
        bucket = classify_path(evidence_path)
        if bucket == "test":
            test_paths.add(evidence_path)
        elif bucket == "doc":
            doc_paths.add(evidence_path)
        else:
            code_paths.add(evidence_path)

    for doc_path in tuple(doc_paths):
        adr_id = doc_id_from_path(doc_path, "adr")
        spec_id = doc_id_from_path(doc_path, "spc")
        if adr_id in adrs_by_id:
            adr_ids.add(adr_id)
        if spec_id in specs_by_id:
            spec_ids.add(spec_id)

    for spec_id in tuple(spec_ids):
        spec_body = spec_bodies.get(spec_id, "")
        adr_ids.update(doc_id_from_text(spec_body, "adr"))

    return {
        "feature_id": feature_id,
        "title": feature.get("title"),
        "implementation_status": feature.get("implementation_status"),
        "lifecycle_stage": feature.get("lifecycle", {}).get("stage"),
        "adr_ids": sorted(adr_ids),
        "spec_ids": sorted(spec_ids),
        "code_paths": normalize_paths(code_paths),
        "doc_paths": normalize_paths(doc_paths),
        "test_paths": normalize_paths(test_paths),
    }


def main() -> None:
    registry = load_registry()

    claims_by_id = {claim["id"]: claim for claim in registry.get("claims", [])}
    tests_by_id = {test["id"]: test for test in registry.get("tests", [])}
    evidence_by_id = {item["id"]: item for item in registry.get("evidence", [])}
    specs_by_id = {item["id"]: item for item in registry.get("specs", [])}
    adrs_by_id = {item["id"]: item for item in registry.get("adrs", [])}

    spec_bodies = load_doc_bodies(registry.get("specs", []))
    adr_bodies = load_doc_bodies(registry.get("adrs", []))

    cells = [
        feature_cell(
            feature=feature,
            claims_by_id=claims_by_id,
            tests_by_id=tests_by_id,
            evidence_by_id=evidence_by_id,
            specs_by_id=specs_by_id,
            adrs_by_id=adrs_by_id,
            spec_bodies=spec_bodies,
            adr_bodies=adr_bodies,
        )
        for feature in sorted(registry.get("features", []), key=lambda item: item["id"])
    ]

    output_path = repo_root() / "reports" / "feature_cells.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(cells, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(cells)} cells to {output_path}")


if __name__ == "__main__":
    main()
