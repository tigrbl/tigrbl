from __future__ import annotations

import pytest

from tigrbl_runtime.semantics import (
    SemanticReactionError,
    acknowledge_application_cancellation,
    complete_application_cancellation,
    observe_application_cancellation,
    react_to_contract_semantic,
)


def test_t0_tigrbl_runtime_names_application_cancellation_sources_only() -> None:
    observed = observe_application_cancellation("requested", "operation_timeout")

    assert observed.as_dict() == {
        "cause": "operation_timeout",
        "domain": "cancellation",
        "event": "cancellation.propagated",
        "previous_state": "requested",
        "source": "tigrbl-runtime",
        "state": "propagated",
    }


def test_t1_application_cancellation_progresses_through_contract_states() -> None:
    propagated = observe_application_cancellation("requested", "hook_failure")
    acknowledged = acknowledge_application_cancellation(propagated.state, propagated.cause)
    completed = complete_application_cancellation(acknowledged.state, acknowledged.cause)

    reaction = react_to_contract_semantic(completed.as_dict())

    assert completed.state == "completed"
    assert reaction.as_dict() == {
        "api_error": "operation_cancelled",
        "audit": True,
        "outcome": "cancelled",
        "post_commit": False,
        "retry": False,
        "rollback": True,
    }


def test_t1_contract_disconnect_observation_maps_to_operation_outcome() -> None:
    reaction = react_to_contract_semantic(
        {
            "domain": "disconnect",
            "event": "disconnect.peer_reset",
            "previous_state": "graceful",
            "source": "tigrcorn",
            "state": "peer_reset",
        }
    )

    assert reaction.rollback is True
    assert reaction.post_commit is False
    assert reaction.api_error == "client_disconnect"


def test_t1_backpressure_reaction_defers_without_transport_semantics() -> None:
    reaction = react_to_contract_semantic(
        {
            "domain": "backpressure",
            "event": "backpressure.saturated",
            "previous_state": "congested",
            "source": "tigrcorn",
            "state": "saturated",
        }
    )

    assert reaction.outcome == "defer"
    assert reaction.retry is True
    assert reaction.rollback is False


@pytest.mark.parametrize(
    "observation",
    [
        {"domain": "http2", "state": "rst_stream", "event": "socket.rst"},
        {"domain": "disconnect", "state": "http2.rst_stream", "event": "disconnect.peer_reset"},
        {"domain": "completion", "state": "queued_for_transport", "event": "completion.queued"},
    ],
)
def test_t2_tigrbl_rejects_protocol_specific_or_incomplete_interpretations(
    observation: dict[str, str],
) -> None:
    with pytest.raises(SemanticReactionError):
        react_to_contract_semantic(observation)


def test_t2_application_cancellation_rejects_transport_originated_causes() -> None:
    with pytest.raises(SemanticReactionError):
        observe_application_cancellation("requested", "stream_reset")
