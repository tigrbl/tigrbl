from __future__ import annotations

from importlib.metadata import version

import pytest
import tigrbl_typing.types as typing_types
from tigrbl_concrete import Column, acol, makeColumn, makeVirtualColumn, vcol


_DEPRECATED_NAMES = {"Column", "Mapped", "mapped_column"}
_REMOVAL_MINOR = (0, 7)


def _major_minor(value: str) -> tuple[int, int]:
    release = value.split("+", 1)[0].split(".dev", 1)[0]
    major, minor, *_ = release.split(".")
    return int(major), int(minor)


@pytest.mark.i9n
def test_typing_column_exports_warn_with_actionable_migration_guidance():
    if _major_minor(version("tigrbl-typing")) >= _REMOVAL_MINOR:
        pytest.skip("deprecated exports have reached their enforced removal version")

    for name in _DEPRECATED_NAMES:
        namespace: dict[str, object] = {}
        with pytest.warns(DeprecationWarning) as caught:
            exec(f"from tigrbl_typing.types import {name}", namespace)

        message = str(caught[0].message)
        assert "tigrbl-typing 0.7" in message
        assert "tigrbl_concrete" in message
        assert "makeColumn" in message
        assert "acol" in message
        assert "sqlalchemy.orm" in message
        assert name in namespace


@pytest.mark.i9n
def test_typing_column_exports_are_hard_gated_by_third_next_minor(monkeypatch):
    assert typing_types.DEPRECATED_EXPORTS_CUTOFF == _REMOVAL_MINOR
    assert typing_types._deprecated_export_names_for((0, 6)) == [
        "Column",
        "Mapped",
        "mapped_column",
    ]
    assert typing_types._deprecated_export_names_for(_REMOVAL_MINOR) == []

    monkeypatch.setattr(typing_types, "_CURRENT_MAJOR_MINOR", _REMOVAL_MINOR)
    for name in _DEPRECATED_NAMES:
        with pytest.raises(AttributeError, match="no longer exported"):
            getattr(typing_types, name)


@pytest.mark.i9n
def test_installed_version_obeys_typing_column_export_gate():
    current = _major_minor(version("tigrbl-typing"))
    expected = _DEPRECATED_NAMES if current < _REMOVAL_MINOR else set()
    assert _DEPRECATED_NAMES.intersection(typing_types.__all__) == expected


@pytest.mark.i9n
def test_tigrbl_concrete_exposes_supported_column_migration_targets():
    assert callable(Column)
    assert makeColumn is acol
    assert makeVirtualColumn is vcol
