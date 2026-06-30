from __future__ import annotations

import ast
from pathlib import Path


CORE_ROOT = Path(__file__).resolve().parents[3]
HOT_PATH_ROOTS = (
    CORE_ROOT / "tigrbl_atoms" / "tigrbl_atoms",
    CORE_ROOT / "tigrbl_kernel" / "tigrbl_kernel",
    CORE_ROOT / "tigrbl_runtime" / "tigrbl_runtime",
)
DEPRECATED_TRANSPORT_MODULE_PREFIXES = (
    "tigrbl.transport",
    "tigrbl_concrete.transport",
)


def _python_sources() -> list[Path]:
    paths: list[Path] = []
    for root in HOT_PATH_ROOTS:
        paths.extend(
            path
            for path in root.rglob("*.py")
            if "__pycache__" not in path.parts
        )
    return paths


def _forbidden_imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    matches: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith(DEPRECATED_TRANSPORT_MODULE_PREFIXES):
                    matches.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.module.startswith(DEPRECATED_TRANSPORT_MODULE_PREFIXES):
                matches.append(node.module)
    return matches


def test_atoms_kernel_runtime_do_not_import_deprecated_transport_shims() -> None:
    offenders = {
        str(path.relative_to(CORE_ROOT)): imports
        for path in _python_sources()
        if (imports := _forbidden_imports(path))
    }

    assert offenders == {}


def test_atoms_kernel_runtime_do_not_dynamic_import_deprecated_transport_shims() -> None:
    offenders: dict[str, list[str]] = {}
    for path in _python_sources():
        text = path.read_text(encoding="utf-8")
        hits = [
            prefix
            for prefix in DEPRECATED_TRANSPORT_MODULE_PREFIXES
            if prefix in text
        ]
        if hits:
            offenders[str(path.relative_to(CORE_ROOT))] = hits

    assert offenders == {}
