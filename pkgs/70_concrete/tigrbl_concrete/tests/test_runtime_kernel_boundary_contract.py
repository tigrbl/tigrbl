from __future__ import annotations

import ast
import importlib.metadata
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PACKAGE_ROOT / "tigrbl_concrete"
PYPROJECT = PACKAGE_ROOT / "pyproject.toml"


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name.split(".", maxsplit=1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            modules.add(node.module.split(".", maxsplit=1)[0])
    return modules


def test_concrete_package_keeps_kernel_imports_out_of_all_modules() -> None:
    violations = [
        str(path.relative_to(PACKAGE_ROOT))
        for path in SOURCE_ROOT.rglob("*.py")
        if "tigrbl_kernel" in _imports(path)
    ]

    assert violations == []


def test_concrete_declares_runtime_dependency_without_kernel_dependency() -> None:
    text = PYPROJECT.read_text(encoding="utf-8")

    assert '"tigrbl-runtime"' in text
    assert '"tigrbl-kernel"' not in text


def test_installed_concrete_distribution_metadata_omits_kernel_dependency() -> None:
    requirements = importlib.metadata.requires("tigrbl-concrete") or []
    normalized = {req.split(maxsplit=1)[0].split(";", maxsplit=1)[0] for req in requirements}

    assert "tigrbl-runtime" in normalized
    assert "tigrbl-kernel" not in normalized


def test_concrete_authoring_and_lowering_modules_do_not_import_runtime() -> None:
    authoring_roots = (
        SOURCE_ROOT / "factories",
        SOURCE_ROOT / "shortcuts",
        SOURCE_ROOT / "_decorators",
        SOURCE_ROOT / "_mapping" / "appspec",
    )
    authoring_files = [
        path
        for root in authoring_roots
        for path in root.rglob("*.py")
        if path.exists()
    ]
    authoring_files.append(SOURCE_ROOT / "webhooks.py")

    violations = [
        str(path.relative_to(PACKAGE_ROOT))
        for path in authoring_files
        if "tigrbl_runtime" in _imports(path)
    ]

    assert violations == []


def test_camelcase_define_make_derive_authoring_surfaces_are_not_runtime_owned() -> None:
    runtime_root = PACKAGE_ROOT.parent / "tigrbl_runtime" / "tigrbl_runtime"
    runtime_exports: list[tuple[str, str]] = []
    for path in runtime_root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.name.startswith(("Make", "Define", "Derive")):
                    runtime_exports.append(
                        (str(path.relative_to(runtime_root)), node.name)
                    )

    assert runtime_exports == []
