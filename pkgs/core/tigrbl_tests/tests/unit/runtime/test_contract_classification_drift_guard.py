from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from tigrbl_kernel.contract_classification import (
    CANONICAL_CONTRACT_EVENTS,
    CONTRACT_BINDING_ALIASES,
    project_contract_classification,
)


def _contract_rows() -> list[dict[str, object]]:
    current = Path(__file__).resolve()
    for parent in current.parents:
        candidate = parent.parent / "tigr-asgi-contracts" / "contract" / "event_classification.yaml"
        if candidate.exists():
            payload = yaml.safe_load(candidate.read_text(encoding="utf-8"))
            return list(payload["event_classifications"])
    pytest.fail("tigr-asgi-contracts contract/event_classification.yaml was not found")


def test_all_supported_tigr_asgi_contract_rows_project_without_custom_event_names() -> None:
    rows = _contract_rows()
    supported = [row for row in rows if row.get("scope_type") != "lifespan"]

    assert supported
    for row in supported:
        projection = project_contract_classification(row)

        assert projection.event == row["event"]
        assert projection.event in CANONICAL_CONTRACT_EVENTS
        assert projection.local_binding_kinds == CONTRACT_BINDING_ALIASES[projection.binding]
        assert projection.local_exchange in {
            "request_response",
            "client_stream",
            "server_stream",
            "bidirectional_stream",
            "fire_and_forget",
        }
        assert "subsurface" not in row


def test_unsupported_contract_rows_fail_closed_instead_of_normalizing() -> None:
    rows = _contract_rows()
    lifespan_rows = [row for row in rows if row.get("scope_type") == "lifespan"]

    assert lifespan_rows
    for row in lifespan_rows:
        with pytest.raises(ValueError):
            project_contract_classification(row)


@pytest.mark.parametrize(
    "row",
    (
        {
            "event": "webtransport.message.receive",
            "channel": "receive",
            "scope_type": "webtransport",
            "binding": "webtransport",
            "family": "message",
            "exchange": "duplex",
            "direction": "client_to_server",
        },
        {
            "event": "webtransport.stream.receive",
            "channel": "receive",
            "scope_type": "webtransport",
            "binding": "webtransport",
            "family": "stream",
            "exchange": "duplex",
            "direction": "client_to_server",
            "subsurface": "webtransport.bidi_stream",
        },
        {
            "event": "http.request",
            "channel": "sideband",
            "scope_type": "http",
            "binding": "rest",
            "family": "request",
            "exchange": "unary",
            "direction": "client_to_server",
        },
        {
            "event": "http.request",
            "channel": "receive",
            "scope_type": "websocket",
            "binding": "rest",
            "family": "request",
            "exchange": "unary",
            "direction": "client_to_server",
        },
    ),
)
def test_contract_classification_drift_negative_corpus(row: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        project_contract_classification(row)
