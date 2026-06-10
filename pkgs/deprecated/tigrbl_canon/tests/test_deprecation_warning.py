from __future__ import annotations

import importlib
from pathlib import Path
import sys
import warnings

import pytest

PACKAGE_DIR = Path(__file__).resolve().parents[1] / "tigrbl_canon"


def _clear_tigrbl_canon_modules() -> None:
    to_remove = [
        name
        for name in sys.modules
        if name == "tigrbl_canon" or name.startswith("tigrbl_canon.")
    ]
    for name in to_remove:
        sys.modules.pop(name, None)


def _module_name_for(module_file: Path) -> str:
    relative = module_file.relative_to(PACKAGE_DIR).with_suffix("")
    parts = ("tigrbl_canon", *relative.parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _parent_modules(module_name: str) -> list[str]:
    parts = module_name.split(".")
    return [".".join(parts[:index]) for index in range(1, len(parts))]


def test_import_tigrbl_canon_emits_deprecation_warning() -> None:
    _clear_tigrbl_canon_modules()

    with pytest.deprecated_call(match="tigrbl_canon is deprecated"):
        importlib.import_module("tigrbl_canon")


def test_import_tigrbl_canon_mapping_emits_deprecation_warning() -> None:
    _clear_tigrbl_canon_modules()

    with pytest.deprecated_call(match="tigrbl_canon is deprecated"):
        importlib.import_module("tigrbl_canon.mapping")


@pytest.mark.parametrize(
    "module_name",
    sorted(_module_name_for(module_file) for module_file in PACKAGE_DIR.rglob("*.py")),
)
def test_each_tigrbl_canon_module_import_emits_deprecation_warning(
    module_name: str,
) -> None:
    _clear_tigrbl_canon_modules()

    for parent in _parent_modules(module_name):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            importlib.import_module(parent)

    sys.modules.pop(module_name, None)

    with pytest.deprecated_call(match="tigrbl_canon is deprecated"):
        importlib.import_module(module_name)
