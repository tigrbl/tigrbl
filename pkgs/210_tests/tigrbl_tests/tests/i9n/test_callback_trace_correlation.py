from types import SimpleNamespace

import pytest

from tigrbl import CallbackSpec
from tigrbl_concrete.callbacks import lower_callback


@pytest.mark.asyncio
async def test_callback_trace_separates_response_from_failed_outcome_write():
    events = []

    async def send(endpoint, body, headers, timeout):
        return {"status_code": 202, "body": "private result"}

    def broken_db():
        raise RuntimeError("private persistence error")

    spec = CallbackSpec(
        ops="pay",
        event="paid",
        destination="https://test/hooks",
        payload=lambda ctx: {"token": "private payload"},
        send=send,
        signing_secret_ref="billing",
        resolve_secret=lambda ref: "private secret",
        durability="results",
        session_factory=broken_db,
    )
    ctx = {
        "temp": {"identity": {"correlation_id": "cor-1", "invocation_id": "op-1"}},
        "app": SimpleNamespace(
            trace_sink=lambda name, carrier, fields: events.append((name, fields))
        ),
    }
    with pytest.raises(RuntimeError, match="private persistence error"):
        await lower_callback(spec, object, "POST_COMMIT")(ctx)
    assert [name for name, _ in events] == [
        "callback.prepared",
        "callback.delivery.emit",
        "callback.delivery.emit_complete",
        "callback.outcome.persistence_failed",
    ]
    for _, fields in events:
        assert fields["origin_invocation_id"] == "op-1"
        assert fields["origin_correlation_id"] == "cor-1"
        assert fields["delivery_id"] == events[0][1]["delivery_id"]
        assert fields["attempt_id"] == events[0][1]["attempt_id"]
    assert "private" not in str(events)
