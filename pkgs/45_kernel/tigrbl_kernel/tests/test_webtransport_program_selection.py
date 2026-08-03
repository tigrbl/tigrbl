from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tigrbl_core._spec.binding_spec import (
    BinaryFramingSpec,
    JsonRpcFramingSpec,
    WebTransportBindingSpec,
)
from tigrbl_core._spec.op_spec import OpSpec
from tigrbl_kernel._compile import _compile_plan
from tigrbl_kernel.models import KernelPlan
from tigrbl_kernel.packed_selectors import resolve_webtransport_program


@dataclass
class AppFixture:
    tables: tuple[type, ...]


class CompilerFixture:
    def _build_ingress(self, app: Any) -> dict[str, list[Any]]:
        return {}

    def _build_egress(self, app: Any) -> dict[str, list[Any]]:
        return {}

    def _build_op(self, model: type, alias: str) -> dict[str, list[Any]]:
        return {}

    def get_specs(self, model: type) -> dict[str, Any]:
        return {}

    def _compile_opview_from_specs(self, specs: Any, sp: Any) -> None:
        return None

    def _pack_kernel_plan(self, semantic: KernelPlan, **_: Any) -> object:
        return object()


class PresentationOps:
    __tigrbl_ops__ = (
        OpSpec(
            alias="hello",
            target="custom",
            bindings=(
                WebTransportBindingSpec(
                    path="/r/{room_id_hash}",
                    profile="bidi_stream",
                    inner_framing=JsonRpcFramingSpec(),
                    rpc_method="Session.hello",
                ),
            ),
        ),
        OpSpec(
            alias="join",
            target="custom",
            bindings=(
                WebTransportBindingSpec(
                    path="/r/{room_id_hash}",
                    profile="bidi_stream",
                    inner_framing=JsonRpcFramingSpec(),
                    rpc_method="Presentation.join",
                ),
            ),
        ),
        OpSpec(
            alias="relay",
            target="custom",
            bindings=(
                WebTransportBindingSpec(
                    path="/r/{room_id_hash}",
                    profile="unidi_client_stream",
                    inner_framing=BinaryFramingSpec(),
                ),
            ),
        ),
        OpSpec(
            alias="heartbeat",
            target="custom",
            bindings=(
                WebTransportBindingSpec(
                    path="/r/{room_id_hash}",
                    profile="datagram",
                    inner_framing=JsonRpcFramingSpec(),
                ),
            ),
        ),
    )


def _plan() -> KernelPlan:
    return _compile_plan(CompilerFixture(), AppFixture((PresentationOps,)))


def test_webtransport_control_dispatches_by_rpc_method_on_shared_path() -> None:
    plan = _plan()
    hello = resolve_webtransport_program(
        plan,
        path="/r/alpha",
        message={
            "type": "webtransport.stream.receive",
            "stream_direction": "bidi",
            "data": (
                b'{"jsonrpc":"2.0","id":1,"method":"Session.hello",'
                b'"params":{"display_name":"Ada"}}'
            ),
        },
    )
    joined = resolve_webtransport_program(
        plan,
        path="/r/alpha",
        message={
            "type": "webtransport.stream.receive",
            "stream_direction": "bidi",
            "data": (
                b'{"jsonrpc":"2.0","id":2,"method":"Presentation.join",'
                b'"params":{"presentation_id":"alpha"}}'
            ),
        },
    )

    assert hello.program_id == 0
    assert joined.program_id == 1
    assert hello.path_params == {"room_id_hash": "alpha"}
    assert hello.rpc_envelope["id"] == 1


def test_webtransport_dispatches_media_and_datagram_by_lane() -> None:
    plan = _plan()
    media = resolve_webtransport_program(
        plan,
        path="/r/alpha",
        message={
            "type": "webtransport.stream.receive",
            "stream_direction": "client_to_server",
            "data": b"media",
        },
    )
    datagram = resolve_webtransport_program(
        plan,
        path="/r/alpha",
        message={"type": "webtransport.datagram.receive", "data": b"{}"},
    )

    assert media.program_id == 2
    assert media.lane == "unidi_client_stream"
    assert datagram.program_id == 3
    assert datagram.lane == "datagram"


def test_webtransport_lifecycle_and_unknown_method_do_not_fall_through() -> None:
    plan = _plan()
    disconnect = resolve_webtransport_program(
        plan,
        path="/r/alpha",
        message={"type": "webtransport.disconnect"},
    )
    unknown = resolve_webtransport_program(
        plan,
        path="/r/alpha",
        message={
            "type": "webtransport.stream.receive",
            "stream_direction": "bidi",
            "data": b'{"jsonrpc":"2.0","id":3,"method":"Nope"}',
        },
    )

    assert disconnect.program_id == -1
    assert disconnect.disposition == "lifecycle"
    assert unknown.program_id == -1
    assert unknown.disposition == "method_not_found"
