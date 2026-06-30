from __future__ import annotations

import pytest

from tigrbl_atoms.client_session_coverage import (
    BEHAVIOR_GROUP_VALUES,
    CLIENT_TOPOLOGY_VALUES,
    DISPOSITION_VALUES,
    GOVERNED_IDENTIFIER_FIELDS,
    INTERNAL_ONLY_FIELDS,
    SESSION_SCOPE_VALUES,
    ClientTopology,
    CoverageDisposition,
    SessionScope,
    build_matrix_row,
    classify_transport_session_scope,
    validate_governed_identifier_fields,
    validate_matrix_row,
)


def test_client_session_vocabulary_is_stable() -> None:
    assert CLIENT_TOPOLOGY_VALUES == {
        "single_client_single_session",
        "single_client_multi_session",
        "sequential_clients",
        "bounded_interleaved_clients",
        "concurrent_clients",
        "churn_clients",
    }
    assert SESSION_SCOPE_VALUES == {
        "request_scoped",
        "stream_scoped",
        "connection_scoped",
        "transport_session_scoped",
    }
    assert BEHAVIOR_GROUP_VALUES == {
        "lifecycle",
        "identity",
        "isolation",
        "ordering",
        "pressure",
        "fault",
        "cleanup",
    }
    assert DISPOSITION_VALUES == {
        "covered",
        "required",
        "planned",
        "not_applicable",
        "fail_closed",
    }


@pytest.mark.parametrize(
    ("transport_scenario", "expected_scope"),
    [
        ("HTTP REST", SessionScope.REQUEST_SCOPED),
        ("HTTPS REST", SessionScope.REQUEST_SCOPED),
        ("HTTP JSON-RPC", SessionScope.REQUEST_SCOPED),
        ("HTTPS JSON-RPC", SessionScope.REQUEST_SCOPED),
        ("http.rest", SessionScope.REQUEST_SCOPED),
        ("http.jsonrpc", SessionScope.REQUEST_SCOPED),
        ("HTTP stream", SessionScope.STREAM_SCOPED),
        ("HTTPS stream", SessionScope.STREAM_SCOPED),
        ("HTTP SSE", SessionScope.STREAM_SCOPED),
        ("HTTPS SSE", SessionScope.STREAM_SCOPED),
        ("WS text", SessionScope.CONNECTION_SCOPED),
        ("WSS text", SessionScope.CONNECTION_SCOPED),
        ("WS binary", SessionScope.CONNECTION_SCOPED),
        ("WSS binary", SessionScope.CONNECTION_SCOPED),
        ("WS JSON-RPC", SessionScope.CONNECTION_SCOPED),
        ("WSS JSON-RPC", SessionScope.CONNECTION_SCOPED),
        ("WS NDJSON", SessionScope.CONNECTION_SCOPED),
        ("WSS NDJSON", SessionScope.CONNECTION_SCOPED),
        ("WebTransport", SessionScope.TRANSPORT_SESSION_SCOPED),
    ],
)
def test_transport_rows_have_default_client_session_scope(
    transport_scenario: str,
    expected_scope: SessionScope,
) -> None:
    assert classify_transport_session_scope(transport_scenario) is expected_scope


@pytest.mark.parametrize(
    "transport_scenario",
    ["Docs payload", "Docs UIX", "Static files", "Nested app mount"],
)
def test_non_session_transport_rows_are_not_applicable(
    transport_scenario: str,
) -> None:
    assert classify_transport_session_scope(transport_scenario) is None


def test_matrix_row_validation_accepts_stream_and_datagram_identifiers() -> None:
    row = build_matrix_row(
        transport_scenario="WebTransport",
        client_topology=ClientTopology.SINGLE_CLIENT_SINGLE_SESSION,
        disposition=CoverageDisposition.COVERED,
        lifecycle_behavior=CoverageDisposition.COVERED,
        isolation_property=CoverageDisposition.COVERED,
        pressure_mode=CoverageDisposition.REQUIRED,
        fault_mode=CoverageDisposition.REQUIRED,
        client_id="client-a",
        session_id="wt-session-a",
        stream_id=7,
        datagram_id=11,
    )

    validate_matrix_row(row)
    assert {"stream_id", "datagram_id"}.issubset(row)
    assert {"stream_id", "datagram_id"}.issubset(GOVERNED_IDENTIFIER_FIELDS)


def test_governed_identifier_validation_rejects_lane() -> None:
    assert "lane" in INTERNAL_ONLY_FIELDS
    with pytest.raises(ValueError, match="lane"):
        validate_governed_identifier_fields(
            {
                "client_id": "client-a",
                "session_id": "session-a",
                "lane": "bidi_stream",
            }
        )


def test_matrix_row_validation_requires_all_axes() -> None:
    with pytest.raises(ValueError, match="missing axes"):
        validate_matrix_row(
            {
                "transport_scenario": "HTTP REST",
                "client_topology": "single_client_single_session",
                "session_scope": "request_scoped",
                "disposition": "covered",
            }
        )
