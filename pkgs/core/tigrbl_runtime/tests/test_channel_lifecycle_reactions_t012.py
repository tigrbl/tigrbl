from __future__ import annotations

import pytest

from tigrbl_runtime.semantics import SemanticReactionError, react_to_contract_semantic


def test_t0_application_consumes_contract_lifecycle_vocabulary_only() -> None:
    reaction = react_to_contract_semantic(
        {
            "domain": "channel_lifecycle",
            "event": "channel.read_closed",
            "previous_state": "open",
            "source": "tigrcorn",
            "state": "read_closed",
        }
    )

    assert reaction.as_dict() == {
        "audit": True,
        "outcome": "input_complete",
        "post_commit": True,
        "retry": False,
        "rollback": False,
    }


def test_t1_write_closed_suppresses_outward_delivery_without_rollback() -> None:
    reaction = react_to_contract_semantic(
        {
            "domain": "channel_lifecycle",
            "event": "channel.write_closed",
            "previous_state": "open",
            "source": "tigrcorn",
            "state": "write_closed",
        }
    )

    assert reaction.rollback is False
    assert reaction.post_commit is False
    assert reaction.webhook_status == "suppressed"
    assert reaction.api_error == "channel_write_closed"


def test_t1_closing_suppresses_new_outward_work_but_does_not_force_rollback() -> None:
    reaction = react_to_contract_semantic(
        {
            "domain": "channel_lifecycle",
            "event": "channel.closing",
            "previous_state": "open",
            "source": "tigrcorn",
            "state": "closing",
        }
    )

    assert reaction.outcome == "draining"
    assert reaction.rollback is False
    assert reaction.retry is False
    assert reaction.post_commit is False


@pytest.mark.parametrize(
    ("state", "retry"),
    [
        ("failed", False),
        ("lost", True),
    ],
)
def test_t2_failed_and_lost_map_to_disconnect_cancellation_policy_candidates(
    state: str,
    retry: bool,
) -> None:
    reaction = react_to_contract_semantic(
        {
            "domain": "channel_lifecycle",
            "event": f"channel.{state}",
            "previous_state": "open",
            "source": "tigrcorn",
            "state": state,
        }
    )

    assert reaction.rollback is True
    assert reaction.post_commit is False
    assert reaction.api_error == "client_disconnect"
    assert reaction.webhook_status == "aborted"
    assert reaction.retry is retry


@pytest.mark.parametrize(
    "observation",
    [
        {"domain": "h3", "event": "h3.reset_stream", "state": "reset_stream"},
        {"domain": "channel_lifecycle", "event": "h3.reset_stream", "state": "write_closed"},
        {"domain": "channel_lifecycle", "event": "channel.write_closed", "state": "quic.stop_sending"},
        {"domain": "channel_lifecycle", "event": "websocket.closing", "state": "closing"},
    ],
)
def test_t2_application_rejects_protocol_specific_lifecycle_mechanics(
    observation: dict[str, str],
) -> None:
    with pytest.raises(SemanticReactionError, match="protocol-specific"):
        react_to_contract_semantic(observation)
