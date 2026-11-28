from __future__ import annotations

from copy import deepcopy

from sqlalchemy import Column, String
import pytest

from tigrbl import TableBase, TigrblApp
from tigrbl._spec import AppSpec, HttpJsonRpcBindingSpec, HttpRestBindingSpec, OpSpec
from tigrbl.factories.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl_tests.tests.fixtures.appspec_corpus_loader import load_corpus, validate_corpus


def _make_widget_model(*, tablename: str, resource: str, include_jsonrpc: bool) -> type:
    class Widget(TableBase, GUIDPk):
        __tablename__ = tablename
        __resource__ = resource
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

    bindings: list[object] = [
        HttpRestBindingSpec(proto="http.rest", path=f"/{resource}", methods=("POST",))
    ]
    if include_jsonrpc:
        bindings.append(
            HttpJsonRpcBindingSpec(proto="http.jsonrpc", rpc_method="Widget.create")
        )

    Widget.__tigrbl_ops__ = (
        OpSpec(alias="create", target="create", bindings=tuple(bindings)),
    )
    return Widget


@pytest.mark.acceptance
@pytest.mark.parametrize(
    ("filename", "lane"),
    [
        ("appspec_corpus.canonical.json", "canonical"),
        ("appspec_corpus.negative.json", "negative"),
    ],
)
def test_appspec_corpus_fixture_schema_and_ids(filename: str, lane: str) -> None:
    corpus = load_corpus(filename)
    validate_corpus(corpus, lane=lane)


@pytest.mark.acceptance
def test_canonical_corpus_cases_have_unique_routes_tables_and_modes() -> None:
    corpus = load_corpus("appspec_corpus.canonical.json")
    validate_corpus(corpus, lane="canonical")

    case_ids = [case["id"] for case in corpus["cases"]]
    table_names = [case["table"]["tablename"] for case in corpus["cases"]]
    modes = [case["mode"] for case in corpus["cases"]]

    assert len(case_ids) == len(set(case_ids))
    assert len(table_names) == len(set(table_names))
    assert set(modes) == {"rest_rpc_parity", "rest_rpc_roundtrip"}


@pytest.mark.acceptance
def test_canonical_corpus_compilation_is_deterministic() -> None:
    corpus = load_corpus("appspec_corpus.canonical.json")
    validate_corpus(corpus, lane="canonical")
    case = corpus["cases"][0]

    def compile_signature() -> tuple[str, str, tuple[str | None, ...]]:
        widget = _make_widget_model(
            tablename=case["table"]["tablename"],
            resource=case["table"]["resource"],
            include_jsonrpc=True,
        )
        spec = AppSpec(
            title=case["app"]["title"],
            version=case["app"]["version"],
            engine=mem(async_=False),
            tables=(widget,),
            jsonrpc_prefix=case["app"]["jsonrpc_prefix"],
            system_prefix=case["app"]["system_prefix"],
        )
        app = TigrblApp.from_spec(spec)
        paths = tuple(sorted(getattr(route, "path", None) for route in app.routes))
        return app.title, app.version, paths

    assert compile_signature() == compile_signature()


@pytest.mark.acceptance
def test_negative_corpus_rejects_duplicate_case_ids() -> None:
    corpus = load_corpus("appspec_corpus.negative.json")
    duplicate = deepcopy(corpus)
    duplicate["cases"][1]["id"] = duplicate["cases"][0]["id"]

    with pytest.raises(ValueError, match="duplicate case id"):
        validate_corpus(duplicate, lane="negative")


@pytest.mark.acceptance
def test_canonical_corpus_materializes_rpc_mounts() -> None:
    corpus = load_corpus("appspec_corpus.canonical.json")
    validate_corpus(corpus, lane="canonical")

    for case in corpus["cases"]:
        widget = _make_widget_model(
            tablename=case["table"]["tablename"],
            resource=case["table"]["resource"],
            include_jsonrpc=True,
        )
        spec = AppSpec(
            title=case["app"]["title"],
            version=case["app"]["version"],
            engine=mem(async_=False),
            tables=(widget,),
            jsonrpc_prefix=case["app"]["jsonrpc_prefix"],
            system_prefix=case["app"]["system_prefix"],
        )
        app = TigrblApp.from_spec(spec)

        paths = {getattr(route, "path", None) for route in getattr(app, "routes", ())}
        rpc_prefix = case["app"]["jsonrpc_prefix"]

        assert isinstance(app, TigrblApp)
        assert getattr(app, "title", None) == case["app"]["title"]
        assert getattr(app, "version", None) == case["app"]["version"]
        assert rpc_prefix in paths or f"{rpc_prefix}/" in paths


@pytest.mark.acceptance
def test_negative_corpus_fail_closed_no_rpc_mount() -> None:
    corpus = load_corpus("appspec_corpus.negative.json")
    validate_corpus(corpus, lane="negative")

    case = next(c for c in corpus["cases"] if c["mode"] == "no_rpc_binding_no_mount")
    widget = _make_widget_model(
        tablename=case["table"]["tablename"],
        resource=case["table"]["resource"],
        include_jsonrpc=False,
    )
    spec = AppSpec(
        title=case["app"]["title"],
        version=case["app"]["version"],
        engine=mem(async_=False),
        tables=(widget,),
        jsonrpc_prefix=case["app"]["jsonrpc_prefix"],
        system_prefix=case["app"]["system_prefix"],
    )
    app = TigrblApp.from_spec(spec)
    paths = {getattr(route, "path", None) for route in getattr(app, "routes", ())}
    rpc_prefix = case["app"]["jsonrpc_prefix"]

    assert rpc_prefix not in paths
    assert f"{rpc_prefix}/" not in paths
