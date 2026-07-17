"""Prove that the parity matrix covers the live Tigrbl Pydantic call surface."""

from __future__ import annotations

import ast
from pathlib import Path


CERTIFIED_IMPORTS = {
    "AliasChoices",
    "BaseModel",
    "ConfigDict",
    "Field",
    "RootModel",
    "ValidationError",
    "create_model",
    "model_validator",
}

CERTIFIED_PYDANTIC_CORE_IMPORTS = {"PydanticUndefined"}

CERTIFIED_CONFIG_OPTIONS = {
    "extra",
    "from_attributes",
    "json_schema_extra",
}

CERTIFIED_METHOD_OPTIONS = {
    "model_dump": {"by_alias", "exclude_none"},
    "model_dump_json": {"exclude", "exclude_none"},
    "model_validate": set(),
    "model_validate_json": set(),
    "model_json_schema": {"ref_template"},
    "model_rebuild": {"force"},
}

CERTIFIED_FIELD_OPTIONS = {
    "default",
    "default_factory",
    "description",
    "examples",
    "ge",
    "json_schema_extra",
}


def _repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "pkgs" / "10_core").is_dir():
            return parent
    raise RuntimeError("Tigrbl repository root not found")


def _runtime_python_files():
    root = _repo_root() / "pkgs"
    included = {
        "00_typing",
        "10_core",
        "20_base",
        "30_orm",
        "40_atoms",
        "45_kernel",
        "50_runtime",
        "60_ops",
        "70_concrete",
        "80_facade",
        "90_engines",
        "95_client",
    }
    for package_layer in included:
        for path in (root / package_layer).rglob("*.py"):
            if "examples" not in path.parts and "tests" not in path.parts:
                yield path


def test_certified_symbols_cover_live_runtime_imports() -> None:
    imported: set[str] = set()
    for path in _runtime_python_files():
        tree = ast.parse(path.read_text(encoding="utf-8-sig"))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.ImportFrom)
                and node.level == 0
                and node.module == "pydantic"
            ):
                imported.update(item.name for item in node.names)

    assert imported <= CERTIFIED_IMPORTS
    assert imported


def test_certified_pydantic_core_symbols_cover_live_runtime_imports() -> None:
    imported: set[str] = set()
    for path in _runtime_python_files():
        tree = ast.parse(path.read_text(encoding="utf-8-sig"))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.ImportFrom)
                and node.level == 0
                and node.module == "pydantic_core"
            ):
                imported.update(item.name for item in node.names)

    assert imported <= CERTIFIED_PYDANTIC_CORE_IMPORTS
    assert imported


def test_certified_config_options_cover_direct_runtime_declarations() -> None:
    observed: set[str] = set()
    for path in _runtime_python_files():
        tree = ast.parse(path.read_text(encoding="utf-8-sig"))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "ConfigDict"
            ):
                observed.update(item.arg for item in node.keywords if item.arg)

    assert observed <= CERTIFIED_CONFIG_OPTIONS
    assert observed


def test_certified_method_options_cover_live_runtime_calls() -> None:
    observed = {name: set() for name in CERTIFIED_METHOD_OPTIONS}
    for path in _runtime_python_files():
        tree = ast.parse(path.read_text(encoding="utf-8-sig"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                continue
            name = node.func.attr
            if name in observed:
                observed[name].update(item.arg for item in node.keywords if item.arg)

    for name, options in observed.items():
        assert options <= CERTIFIED_METHOD_OPTIONS[name], (name, options)


def test_certified_field_options_cover_direct_runtime_declarations() -> None:
    observed: set[str] = set()
    for path in _runtime_python_files():
        tree = ast.parse(path.read_text(encoding="utf-8-sig"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "Field":
                observed.update(item.arg for item in node.keywords if item.arg)

    assert observed <= CERTIFIED_FIELD_OPTIONS


def test_tigrbl_model_runtime_source_has_no_pydantic_imports() -> None:
    package_root = Path(__file__).resolve().parents[2] / "tigrbl_model"
    violations = []
    for path in package_root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8-sig"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import) and any(
                item.name == "pydantic" or item.name.startswith("pydantic.")
                for item in node.names
            ):
                violations.append(path)
            if (
                isinstance(node, ast.ImportFrom)
                and node.level == 0
                and node.module
                and (node.module == "pydantic" or node.module.startswith("pydantic."))
            ):
                violations.append(path)
    assert not violations
