from __future__ import annotations

import pytest

from tigrbl_runtime.semantics import SemanticReactionError, react_to_contract_semantic


def test_t0_application_accepts_canonical_lifecycle_state_with_transport_provenance() -> None:
    reaction = react_to_contract_semantic(
        {
            "detail": "transport:h3.reset_stream:write",
            "domain": "channel_lifecycle",
            "event": "channel.write_closed",
            "previous_state": "open",
            "source": "tigrcorn",
            "state": "write_closed",
        }
    )

    assert reaction.outcome == "output_suppressed"
    assert reaction.rollback is False
    assert reaction.webhook_status == "suppressed"


@pytest.mark.parametrize(
    ("state", "outcome", "rollback", "post_commit"),
    [
        ("read_closed", "input_complete", False, True),
        ("write_closed", "output_suppressed", False, False),
        ("closing", "draining", False, False),
        ("closed", "closed", False, True),
        ("failed", "channel_failed", True, False),
        ("lost", "channel_lost", True, False),
    ],
)
def test_t1_application_policy_is_bound_to_contract_states_not_protocol_terms(
    state: str,
    outcome: str,
    rollback: bool,
    post_commit: bool,
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

    assert reaction.outcome == outcome
    assert reaction.rollback is rollback
    assert reaction.post_commit is post_commit


@pytest.mark.parametrize(
    "observation",
    [
        {"domain": "h2", "event": "channel.read_closed", "state": "read_closed"},
        {"domain": "channel_lifecycle", "event": "h2.end_stream_received", "state": "read_closed"},
        {"domain": "channel_lifecycle", "event": "h2.rst_stream", "state": "lost"},
        {"domain": "channel_lifecycle", "event": "h2.goaway", "state": "closing"},
        {"domain": "h3", "event": "channel.write_closed", "state": "write_closed"},
        {"domain": "channel_lifecycle", "event": "h3.reset_stream", "state": "write_closed"},
        {"domain": "channel_lifecycle", "event": "h3.stop_sending", "state": "read_closed"},
        {"domain": "quic", "event": "channel.lost", "state": "lost"},
        {"domain": "channel_lifecycle", "event": "quic.connection_close", "state": "closing"},
        {"domain": "channel_lifecycle", "event": "channel.write_closed", "state": "quic.stop_sending"},
        {"domain": "channel_lifecycle", "event": "websocket.closing", "state": "closing"},
    ],
)
def test_t2_protocol_mechanics_are_rejected_in_application_semantic_inputs(
    observation: dict[str, str],
) -> None:
    with pytest.raises(SemanticReactionError, match="protocol-specific"):
        react_to_contract_semantic(observation)
