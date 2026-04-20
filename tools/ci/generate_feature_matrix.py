from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / ".ssot" / "registry.json"
ADR_DIR = REPO_ROOT / ".ssot" / "adr"
SPEC_DIR = REPO_ROOT / ".ssot" / "specs"
DEFAULT_OUTPUT = REPO_ROOT / "reports" / "feature_matrix.csv"

ADR_REF_RE = re.compile(r"adr:\d+")
ID_RE = re.compile(r'^id:\s*"?(?P<value>[^"\n]+)"?', re.MULTILINE)
TITLE_RE = re.compile(r'^title:\s*"?(?P<value>[^"\n]+)"?', re.MULTILINE)


def repo_rel(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()


def yaml_docs(directory: Path) -> dict[str, dict[str, str]]:
    docs: dict[str, dict[str, str]] = {}
    for path in sorted(directory.glob("*.yaml")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        id_match = ID_RE.search(text)
        title_match = TITLE_RE.search(text)
        if not id_match:
            continue
        doc_id = id_match.group("value")
        docs[doc_id] = {
            "id": doc_id,
            "title": title_match.group("value") if title_match else path.stem,
            "path": repo_rel(path),
            "text": text,
        }
    return docs


def join_paths(paths: list[str]) -> str:
    return ";".join(sorted(dict.fromkeys(path.replace("\\", "/") for path in paths if path)))


def join_ids(values: list[str]) -> str:
    return ";".join(sorted(dict.fromkeys(value for value in values if value)))


def classify_paths(paths: set[str]) -> tuple[list[str], list[str]]:
    code_paths: list[str] = []
    doc_paths: list[str] = []
    for path in sorted(paths):
        clean = path.replace("\\", "/")
        if clean.endswith(".log"):
            continue
        if clean.startswith(("pkgs/", "crates/", "tools/", ".github/")):
            code_paths.append(clean)
            continue
        if clean.startswith(("docs/", ".ssot/", "reports/", "certification/")):
            doc_paths.append(clean)
    return code_paths, doc_paths


def heuristic_code_paths(feature_id: str, title: str) -> list[str]:
    key = f"{feature_id} {title}".lower()
    paths: list[str] = []

    if "cli" in feature_id or "server-support-" in feature_id:
        paths.extend(
            [
                "pkgs/core/tigrbl/tigrbl/cli.py",
                "pkgs/core/tigrbl/tigrbl/__main__.py",
            ]
        )
    if any(token in key for token in ("openapi", "openrpc", "swagger", "lens", "asyncapi", "json schema", "docs-support", "docs-ui")):
        paths.extend(
            [
                "pkgs/core/tigrbl/tigrbl/system/docs/__init__.py",
                "pkgs/core/tigrbl/tigrbl/system/docs/openrpc.py",
                "pkgs/core/tigrbl/tigrbl/system/docs/openapi/mount.py",
                "pkgs/core/tigrbl/tigrbl/system/docs/swagger.py",
                "pkgs/core/tigrbl/tigrbl/system/docs/lens.py",
            ]
        )
    if any(token in key for token in ("diagnostic", "healthz", "kernelz", "hookz", "methodz")):
        paths.extend(
            [
                "pkgs/core/tigrbl/tigrbl/system/diagnostics/router.py",
                "pkgs/core/tigrbl/tigrbl/system/diagnostics/healthz.py",
                "pkgs/core/tigrbl/tigrbl/system/diagnostics/kernelz.py",
                "pkgs/core/tigrbl/tigrbl/system/diagnostics/hookz.py",
                "pkgs/core/tigrbl/tigrbl/system/diagnostics/methodz.py",
            ]
        )
    if any(token in key for token in ("transport", "kernelplan", "jsonrpc-endpoint", "binding-driven", "dispatch")):
        paths.extend(
            [
                "pkgs/core/tigrbl_kernel/tigrbl_kernel/_compile.py",
                "pkgs/core/tigrbl_kernel/tigrbl_kernel/models.py",
                "pkgs/core/tigrbl_runtime/tigrbl_runtime/executors/packed.py",
                "pkgs/core/tigrbl_concrete/tigrbl_concrete/_mapping/model.py",
            ]
        )
    if "bindingspec" in key:
        paths.append("pkgs/core/tigrbl_core/tigrbl_core/_spec/binding_spec.py")
    if "middleware" in key:
        paths.extend(
            [
                "pkgs/core/tigrbl_concrete/tigrbl_concrete/_concrete/_middleware.py",
                "pkgs/core/tigrbl_concrete/tigrbl_concrete/_concrete/_cors_middleware.py",
            ]
        )
    if "hook" in key:
        paths.extend(
            [
                "pkgs/core/tigrbl_core/tigrbl_core/_spec/hook_spec.py",
                "pkgs/core/tigrbl_core/tigrbl_core/_spec/hook_types.py",
                "pkgs/core/tigrbl/tigrbl/hook/types.py",
            ]
        )
    if "static-files" in key or "mount_static" in key or "static files" in key:
        paths.append("pkgs/core/tigrbl_concrete/tigrbl_concrete/system/static.py")
    if "response" in key:
        paths.extend(
            [
                "pkgs/core/tigrbl_concrete/tigrbl_concrete/_concrete/_response.py",
                "pkgs/core/tigrbl_concrete/tigrbl_concrete/_concrete/_streaming_response.py",
                "pkgs/core/tigrbl_concrete/tigrbl_concrete/_concrete/_event_stream_response.py",
            ]
        )
    if "websocket" in key:
        paths.append("pkgs/core/tigrbl_concrete/tigrbl_concrete/_concrete/_websocket.py")
    if "sse" in key or "eventstream" in key:
        paths.append("pkgs/core/tigrbl_concrete/tigrbl_concrete/_concrete/_event_stream_response.py")
    if "multipart" in key or "uploaded-file" in key or "forms-and-uploads" in key:
        paths.append("pkgs/core/tigrbl_concrete/tigrbl_concrete/_concrete/_request.py")
    if "kernel-prime" in key or "opview cache" in key:
        paths.append("pkgs/core/tigrbl_kernel/tigrbl_kernel/core.py")

    return sorted(dict.fromkeys(paths))


def infer_topic(feature_id: str, title: str, spec_ids: set[str], doc_paths: set[str], row_origin: str) -> str:
    key = f"{feature_id} {title}".lower()
    if row_origin == "matrix_extra_profile":
        return "operator-profile"
    if row_origin == "matrix_extra_operator":
        return "operator"
    if any(spec in spec_ids for spec in {"spc:2017"}):
        return "cli"
    if any(spec in spec_ids for spec in {"spc:2021"}):
        return "diagnostics"
    if any(spec in spec_ids for spec in {"spc:2010", "spc:2019"}):
        return "docs"
    if any(spec in spec_ids for spec in {"spc:2020", "spc:2030", "spc:2040", "spc:2041", "spc:2028"}):
        return "operator"
    if any(spec in spec_ids for spec in {"spc:2007", "spc:2014", "spc:2024"}):
        return "transport"
    if any(spec in spec_ids for spec in {"spc:2012"}):
        return "auth-security"
    if any(spec in spec_ids for spec in {"spc:0603", "spc:0608", "spc:2002", "spc:2018"}):
        return "lifecycle"
    if "docs/developer/operator/profiles/" in " ".join(sorted(doc_paths)):
        return "operator-profile"
    if any(token in key for token in ("cli", "server-support-", "target resolution")):
        return "cli"
    if any(token in key for token in ("diagnostic", "healthz", "kernelz", "hookz", "methodz")):
        return "diagnostics"
    if any(token in key for token in ("transport", "kernelplan", "jsonrpc", "webtransport", "websocket", "bindingspec", "sse")):
        return "transport"
    if any(token in key for token in ("openapi", "openrpc", "asyncapi", "json schema", "swagger", "lens", "docs")):
        return "docs"
    if any(token in key for token in ("middleware", "static files", "multipart", "upload", "response", "hook")):
        return "operator"
    return "other"


EXTRA_ROWS: list[dict[str, Any]] = [
    {
        "feature_id": "matrix:operator-page:cookies-and-streaming",
        "title": "Operator page — cookies and streaming",
        "implementation_status": "matrix_extra",
        "lifecycle_stage": "matrix_extra",
        "row_origin": "matrix_extra_operator",
        "adr_ids": ["adr:1041", "adr:1058"],
        "spec_ids": ["spc:2020", "spc:2041"],
        "code_paths": [
            "pkgs/core/tigrbl_concrete/tigrbl_concrete/_concrete/_response.py",
            "pkgs/core/tigrbl_concrete/tigrbl_concrete/_concrete/_streaming_response.py",
        ],
        "doc_paths": ["docs/developer/operator/cookies-and-streaming.md"],
        "test_paths": [
            "pkgs/core/tigrbl_tests/tests/unit/test_phase7_operator_surface_closure.py",
            "pkgs/core/tigrbl_tests/tests/unit/test_phase7_operator_surface_docs_parity.py",
        ],
    },
    {
        "feature_id": "matrix:operator-page:docs-ui",
        "title": "Operator page — docs UI",
        "implementation_status": "matrix_extra",
        "lifecycle_stage": "matrix_extra",
        "row_origin": "matrix_extra_operator",
        "adr_ids": ["adr:1040"],
        "spec_ids": ["spc:2010"],
        "code_paths": [
            "pkgs/core/tigrbl/tigrbl/system/docs/__init__.py",
            "pkgs/core/tigrbl/tigrbl/system/docs/openapi/mount.py",
            "pkgs/core/tigrbl/tigrbl/system/docs/openrpc.py",
            "pkgs/core/tigrbl/tigrbl/system/docs/swagger.py",
            "pkgs/core/tigrbl/tigrbl/system/docs/lens.py",
        ],
        "doc_paths": [
            "docs/developer/operator/docs-ui.md",
            "docs/developer/CLI_REFERENCE.md",
        ],
        "test_paths": [
            "pkgs/core/tigrbl_tests/tests/unit/test_jsonrpc_openrpc.py",
            "pkgs/core/tigrbl_tests/tests/unit/test_phase7_operator_surface_docs_parity.py",
            "pkgs/core/tigrbl_tests/tests/i9n/test_mountable_openapi_uvicorn.py",
            "pkgs/core/tigrbl_tests/tests/i9n/test_mountable_openrpc_uvicorn.py",
            "pkgs/core/tigrbl_tests/tests/i9n/test_mountable_lens_uvicorn.py",
            "pkgs/core/tigrbl_tests/tests/i9n/test_mountable_swagger_uvicorn.py",
        ],
    },
    {
        "feature_id": "matrix:operator-page:forms-and-uploads",
        "title": "Operator page — forms and uploads",
        "implementation_status": "matrix_extra",
        "lifecycle_stage": "matrix_extra",
        "row_origin": "matrix_extra_operator",
        "adr_ids": ["adr:1041"],
        "spec_ids": ["spc:2020"],
        "code_paths": ["pkgs/core/tigrbl_concrete/tigrbl_concrete/_concrete/_request.py"],
        "doc_paths": ["docs/developer/operator/forms-and-uploads.md"],
        "test_paths": [
            "pkgs/core/tigrbl_tests/tests/unit/test_phase7_operator_surface_closure.py",
            "pkgs/core/tigrbl_tests/tests/unit/test_phase7_operator_surface_docs_parity.py",
        ],
    },
    {
        "feature_id": "matrix:operator-page:middleware-catalog",
        "title": "Operator page — middleware catalog",
        "implementation_status": "matrix_extra",
        "lifecycle_stage": "matrix_extra",
        "row_origin": "matrix_extra_operator",
        "adr_ids": ["adr:1041", "adr:1054"],
        "spec_ids": ["spc:2030"],
        "code_paths": [
            "pkgs/core/tigrbl_concrete/tigrbl_concrete/_concrete/_middleware.py",
            "pkgs/core/tigrbl_concrete/tigrbl_concrete/_concrete/_cors_middleware.py",
        ],
        "doc_paths": ["docs/developer/operator/middleware-catalog.md"],
        "test_paths": [
            "pkgs/core/tigrbl_tests/tests/unit/test_middleware_http_and_cors.py",
            "pkgs/core/tigrbl_tests/tests/unit/test_phase7_operator_surface_docs_parity.py",
        ],
    },
    {
        "feature_id": "matrix:operator-page:static-files",
        "title": "Operator page — static files",
        "implementation_status": "matrix_extra",
        "lifecycle_stage": "matrix_extra",
        "row_origin": "matrix_extra_operator",
        "adr_ids": ["adr:1041", "adr:1057"],
        "spec_ids": ["spc:2040"],
        "code_paths": ["pkgs/core/tigrbl_concrete/tigrbl_concrete/system/static.py"],
        "doc_paths": ["docs/developer/operator/static-files.md"],
        "test_paths": [
            "pkgs/core/tigrbl_tests/tests/unit/test_phase7_operator_surface_closure.py",
            "pkgs/core/tigrbl_tests/tests/unit/test_phase7_operator_surface_docs_parity.py",
        ],
    },
    {
        "feature_id": "matrix:operator-page:websockets-and-sse",
        "title": "Operator page — websockets and SSE",
        "implementation_status": "matrix_extra",
        "lifecycle_stage": "matrix_extra",
        "row_origin": "matrix_extra_operator",
        "adr_ids": ["adr:1006", "adr:1041", "adr:1058"],
        "spec_ids": ["spc:2007", "spc:2020", "spc:2041"],
        "code_paths": [
            "pkgs/core/tigrbl_concrete/tigrbl_concrete/_concrete/_websocket.py",
            "pkgs/core/tigrbl_concrete/tigrbl_concrete/_concrete/_event_stream_response.py",
        ],
        "doc_paths": ["docs/developer/operator/websockets-and-sse.md"],
        "test_paths": [
            "pkgs/core/tigrbl_tests/tests/unit/test_phase7_operator_surface_closure.py",
            "pkgs/core/tigrbl_tests/tests/unit/test_phase7_operator_surface_docs_parity.py",
        ],
    },
    {
        "feature_id": "matrix:operator-profile:static-origin",
        "title": "Operator profile — static-origin",
        "implementation_status": "matrix_extra",
        "lifecycle_stage": "matrix_extra",
        "row_origin": "matrix_extra_profile",
        "adr_ids": ["adr:1039", "adr:1041"],
        "spec_ids": [],
        "code_paths": ["pkgs/core/tigrbl/tigrbl/cli.py"],
        "doc_paths": [
            "docs/developer/operator/profiles/static-origin.md",
            "docs/developer/CLI_REFERENCE.md",
        ],
        "test_paths": [
            "pkgs/core/tigrbl_tests/tests/unit/test_phase8_cli_cmds.py",
            "pkgs/core/tigrbl_tests/tests/unit/test_phase8_cli_srv.py",
            "tools/ci/tests/test_phase6_tigrcorn_hardening.py",
        ],
    },
    {
        "feature_id": "matrix:operator-profile:strict-h1-origin",
        "title": "Operator profile — strict-h1-origin",
        "implementation_status": "matrix_extra",
        "lifecycle_stage": "matrix_extra",
        "row_origin": "matrix_extra_profile",
        "adr_ids": ["adr:1039", "adr:1041"],
        "spec_ids": [],
        "code_paths": ["pkgs/core/tigrbl/tigrbl/cli.py"],
        "doc_paths": [
            "docs/developer/operator/profiles/strict-h1-origin.md",
            "docs/developer/CLI_REFERENCE.md",
        ],
        "test_paths": [
            "pkgs/core/tigrbl_tests/tests/unit/test_phase8_cli_cmds.py",
            "pkgs/core/tigrbl_tests/tests/unit/test_phase8_cli_srv.py",
            "tools/ci/tests/test_phase6_tigrcorn_hardening.py",
        ],
    },
    {
        "feature_id": "matrix:operator-profile:strict-h2-origin",
        "title": "Operator profile — strict-h2-origin",
        "implementation_status": "matrix_extra",
        "lifecycle_stage": "matrix_extra",
        "row_origin": "matrix_extra_profile",
        "adr_ids": ["adr:1039", "adr:1041"],
        "spec_ids": [],
        "code_paths": ["pkgs/core/tigrbl/tigrbl/cli.py"],
        "doc_paths": [
            "docs/developer/operator/profiles/strict-h2-origin.md",
            "docs/developer/CLI_REFERENCE.md",
        ],
        "test_paths": [
            "pkgs/core/tigrbl_tests/tests/unit/test_phase8_cli_cmds.py",
            "pkgs/core/tigrbl_tests/tests/unit/test_phase8_cli_srv.py",
            "tools/ci/tests/test_phase6_tigrcorn_hardening.py",
        ],
    },
    {
        "feature_id": "matrix:operator-profile:strict-h3-edge",
        "title": "Operator profile — strict-h3-edge",
        "implementation_status": "matrix_extra",
        "lifecycle_stage": "matrix_extra",
        "row_origin": "matrix_extra_profile",
        "adr_ids": ["adr:1039", "adr:1041"],
        "spec_ids": [],
        "code_paths": ["pkgs/core/tigrbl/tigrbl/cli.py"],
        "doc_paths": [
            "docs/developer/operator/profiles/strict-h3-edge.md",
            "docs/developer/CLI_REFERENCE.md",
        ],
        "test_paths": [
            "pkgs/core/tigrbl_tests/tests/unit/test_phase8_cli_cmds.py",
            "pkgs/core/tigrbl_tests/tests/unit/test_phase8_cli_srv.py",
            "tools/ci/tests/test_phase6_tigrcorn_hardening.py",
        ],
    },
    {
        "feature_id": "matrix:operator-profile:strict-mtls-origin",
        "title": "Operator profile — strict-mtls-origin",
        "implementation_status": "matrix_extra",
        "lifecycle_stage": "matrix_extra",
        "row_origin": "matrix_extra_profile",
        "adr_ids": ["adr:1039", "adr:1041"],
        "spec_ids": [],
        "code_paths": ["pkgs/core/tigrbl/tigrbl/cli.py"],
        "doc_paths": [
            "docs/developer/operator/profiles/strict-mtls-origin.md",
            "docs/developer/CLI_REFERENCE.md",
        ],
        "test_paths": [
            "pkgs/core/tigrbl_tests/tests/unit/test_phase8_cli_cmds.py",
            "pkgs/core/tigrbl_tests/tests/unit/test_phase8_cli_srv.py",
            "tools/ci/tests/test_phase6_tigrcorn_hardening.py",
        ],
    },
]


def build_rows() -> list[dict[str, str]]:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    adrs = yaml_docs(ADR_DIR)
    specs = yaml_docs(SPEC_DIR)

    claims = {item["id"]: item for item in registry["claims"]}
    evidence = {item["id"]: item for item in registry["evidence"]}
    tests = {item["id"]: item for item in registry["tests"]}

    feature_ids = [item["id"] for item in registry["features"]]
    spec_mentions: dict[str, set[str]] = defaultdict(set)
    adr_mentions: dict[str, set[str]] = defaultdict(set)
    spec_adr_refs: dict[str, set[str]] = defaultdict(set)

    for spec_id, spec in specs.items():
        spec_adr_refs[spec_id].update(ADR_REF_RE.findall(spec["text"]))
        lower = spec["text"].lower()
        for feature_id in feature_ids:
            if feature_id.lower() in lower:
                spec_mentions[feature_id].add(spec_id)

    for adr_id, adr in adrs.items():
        lower = adr["text"].lower()
        for feature_id in feature_ids:
            if feature_id.lower() in lower:
                adr_mentions[feature_id].add(adr_id)

    rows: list[dict[str, str]] = []

    for feature in registry["features"]:
        feature_id = feature["id"]
        title = feature["title"]

        spec_ids = set(feature.get("spec_ids", []))
        spec_ids.update(spec_mentions.get(feature_id, set()))

        adr_ids = set(adr_mentions.get(feature_id, set()))
        for spec_id in spec_ids:
            adr_ids.update(spec_adr_refs.get(spec_id, set()))

        feature_test_paths: set[str] = set()
        evidence_paths: set[str] = set()
        claim_ids = set(feature.get("claim_ids", []))

        for claim_id in claim_ids:
            claim = claims.get(claim_id)
            if not claim:
                continue
            for test_id in claim.get("test_ids", []):
                test = tests.get(test_id)
                if test:
                    feature_test_paths.add(test["path"].replace("\\", "/"))
            for evidence_id in claim.get("evidence_ids", []):
                item = evidence.get(evidence_id)
                if item and item.get("path"):
                    evidence_paths.add(item["path"].replace("\\", "/"))

        for test_id in feature.get("test_ids", []):
            test = tests.get(test_id)
            if test:
                feature_test_paths.add(test["path"].replace("\\", "/"))

        code_paths, doc_paths = classify_paths(evidence_paths)
        for spec_id in spec_ids:
            spec = specs.get(spec_id)
            if spec:
                doc_paths.append(spec["path"])
        for adr_id in adr_ids:
            adr = adrs.get(adr_id)
            if adr:
                doc_paths.append(adr["path"])

        code_paths.extend(heuristic_code_paths(feature_id, title))
        code_paths = sorted(dict.fromkeys(code_paths))
        doc_path_set = set(doc_paths)

        rows.append(
            {
                "row_origin": "registry",
                "topic": infer_topic(feature_id, title, spec_ids, doc_path_set, "registry"),
                "feature_id": feature_id,
                "title": title,
                "implementation_status": feature.get("implementation_status", ""),
                "lifecycle_stage": feature.get("lifecycle", {}).get("stage", ""),
                "adr_ids": join_ids(list(adr_ids)),
                "spec_ids": join_ids(list(spec_ids)),
                "code_paths": join_paths(code_paths),
                "doc_paths": join_paths(list(doc_path_set)),
                "test_paths": join_paths(list(feature_test_paths)),
            }
        )

    for extra in EXTRA_ROWS:
        spec_ids = set(extra["spec_ids"])
        doc_path_set = set(extra["doc_paths"])
        for spec_id in spec_ids:
            spec = specs.get(spec_id)
            if spec:
                doc_path_set.add(spec["path"])
        for adr_id in extra["adr_ids"]:
            adr = adrs.get(adr_id)
            if adr:
                doc_path_set.add(adr["path"])
        rows.append(
            {
                "row_origin": extra["row_origin"],
                "topic": infer_topic(extra["feature_id"], extra["title"], spec_ids, doc_path_set, extra["row_origin"]),
                "feature_id": extra["feature_id"],
                "title": extra["title"],
                "implementation_status": extra["implementation_status"],
                "lifecycle_stage": extra["lifecycle_stage"],
                "adr_ids": join_ids(extra["adr_ids"]),
                "spec_ids": join_ids(extra["spec_ids"]),
                "code_paths": join_paths(extra["code_paths"]),
                "doc_paths": join_paths(list(doc_path_set)),
                "test_paths": join_paths(extra["test_paths"]),
            }
        )

    rows.sort(key=lambda row: (row["topic"], row["feature_id"]))
    return rows


def write_csv(output_path: Path, rows: list[dict[str, str]]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "row_origin",
                "topic",
                "feature_id",
                "title",
                "implementation_status",
                "lifecycle_stage",
                "adr_ids",
                "spec_ids",
                "code_paths",
                "doc_paths",
                "test_paths",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    rows = build_rows()
    write_csv(DEFAULT_OUTPUT, rows)
    print(f"wrote {len(rows)} rows to {repo_rel(DEFAULT_OUTPUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
