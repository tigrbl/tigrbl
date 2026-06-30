from __future__ import annotations

import pytest

from tigrbl_core._spec import (
    HttpJsonRpcBindingSpec,
    HttpRestBindingSpec,
    HttpStreamBindingSpec,
    JsonRpcFramingSpec,
    NdjsonFramingSpec,
    OpSpec,
    PathSpec,
    TextFramingSpec,
    WellKnownResourceSpec,
    WsBindingSpec,
    validate_path_binding,
)


def _op(alias: str, *bindings: object) -> OpSpec:
    return OpSpec(alias=alias, target="custom", bindings=tuple(bindings))


@pytest.mark.parametrize("field", ("engine", "engine_name"))
def test_pathspec_from_dict_rejects_engine_ownership_fields(field: str) -> None:
    with pytest.raises(ValueError, match=f"PathSpec does not own engines.*{field}"):
        PathSpec.from_dict({"path": "/items", field: "primary"})


def test_pathspec_rejects_unknown_kind_with_actionable_diagnostic() -> None:
    with pytest.raises(ValueError, match="PathSpec.kind.*not-a-kind"):
        PathSpec(path="/items", kind="not-a-kind")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("path", "binding", "message"),
    (
        (
            PathSpec(path="/items", kind="resource"),
            HttpStreamBindingSpec(proto="http.stream", path="/items"),
            "stream",
        ),
        (
            PathSpec(path="/rpc", kind="jsonrpc"),
            WsBindingSpec(proto="ws", path="/rpc", framing=JsonRpcFramingSpec()),
            "ws-jsonrpc",
        ),
        (
            PathSpec(path="/events", kind="stream"),
            WsBindingSpec(proto="ws", path="/events", framing=TextFramingSpec()),
            "websocket",
        ),
        (
            PathSpec(path="/ws", kind="ws-jsonrpc"),
            HttpJsonRpcBindingSpec(proto="http.jsonrpc", rpc_method="Item.list"),
            "jsonrpc",
        ),
    ),
)
def test_pathspec_binding_mismatch_fails_closed(
    path: PathSpec,
    binding: object,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        validate_path_binding(path, binding)  # type: ignore[arg-type]


def test_pathspec_binding_path_conflicts_fail_closed() -> None:
    path = PathSpec(path="/items", kind="resource")

    with pytest.raises(ValueError, match="path conflicts"):
        validate_path_binding(
            path,
            HttpRestBindingSpec(proto="http.rest", methods=("GET",), path="/other"),
        )


def test_pathspec_round_trip_preserves_kind_path_ops_and_binding_metadata() -> None:
    path = PathSpec(
        path="/items/tail",
        kind="stream",
        ops=(
            _op(
                "tail",
                HttpStreamBindingSpec(
                    proto="https.stream",
                    path="/items/tail",
                    methods=("GET",),
                    framing=NdjsonFramingSpec(),
                ),
            ),
        ),
    )

    restored = PathSpec.from_dict(path.to_dict())
    binding = restored.ops[0].bindings[0]

    assert restored.path == "/items/tail"
    assert restored.kind == "stream"
    assert restored.ops[0].alias == "tail"
    assert isinstance(binding, HttpStreamBindingSpec)
    assert binding.proto == "https.stream"
    assert isinstance(binding.framing, NdjsonFramingSpec)


def test_pathspec_well_known_kind_requires_spec_payload_and_round_trips() -> None:
    path = PathSpec(
        path="/.well-known/openid-configuration",
        kind="well-known",
        well_known=WellKnownResourceSpec(
            name="openid-configuration",
            payload={"issuer": "https://issuer.example"},
        ),
    )

    restored = PathSpec.from_dict(path.to_dict())

    assert restored == path


def test_pathspec_well_known_rejects_non_well_known_payload() -> None:
    with pytest.raises(TypeError, match="PathSpec.well_known"):
        PathSpec(
            path="/.well-known/openid-configuration",
            kind="well-known",
            well_known={"name": "openid-configuration"},  # type: ignore[arg-type]
        )
