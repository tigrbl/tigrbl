"""Counts over projected trace timeline events."""

from collections import Counter

from .projection import BAD_OUTCOMES, PROTOCOLS


def summarize(events):
    concepts = {
        "connections": "connection_id",
        "transport_sessions": "transport_session_id",
        "invocations": "invocation_id",
        "subscriptions": "subscription_id",
        "publications": "publication_id",
        "deliveries": "delivery_id",
    }

    def distinct(rows, key):
        return len({row[key] for row in rows if key in row})

    def count_for(protocol):
        rows = [row for row in events if row["transport"] == protocol]
        return {
            "events": len(rows),
            "connections": distinct(rows, "connection_id"),
            "sessions": distinct(rows, "transport_session_id"),
            "invocations": distinct(rows, "invocation_id"),
            "errors": Counter(row["outcome"] in BAD_OUTCOMES for row in rows)[True],
        }

    transactions = {
        (row["engine_session_id"], row["transaction_id"])
        for row in events
        if "engine_session_id" in row and "transaction_id" in row
    }
    return {
        **{name: distinct(events, key) for name, key in concepts.items()},
        "transactions": len(transactions),
        "by_protocol": {protocol: count_for(protocol) for protocol in PROTOCOLS},
    }
