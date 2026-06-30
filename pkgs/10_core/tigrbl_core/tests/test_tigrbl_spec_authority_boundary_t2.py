from __future__ import annotations

from pathlib import Path

import tigrbl_spec
from tigrbl_core import schema as core_schema


ROOT = Path(__file__).resolve().parents[4]


def test_tigrbl_core_schema_api_consumes_tigrbl_spec_authority() -> None:
    assert core_schema.build_spec_json_schema_bundle()["authority"] == "tigrbl_spec"
    assert core_schema.build_individual_spec_json_schemas()["AppSpec"] == tigrbl_spec.load_schema(
        "AppSpec"
    )


def test_tigrbl_core_does_not_package_a_competing_schema_catalog() -> None:
    pyproject = (ROOT / "pkgs/10_core/tigrbl_core/pyproject.toml").read_text(encoding="utf-8")

    assert "tigrbl_core/schemas" not in pyproject
    assert "tigrbl_spec\" = { workspace = true }" in pyproject
