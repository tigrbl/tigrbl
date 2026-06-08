from __future__ import annotations

import pytest

from tigrbl_base._base import CrudTableBase, RealtimeTableBase, TableBase
from tigrbl_core._spec.op_spec import OpSpec
from tigrbl_core._spec.table_profile_spec import (
    PLAIN_TABLE_PROFILE,
    REALTIME_TABLE_PROFILE,
    TableProfileError,
    TableProfileSpec,
)


def test_tablebase_declares_plain_table_profile() -> None:
    assert TableBase.TABLE_PROFILE == PLAIN_TABLE_PROFILE


def test_abstract_table_presets_inherit_from_tablebase() -> None:
    assert issubclass(CrudTableBase, TableBase)
    assert issubclass(RealtimeTableBase, TableBase)
    assert CrudTableBase.TABLE_PROFILE.role == "abstract"
    assert RealtimeTableBase.TABLE_PROFILE == REALTIME_TABLE_PROFILE


def test_explicit_table_profile_conflicts_with_default_canon_verbs() -> None:
    with pytest.raises(TableProfileError, match="legacy table default authority"):

        class Bad(TableBase):
            __abstract__ = True
            TABLE_PROFILE = PLAIN_TABLE_PROFILE
            DEFAULT_CANON_VERBS = {"read"}


def test_explicit_table_profile_conflicts_with_declared_ops_attr() -> None:
    with pytest.raises(TableProfileError, match="legacy table default authority"):

        class Bad(TableBase):
            __abstract__ = True
            TABLE_PROFILE = PLAIN_TABLE_PROFILE
            __tigrbl_ops__ = (OpSpec(alias="read", target="read"),)


def test_explicit_table_profile_conflicts_with_binding_profile_config() -> None:
    with pytest.raises(TableProfileError, match="table_config.binding_profiles"):

        class Bad(TableBase):
            __abstract__ = True
            TABLE_PROFILE = PLAIN_TABLE_PROFILE
            table_config = {"binding_profiles": ("rest",)}


def test_single_op_profile_means_exactly_one_op() -> None:
    class SingleRead(TableBase):
        __abstract__ = True
        TABLE_PROFILE = TableProfileSpec(
            kind="test.single_read",
            role="concrete",
            ops=(OpSpec(alias="read", target="read"),),
            custom=True,
            namespace="test",
        )

    assert tuple(op.target for op in SingleRead.TABLE_PROFILE.ops) == ("read",)
