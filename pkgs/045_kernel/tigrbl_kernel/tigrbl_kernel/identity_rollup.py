"""Read models for identity-bearing runtime records."""

from collections.abc import Iterable, Mapping
from typing import Any


def rollup_identity_records(records: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Group session records while counting logical subscriptions and actual DB transactions."""
    connections: dict[str, set[str]] = {}
    deliveries: dict[str, dict[str, Any]] = {}
    sessions: dict[str, dict[str, Any]] = {}
    transactions: dict[tuple[str, str], dict[str, Any]] = {}
    subscriptions: dict[str, set[str]] = {}
    for record in records:
        correlation = record.get("correlation_id")
        carrier = record.get("transport_session_id")
        if correlation and carrier:
            if connection := record.get("connection_id"):
                connections.setdefault(connection, set()).add(correlation)
            session = sessions.setdefault(correlation, {"streams": {}, "datagrams": set()})
            stream = record.get("stream_correlation_id")
            if stream:
                invocations = session["streams"].setdefault(stream, set())
                if invocation := record.get("invocation_id"):
                    invocations.add(invocation)
            if datagram := record.get("datagram_id"):
                session["datagrams"].add(datagram)
        engine, transaction = record.get("engine_session_id"), record.get("transaction_id")
        if engine and transaction:
            group = transactions.setdefault((engine, transaction), {"invocations": set(), "outcomes": set()})
            if invocation := record.get("invocation_id"):
                group["invocations"].add(invocation)
            if outcome := record.get("outcome"):
                group["outcomes"].add(outcome)
        if subscription := record.get("subscription_id"):
            destinations = subscriptions.setdefault(subscription, set())
            if carrier:
                destinations.add(carrier)
        if delivery := record.get("delivery_id"):
            deliveries[delivery] = {
                key: record[key] for key in (
                    "publication_id", "subscription_id", "transport_session_id",
                    "origin_invocation_id", "correlation_id", "outcome",
                ) if key in record
            }
    return {
        "connections": {key: sorted(items) for key, items in sorted(connections.items())},
        "deliveries": dict(sorted(deliveries.items())),
        "sessions": {
            key: {"streams": {stream: sorted(items) for stream, items in sorted(value["streams"].items())},
                  "datagrams": sorted(value["datagrams"], key=str)}
            for key, value in sorted(sessions.items())
        },
        "transactions": [
            {"engine_session_id": engine, "transaction_id": transaction,
             "invocations": sorted(value["invocations"]), "outcomes": sorted(value["outcomes"])}
            for (engine, transaction), value in sorted(transactions.items())
        ],
        "subscriptions": {key: sorted(destinations) for key, destinations in sorted(subscriptions.items())},
    }
