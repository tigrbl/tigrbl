from __future__ import annotations

import ast
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10
    import tomli as tomllib

PACKAGE_NAME = "tigrbl_core"
PACKAGE_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = PACKAGE_ROOT / PACKAGE_NAME
TESTS_DIR = PACKAGE_ROOT / "tests"

# Static snapshot from pyproject.toml [project.dependencies].
ALLOWED_TOP_LEVEL_IMPORTS = {
    "tigrbl_typing",
    "tomli_w",
    "tomli",
    "tomllib",
    "yaml",
    "tigrbl_atoms",
    "tigrbl_spec",
    "pydantic",
    "pydantic_core",
}


def _collect_top_level_imports(package_dir: Path) -> set[str]:
    imports: set[str] = set()
    for module_file in package_dir.rglob("*.py"):
        tree = ast.parse(
            module_file.read_text(encoding="utf-8"), filename=str(module_file)
        )
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".", maxsplit=1)[0])
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0 and node.module:
                    imports.add(node.module.split(".", maxsplit=1)[0])
    return imports


def test_only_declared_dependencies_are_imported() -> None:
    stdlib = set(sys.stdlib_module_names)
    imported = _collect_top_level_imports(PACKAGE_DIR)

    disallowed = {
        module
        for module in imported
        if module not in stdlib
        and module != PACKAGE_NAME
        and module not in ALLOWED_TOP_LEVEL_IMPORTS
    }

    assert not disallowed, (
        "Found imports that are not in the static dependency allowlist: "
        f"{sorted(disallowed)}"
    )


def test_core_does_not_import_base_concrete_kernel_or_runtime() -> None:
    imported = _collect_top_level_imports(PACKAGE_DIR)

    forbidden = {
        "tigrbl_base",
        "tigrbl_concrete",
        "tigrbl_kernel",
        "tigrbl_runtime",
    }

    assert imported.isdisjoint(forbidden)


def test_core_pyproject_does_not_depend_on_public_facade() -> None:
    pyproject = tomllib.loads((PACKAGE_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies = pyproject["project"]["dependencies"]

    assert "tigrbl" not in dependencies


def test_core_package_local_tests_do_not_import_public_facade() -> None:
    imported = _collect_top_level_imports(TESTS_DIR)

    assert "tigrbl" not in imported
