from __future__ import annotations

import importlib

import pytest


def _require(module_name: str, attr_name: str):
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        pytest.xfail(f"{module_name} is not implemented")
    value = getattr(module, attr_name, None)
    if value is None:
        pytest.xfail(f"{module_name}.{attr_name} is not implemented")
    return value


def test_transport_event_registry_contains_required_transport_families() -> None:
    registry = _require("tigrbl_kernel.transport_events", "build_transport_event_registry")

    events = registry()
    families = {event["transport"] for event in events}

    assert {
        "http",
        "websocket",
        "webtransport",
        "static_file",
        "lifespan",
        "callback",
        "webhook",
    } <= families


def test_transport_event_rows_declare_direction_scope_mapping_and_requirement() -> None:
    registry = _require("tigrbl_kernel.transport_events", "build_transport_event_registry")

    row = next(event for event in registry() if event["event"] == "websocket.receive")

    assert row["direction"] == "inbound"
    assert row["required"] is True
    assert row["scope_type"] == "websocket"
    assert row["subevent"] == "message.received"
    assert row["extension_namespace"] in {"asgi", "tigrbl", None}


@pytest.mark.parametrize(
    ("transport", "required_events"),
    (
        ("http", {"http.request", "http.response.start", "http.response.body"}),
        ("websocket", {"websocket.connect", "websocket.receive", "websocket.send", "websocket.close"}),
        ("webtransport", {"webtransport.connect", "webtransport.datagram.receive", "webtransport.stream.receive", "webtransport.close"}),
        ("lifespan", {"lifespan.startup", "lifespan.shutdown"}),
        ("static_file", {"static_file.lookup", "static_file.emit"}),
    ),
)
def test_registry_declares_required_events_per_transport(
    transport: str,
    required_events: set[str],
) -> None:
    registry = _require("tigrbl_kernel.transport_events", "build_transport_event_registry")

    events = {event["event"] for event in registry() if event["transport"] == transport}

    assert required_events <= events


def test_transport_event_registry_rejects_duplicate_event_keys() -> None:
    validate = _require("tigrbl_kernel.transport_events", "validate_transport_event_registry")

    with pytest.raises(ValueError, match="duplicate|event|registry"):
        validate(
            [
                {"event": "websocket.receive", "transport": "websocket", "direction": "inbound", "scope_type": "websocket"},
                {"event": "websocket.receive", "transport": "websocket", "direction": "inbound", "scope_type": "websocket"},
            ]
        )


def test_transport_event_registry_rejects_unknown_transport_event_names() -> None:
    validate = _require("tigrbl_kernel.transport_events", "validate_transport_event_registry")

    with pytest.raises(ValueError, match="unknown|transport|event|registry"):
        validate(
            [
                {"event": "websocket.teleport", "transport": "websocket", "direction": "inbound", "scope_type": "websocket"},
            ]
        )


def test_transport_event_registry_rejects_invalid_direction_or_scope_mapping() -> None:
    validate = _require("tigrbl_kernel.transport_events", "validate_transport_event_registry")

    with pytest.raises(ValueError, match="direction|scope|mapping|transport"):
        validate(
            [
                {"event": "websocket.receive", "transport": "websocket", "direction": "sideways", "scope_type": "http"},
            ]
        )
