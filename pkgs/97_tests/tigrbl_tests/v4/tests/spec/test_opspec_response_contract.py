from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from tigrbl import OpSpec, ResponseSpec


def _dep(_ctx=None):
    return None


def test_opspec_preserves_alias_target_and_projection_flags() -> None:
    response = ResponseSpec(kind="json", status_code=201)
    op = OpSpec(
        alias="publish_book",
        target="custom",
        expose_routes=True,
        expose_rpc=False,
        expose_method=True,
        path_suffix="/publish",
        tags=("Books",),
        status_code=201,
        response=response,
    )

    assert op.alias == "publish_book"
    assert op.target == "custom"
    assert op.expose_routes is True
    assert op.expose_rpc is False
    assert op.path_suffix == "/publish"
    assert op.tags == ("Books",)
    assert op.response is response


def test_opspec_security_deps_and_secdeps_stay_synchronized() -> None:
    from_security = OpSpec(
        alias="secure_read",
        target="read",
        security_deps=(_dep,),
    )
    from_secdeps = OpSpec(
        alias="secure_list",
        target="list",
        secdeps=(_dep,),
    )

    assert from_security.secdeps == (_dep,)
    assert from_security.security_deps == (_dep,)
    assert from_secdeps.secdeps == (_dep,)
    assert from_secdeps.security_deps == (_dep,)


def test_opspec_preserves_ordinary_dependencies_and_transport_modes() -> None:
    op = OpSpec(
        alias="download_report",
        target="download",
        deps=(_dep,),
        http_methods=("GET",),
        arity="member",
        tx_scope="read_only",
        returns="model",
        extra={"audit": True},
    )

    assert op.deps == (_dep,)
    assert op.http_methods == ("GET",)
    assert op.arity == "member"
    assert op.tx_scope == "read_only"
    assert op.returns == "model"
    assert op.extra == {"audit": True}


def test_opspec_is_frozen_after_construction() -> None:
    op = OpSpec(alias="read", target="read")

    with pytest.raises(FrozenInstanceError):
        op.alias = "mutated"  # type: ignore[misc]


def test_response_spec_preserves_protocol_response_metadata() -> None:
    response = ResponseSpec(
        kind="json",
        media_type="application/vnd.tigrbl+json",
        status_code=202,
        headers={"X-Trace": "enabled"},
        envelope=True,
        cache_control="no-store",
    )

    assert response.kind == "json"
    assert response.media_type == "application/vnd.tigrbl+json"
    assert response.status_code == 202
    assert response.headers == {"X-Trace": "enabled"}
    assert response.envelope is True
    assert response.cache_control == "no-store"


def test_opspec_response_override_remains_distinct_from_default_response() -> None:
    default_response = ResponseSpec(kind="json", status_code=200)
    create_response = ResponseSpec(kind="json", status_code=201)
    op = OpSpec(alias="create", target="create", response=create_response)

    assert default_response.status_code == 200
    assert op.response is create_response
    assert op.response.status_code == 201
