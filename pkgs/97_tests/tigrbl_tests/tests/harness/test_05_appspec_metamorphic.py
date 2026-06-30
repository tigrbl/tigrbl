from __future__ import annotations

from collections.abc import Iterable

import pytest
from sqlalchemy import Column, String

from tigrbl import TableBase, TigrblApp
from tigrbl._spec import AppSpec, HttpJsonRpcBindingSpec, HttpRestBindingSpec, OpSpec
from tigrbl.factories.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl_tests.tests.fixtures.appspec_corpus_loader import (
    load_corpus,
    validate_corpus,
)


def _make_widget_model(
    *,
    class_name: str,
    tablename: str,
    resource: str,
    binding_order: Iterable[str] = ("rest", "jsonrpc"),
) -> type:
    bindings_by_kind = {
        "rest": HttpRestBindingSpec(
            proto="http.rest",
            path=f"/{resource}",
            methods=("POST",),
        ),
        "jsonrpc": HttpJsonRpcBindingSpec(
            proto="http.jsonrpc",
            rpc_method=f"{class_name}.create",
        ),
    }

    attrs = {
        "__tablename__": tablename,
        "__resource__": resource,
        "__allow_unmapped__": True,
        "name": Column(String, nullable=False),
    }
    widget = type(class_name, (TableBase, GUIDPk), attrs)
    widget.__tigrbl_ops__ = (
        OpSpec(
            alias="create",
            target="create",
            bindings=tuple(bindings_by_kind[kind] for kind in binding_order),
        ),
    )
    return widget


def _materialize_app(
    *,
    case: dict,
    tables: tuple[type, ...],
    title: str | None = None,
    version: str | None = None,
) -> TigrblApp:
    spec = AppSpec(
        title=title or case["app"]["title"],
        version=version or case["app"]["version"],
        engine=mem(async_=False),
        tables=tables,
        jsonrpc_prefix=case["app"]["jsonrpc_prefix"],
        system_prefix=case["app"]["system_prefix"],
    )
    return TigrblApp.from_spec(spec)


def _route_signature(app: TigrblApp) -> frozenset[tuple[str, tuple[str, ...]]]:
    signature: set[tuple[str, tuple[str, ...]]] = set()
    for route in getattr(app, "routes", ()):
        path = getattr(route, "path", None)
        if not isinstance(path, str):
            continue
        methods = tuple(sorted(getattr(route, "methods", ()) or ()))
        signature.add((path, methods))
    return frozenset(signature)


@pytest.mark.acceptance
def test_appspec_metadata_transform_preserves_route_surface() -> None:
    corpus = load_corpus("appspec_corpus.canonical.json")
    validate_corpus(corpus, lane="canonical")
    case = corpus["cases"][0]

    widget = _make_widget_model(
        class_name="MetamorphicWidget",
        tablename=f"{case['table']['tablename']}_metadata",
        resource=case["table"]["resource"],
    )
    baseline = _materialize_app(case=case, tables=(widget,))
    transformed = _materialize_app(
        case=case,
        tables=(widget,),
        title=f"{case['app']['title']} Transformed",
        version="9.9.9",
    )

    assert getattr(transformed, "title", None) != getattr(baseline, "title", None)
    assert _route_signature(transformed) == _route_signature(baseline)


@pytest.mark.acceptance
def test_appspec_binding_order_transform_preserves_route_surface() -> None:
    corpus = load_corpus("appspec_corpus.canonical.json")
    validate_corpus(corpus, lane="canonical")
    case = corpus["cases"][0]

    rest_first = _make_widget_model(
        class_name="MetamorphicBindingRestFirst",
        tablename=f"{case['table']['tablename']}_rest_first",
        resource=case["table"]["resource"],
        binding_order=("rest", "jsonrpc"),
    )
    rpc_first = _make_widget_model(
        class_name="MetamorphicBindingRpcFirst",
        tablename=f"{case['table']['tablename']}_rpc_first",
        resource=case["table"]["resource"],
        binding_order=("jsonrpc", "rest"),
    )

    baseline = _materialize_app(case=case, tables=(rest_first,))
    transformed = _materialize_app(case=case, tables=(rpc_first,))

    assert _route_signature(transformed) == _route_signature(baseline)


@pytest.mark.acceptance
def test_appspec_table_order_transform_preserves_route_surface() -> None:
    corpus = load_corpus("appspec_corpus.canonical.json")
    validate_corpus(corpus, lane="canonical")
    case = corpus["cases"][0]

    alpha = _make_widget_model(
        class_name="MetamorphicAlphaWidget",
        tablename=f"{case['table']['tablename']}_alpha",
        resource="alpha-widget",
    )
    beta = _make_widget_model(
        class_name="MetamorphicBetaWidget",
        tablename=f"{case['table']['tablename']}_beta",
        resource="beta-widget",
    )

    baseline = _materialize_app(case=case, tables=(alpha, beta))
    transformed = _materialize_app(case=case, tables=(beta, alpha))

    assert _route_signature(transformed) == _route_signature(baseline)
