from __future__ import annotations

import pytest

from tigrbl import CrudTable, RestTable, StreamTable
from tigrbl_core._spec import (
    HttpRestBindingSpec,
    OpSpec,
    TableProfileError,
    TableProfileSpec,
    TableSpec,
    get_table_profile,
)


def _spec(table: type) -> TableSpec:
    return TableSpec.collect(table)


def test_table_profile_axis_model_separates_concerns() -> None:
    rest_profile = get_table_profile("rest")
    abstract_spec = _spec(CrudTable)

    assert rest_profile.docs_exposure == "default"
    assert rest_profile.runtime_exposure == "default"
    assert tuple(op.target for op in rest_profile.ops) == (
        "create",
        "read",
        "update",
        "replace",
        "delete",
        "list",
        "clear",
    )
    assert abstract_spec.table_profile.role == "abstract"
    assert abstract_spec.table_profile.docs_exposure == "none"
    assert abstract_spec.table_profile.runtime_exposure == "none"
    assert all(not op.bindings for op in abstract_spec.ops)


def test_binding_profile_does_not_imply_ops_docs_or_network() -> None:
    profile = TableProfileSpec(
        kind="tests.binding-axis-only",
        ops=(),
        default_bindings=(HttpRestBindingSpec("http.rest", ("GET",), "/items"),),
        docs_exposure="none",
        runtime_exposure="none",
        custom=True,
        namespace="tests",
    )

    class BindingAxisOnly(RestTable):
        __abstract__ = True
        TABLE_PROFILE = profile

    collected = _spec(BindingAxisOnly)

    assert collected.ops == ()
    assert collected.table_profile.default_bindings == profile.default_bindings
    assert collected.table_profile.docs_exposure == "none"
    assert collected.table_profile.runtime_exposure == "none"


def test_default_bindings_do_not_override_per_op_bindings() -> None:
    explicit = _spec(StreamTable).ops[0].bindings[0]
    profile = TableProfileSpec(
        kind="tests.default-binding-precedence",
        ops=(OpSpec(alias="read", target="read", bindings=(explicit,)),),
        default_bindings=(
            HttpRestBindingSpec("http.rest", ("GET",), "/items/{item_id}"),
        ),
        custom=True,
        namespace="tests",
    )

    class ExplicitBinding(RestTable):
        __abstract__ = True
        TABLE_PROFILE = profile

    assert _spec(ExplicitBinding).ops[0].bindings == (explicit,)


def test_abstract_profile_cannot_declare_default_network_bindings() -> None:
    with pytest.raises(TableProfileError, match="abstract table profiles"):
        TableProfileSpec(
            kind="tests.abstract-with-bindings",
            role="abstract",
            ops=(OpSpec(alias="read", target="read"),),
            default_bindings=(HttpRestBindingSpec("http.rest", ("GET",), "/items"),),
            custom=True,
            namespace="tests",
        )


def test_builtin_profile_requires_authoritative_role() -> None:
    with pytest.raises(TableProfileError, match="requires role 'abstract'"):
        TableProfileSpec(kind="crud", role="concrete")
