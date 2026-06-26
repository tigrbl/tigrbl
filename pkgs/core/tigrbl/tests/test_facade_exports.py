from __future__ import annotations

from pathlib import Path

import tigrbl
from tigrbl_core._spec.headers_spec import HeadersSpec

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10
    import tomli as tomllib


PACKAGE_ROOT = Path(__file__).resolve().parents[1]


def test_public_facade_depends_on_core_package() -> None:
    pyproject = tomllib.loads(
        (PACKAGE_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    )
    dependencies = pyproject["project"]["dependencies"]

    assert "tigrbl-core" in dependencies


def test_public_facade_reexports_headers_spec_from_core() -> None:
    assert tigrbl.HeadersSpec is HeadersSpec
    assert "HeadersSpec" in tigrbl.__all__
