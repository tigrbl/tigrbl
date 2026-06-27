from __future__ import annotations

import ast
import sys
import tomllib
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = ROOT / "pkgs" / "core" / "tigrbl_runtime"
RUNTIME_ROOT = PACKAGE_ROOT / "tigrbl_runtime"
BOUNDARY_PATH = PACKAGE_ROOT / "BOUNDARY.yaml"
PYPROJECT_PATH = PACKAGE_ROOT / "pyproject.toml"


def _load_boundary() -> dict[str, Any]:
    data: dict[str, Any] = {}
    current_key: str | None = None
    for raw_line in BOUNDARY_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if not raw_line.startswith(" "):
            key, _, value = line.partition(":")
            current_key = key.strip()
            value = value.strip()
            if value:
                data[current_key] = _parse_scalar(value)
            else:
                data[current_key] = []
            continue
        if current_key is None:
            raise AssertionError(f"Invalid BOUNDARY.yaml line: {raw_line!r}")
        item = line.strip()
        if item.startswith("- "):
            if not isinstance(data[current_key], list):
                raise AssertionError(
                    f"BOUNDARY.yaml key {current_key!r} mixes list and mapping values"
                )
            data[current_key].append(_parse_scalar(item[2:].strip()))
            continue
        key, sep, value = item.partition(":")
        if not sep:
            raise AssertionError(f"Invalid BOUNDARY.yaml line: {raw_line!r}")
        if isinstance(data[current_key], list) and not data[current_key]:
            data[current_key] = {}
        if not isinstance(data[current_key], dict):
            raise AssertionError(
                f"BOUNDARY.yaml key {current_key!r} mixes list and mapping values"
            )
        data[current_key][key.strip()] = _parse_scalar(value.strip())

    if not isinstance(data, dict):
        raise AssertionError("BOUNDARY.yaml must contain a mapping")
    required = {
        "package",
        "role",
        "owns",
        "does_not_own",
        "forbidden_import_roots",
        "max_python_file_loc",
        "allowed_runtime_files",
        "legacy_token_ratchets",
    }
    missing = sorted(required - set(data))
    if missing:
        raise AssertionError(f"BOUNDARY.yaml missing required keys: {missing}")
    return data


def _parse_scalar(value: str) -> Any:
    if value == "true":
        return True
    if value == "false":
        return False
    try:
        return int(value)
    except ValueError:
        return value


def _declared_import_roots() -> set[str]:
    data = tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))
    deps = data.get("project", {}).get("dependencies", [])
    if not isinstance(deps, list):
        raise AssertionError("pyproject.toml [project].dependencies must be a list")
    roots = set()
    for dep in deps:
        name = str(dep).split(";", 1)[0].split("[", 1)[0]
        for marker in (">=", "<=", "==", "~=", "!=", ">", "<"):
            name = name.split(marker, 1)[0]
        name = name.strip().replace("-", "_")
        if name:
            roots.add(name)
    return roots


def _runtime_py_files() -> list[Path]:
    return sorted(RUNTIME_ROOT.rglob("*.py"))


def _relative(path: Path) -> str:
    return path.relative_to(RUNTIME_ROOT).as_posix()


def _top_level_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".", maxsplit=1)[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                roots.add(node.module.split(".", maxsplit=1)[0])
    return roots


def _literal_count(text: str, key: str) -> int:
    if key == "jsonrpc_literal":
        return text.count('"jsonrpc"') + text.count("'jsonrpc'")
    if key == "error_literal":
        return text.count('"error"') + text.count("'error'")
    if key == "id_literal":
        return text.count('"id"') + text.count("'id'")
    return text.count(key)


def validate() -> None:
    boundary = _load_boundary()
    if boundary["package"] != "tigrbl_runtime":
        raise AssertionError("BOUNDARY.yaml package must be tigrbl_runtime")

    declared = _declared_import_roots()
    allowed = set(sys.stdlib_module_names) | declared | {"tigrbl_runtime"}
    forbidden = set(boundary.get("forbidden_import_roots", []))
    max_loc = int(boundary["max_python_file_loc"])
    allowed_files = set(boundary["allowed_runtime_files"])
    actual_files = {_relative(path) for path in _runtime_py_files()}

    extra_files = sorted(actual_files - allowed_files)
    missing_files = sorted(allowed_files - actual_files)
    if extra_files or missing_files:
        raise AssertionError(
            "Runtime module tree drifted from BOUNDARY.yaml: "
            f"extra={extra_files}, missing={missing_files}"
        )

    bad_imports: dict[str, list[str]] = {}
    forbidden_imports: dict[str, list[str]] = {}
    long_files: dict[str, int] = {}
    token_counts = {key: 0 for key in boundary["legacy_token_ratchets"]}

    for path in _runtime_py_files():
        rel = _relative(path)
        text = path.read_text(encoding="utf-8")
        line_count = len(text.splitlines())
        if line_count > max_loc:
            long_files[rel] = line_count

        imports = _top_level_imports(path)
        disallowed = sorted(root for root in imports if root not in allowed)
        if disallowed:
            bad_imports[rel] = disallowed

        forbidden_hits = sorted(root for root in imports if root in forbidden)
        if forbidden_hits:
            forbidden_imports[rel] = forbidden_hits

        for key in token_counts:
            token_counts[key] += _literal_count(text, key)

    if long_files:
        raise AssertionError(f"Runtime Python files exceed {max_loc} LoC: {long_files}")
    if bad_imports:
        raise AssertionError(f"Runtime imports undeclared roots: {bad_imports}")
    if forbidden_imports:
        raise AssertionError(f"Runtime imports forbidden roots: {forbidden_imports}")

    limits = boundary["legacy_token_ratchets"]
    exceeded = {
        key: {"actual": actual, "limit": int(limits[key])}
        for key, actual in token_counts.items()
        if actual > int(limits[key])
    }
    if exceeded:
        raise AssertionError(f"Runtime legacy token ratchets exceeded: {exceeded}")


if __name__ == "__main__":
    validate()
