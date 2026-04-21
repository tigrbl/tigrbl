from __future__ import annotations

import ast
import re
import subprocess
import sys
import tomllib
from pathlib import Path

PACKAGE_IMPORT = "tigrbl_kernel"
PACKAGE_DEPENDENCY = "tigrbl-kernel"
PACKAGE_DIR = Path(__file__).resolve().parents[1] / "tigrbl_concrete"
PYPROJECT_PATH = Path(__file__).resolve().parents[1] / "pyproject.toml"


def _dependency_name(requirement: str) -> str:
    raw_name = re.split(r"[<>=!~; \[]", requirement, maxsplit=1)[0]
    return raw_name.replace("_", "-").replace(".", "-").lower()


def _literal_import_target(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value.split(".", maxsplit=1)[0]
    return None


def test_01_tigrbl_concrete_does_not_import_tigrbl_kernel() -> None:
    violations: list[str] = []

    for module_file in PACKAGE_DIR.rglob("*.py"):
        tree = ast.parse(
            module_file.read_text(encoding="utf-8-sig"), filename=str(module_file)
        )
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".", maxsplit=1)[0] == PACKAGE_IMPORT:
                        violations.append(f"{module_file}: import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if (
                    node.level == 0
                    and node.module
                    and node.module.split(".", maxsplit=1)[0] == PACKAGE_IMPORT
                ):
                    violations.append(f"{module_file}: from {node.module} import ...")
            elif isinstance(node, ast.Call):
                direct_import_call = (
                    isinstance(node.func, ast.Name) and node.func.id == "__import__"
                )
                importlib_call = (
                    isinstance(node.func, ast.Attribute)
                    and node.func.attr in {"import_module", "find_spec"}
                )
                if node.args and (direct_import_call or importlib_call):
                    target = _literal_import_target(node.args[0])
                    if target == PACKAGE_IMPORT:
                        violations.append(
                            f"{module_file}: dynamic import of {PACKAGE_IMPORT}"
                        )

    assert violations == []


def test_01_tigrbl_concrete_does_not_depend_on_tigrbl_kernel() -> None:
    pyproject_data = tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))
    project = pyproject_data["project"]
    declared_dependencies = list(project["dependencies"])
    for optional_group in project.get("optional-dependencies", {}).values():
        declared_dependencies.extend(optional_group)

    normalized_dependencies = {_dependency_name(dep) for dep in declared_dependencies}

    assert PACKAGE_DEPENDENCY not in normalized_dependencies


def test_01_tigrbl_concrete_import_does_not_load_tigrbl_kernel() -> None:
    probe = (
        "import sys\n"
        "sys.modules.pop('tigrbl_kernel', None)\n"
        "import tigrbl_concrete\n"
        "raise SystemExit(1 if 'tigrbl_kernel' in sys.modules else 0)\n"
    )

    result = subprocess.run(
        [sys.executable, "-c", probe],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr or result.stdout
