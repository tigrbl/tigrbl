from __future__ import annotations

import tigrbl
import tigrbl_core._spec as spec


def test_public_facade_exports_governed_spec_contracts() -> None:
    expected = (
        "AppSpec",
        "RouterSpec",
        "TableSpec",
        "ColumnSpec",
        "FieldSpec",
        "IOSpec",
        "StorageSpec",
        "ForeignKeySpec",
        "OpSpec",
        "ResponseSpec",
    )

    for name in expected:
        assert getattr(tigrbl, name) is getattr(spec, name)
        assert name in tigrbl.__all__
        assert name in spec.__all__


def test_short_spec_aliases_resolve_to_canonical_contracts() -> None:
    assert spec.F is spec.FieldSpec
    assert spec.IO is spec.IOSpec
    assert spec.S is spec.StorageSpec
    assert tigrbl.FieldSpec is spec.F
    assert tigrbl.IOSpec is spec.IO
    assert tigrbl.StorageSpec is spec.S


def test_private_compat_import_surface_resolves_to_core_spec_package() -> None:
    import tigrbl._spec as legacy_spec

    assert legacy_spec.AppSpec is spec.AppSpec
    assert legacy_spec.RouterSpec is spec.RouterSpec
    assert legacy_spec.TableSpec is spec.TableSpec
