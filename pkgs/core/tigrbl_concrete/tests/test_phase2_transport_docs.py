from __future__ import annotations

from types import SimpleNamespace

from tigrbl_concrete.system.docs.asyncapi import _build_asyncapi_spec
from tigrbl_core._spec.binding_spec import SseBindingSpec, WsBindingSpec
from tigrbl_core._spec.op_spec import OpSpec


class WidgetTable:
    ops = SimpleNamespace(
        all=(
            OpSpec(
                alias="watch_widgets",
                target="custom",
                exchange="event_stream",
                bindings=(
                    SseBindingSpec(
                        proto="http.sse",
                        path="/widgets/events",
                        methods=("GET",),
                    ),
                ),
            ),
            OpSpec(
                alias="widgets_socket",
                target="custom",
                exchange="bidirectional_stream",
                bindings=(
                    WsBindingSpec(
                        proto="wss",
                        path="/ws/widgets/{widget_id}",
                        framing="jsonrpc",
                    ),
                ),
            ),
        )
    )


def test_asyncapi_uses_declared_transport_bindings() -> None:
    router = SimpleNamespace(title="Demo", version="0.1.0", tables={"WidgetTable": WidgetTable})

    spec = _build_asyncapi_spec(router)

    assert "/widgets/events" in spec["channels"]
    assert spec["channels"]["/widgets/events"]["subscribe"]["operationId"] == "watch_widgets"
    ws_bindings = spec["channels"]["/ws/widgets/{widget_id}"]["receive"]["bindings"]["wss"]
    assert ws_bindings["framing"] == "jsonrpc"
    assert ws_bindings["exchange"] == "bidirectional_stream"
