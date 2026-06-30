from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


class SemanticReactionError(ValueError):
    """Raised when an application semantic reaction is ambiguous or unsupported."""


_APPLICATION_CANCELLATION_CAUSES = {
    "operation_timeout",
    "authorization_abort",
    "validation_abort",
    "dependency_failure",
    "transaction_rollback",
    "hook_failure",
    "idempotency_conflict",
}

_CANCELLATION_TRANSITIONS = {
    ("requested", "cancellation.propagated"): "propagated",
    ("propagated", "cancellation.acknowledged"): "acknowledged",
    ("acknowledged", "cancellation.completed"): "completed",
    ("requested", "cancellation.ignored"): "ignored",
    ("propagated", "cancellation.failed"): "failed",
    ("acknowledged", "cancellation.failed"): "failed",
}

_PROTOCOL_SPECIFIC_TOKENS = {
    "h2",
    "h3",
    "http2",
    "http3",
    "quic",
    "end_stream",
    "goaway",
    "rst_stream",
    "reset_stream",
    "stop_sending",
    "half_closed",
    "websocket.closing",
    "tcp.reset",
}


@dataclass(frozen=True, slots=True)
class ApplicationSemanticObservation:
    domain: str
    previous_state: str
    event: str
    state: str
    source: str
    cause: str | None = None

    def as_dict(self) -> dict[str, str]:
        payload = {
            "domain": self.domain,
            "event": self.event,
            "previous_state": self.previous_state,
            "source": self.source,
            "state": self.state,
        }
        if self.cause:
            payload["cause"] = self.cause
        return payload


@dataclass(frozen=True, slots=True)
class OperationSemanticReaction:
    outcome: str
    rollback: bool
    retry: bool
    post_commit: bool
    audit: bool
    api_error: str | None = None
    webhook_status: str | None = None

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "audit": self.audit,
            "outcome": self.outcome,
            "post_commit": self.post_commit,
            "retry": self.retry,
            "rollback": self.rollback,
        }
        if self.api_error is not None:
            payload["api_error"] = self.api_error
        if self.webhook_status is not None:
            payload["webhook_status"] = self.webhook_status
        return payload


def observe_application_cancellation(state: str, cause: str) -> ApplicationSemanticObservation:
    if cause not in _APPLICATION_CANCELLATION_CAUSES:
        raise SemanticReactionError(f"unsupported application cancellation cause: {cause!r}")
    return _transition_application_cancellation(
        state,
        "cancellation.propagated",
        cause=cause,
    )


def acknowledge_application_cancellation(state: str, cause: str | None = None) -> ApplicationSemanticObservation:
    return _transition_application_cancellation(
        state,
        "cancellation.acknowledged",
        cause=cause,
    )


def complete_application_cancellation(state: str, cause: str | None = None) -> ApplicationSemanticObservation:
    return _transition_application_cancellation(
        state,
        "cancellation.completed",
        cause=cause,
    )


def react_to_contract_semantic(observation: Mapping[str, Any]) -> OperationSemanticReaction:
    domain = str(observation.get("domain") or "")
    state = str(observation.get("state") or "")
    event = str(observation.get("event") or "")
    cause = str(observation.get("cause") or observation.get("detail") or "")

    _reject_protocol_specific_application_terms(domain, state, event)

    if domain == "cancellation":
        if state in {"propagated", "acknowledged"}:
            return OperationSemanticReaction(
                outcome="cancel_pending",
                rollback=True,
                retry=False,
                post_commit=False,
                audit=True,
                api_error="operation_cancelled",
            )
        if state == "completed":
            return OperationSemanticReaction(
                outcome="cancelled",
                rollback=True,
                retry=False,
                post_commit=False,
                audit=True,
                api_error="operation_cancelled",
            )
        if state == "ignored":
            return OperationSemanticReaction(
                outcome="continue",
                rollback=False,
                retry=False,
                post_commit=True,
                audit=True,
            )
        if state == "failed":
            return OperationSemanticReaction(
                outcome="cancel_failed",
                rollback=True,
                retry=False,
                post_commit=False,
                audit=True,
                api_error="cancellation_failed",
            )

    if domain == "disconnect":
        if state == "graceful":
            return OperationSemanticReaction(
                outcome="closed",
                rollback=False,
                retry=False,
                post_commit=True,
                audit=True,
            )
        if state in {"peer_reset", "transport_lost", "timeout", "protocol_error", "server_shutdown"}:
            return OperationSemanticReaction(
                outcome="client_gone",
                rollback=True,
                retry=state in {"transport_lost", "timeout", "server_shutdown"},
                post_commit=False,
                audit=True,
                api_error="client_disconnect",
            )

    if domain == "completion":
        if state in {"peer_acknowledged", "flushed_to_transport"}:
            return OperationSemanticReaction(
                outcome="delivered",
                rollback=False,
                retry=False,
                post_commit=True,
                audit=True,
                webhook_status="delivered",
            )
        if state == "failed_during_emit":
            return OperationSemanticReaction(
                outcome="emit_failed",
                rollback=False,
                retry=True,
                post_commit=False,
                audit=True,
                webhook_status="failed",
            )
        if state == "aborted_by_peer":
            return OperationSemanticReaction(
                outcome="aborted",
                rollback=True,
                retry=False,
                post_commit=False,
                audit=True,
                api_error="client_disconnect",
                webhook_status="aborted",
            )

    if domain == "backpressure":
        if state in {"congested", "saturated", "draining"}:
            return OperationSemanticReaction(
                outcome="defer",
                rollback=False,
                retry=True,
                post_commit=False,
                audit=True,
                api_error="backpressure",
            )
        if state in {"writable", "resumed"}:
            return OperationSemanticReaction(
                outcome="continue",
                rollback=False,
                retry=False,
                post_commit=True,
                audit=False,
            )

    if domain == "channel_lifecycle":
        if state == "read_closed":
            return OperationSemanticReaction(
                outcome="input_complete",
                rollback=False,
                retry=False,
                post_commit=True,
                audit=True,
            )
        if state == "write_closed":
            return OperationSemanticReaction(
                outcome="output_suppressed",
                rollback=False,
                retry=False,
                post_commit=False,
                audit=True,
                api_error="channel_write_closed",
                webhook_status="suppressed",
            )
        if state == "closing":
            return OperationSemanticReaction(
                outcome="draining",
                rollback=False,
                retry=False,
                post_commit=False,
                audit=True,
                webhook_status="suppressed",
            )
        if state == "closed":
            return OperationSemanticReaction(
                outcome="closed",
                rollback=False,
                retry=False,
                post_commit=True,
                audit=True,
            )
        if state in {"failed", "lost"}:
            return OperationSemanticReaction(
                outcome=f"channel_{state}",
                rollback=True,
                retry=state == "lost",
                post_commit=False,
                audit=True,
                api_error="client_disconnect",
                webhook_status="aborted",
            )

    raise SemanticReactionError(
        f"unsupported semantic observation for application reaction: {domain}:{event}:{state}:{cause}"
    )


def _transition_application_cancellation(
    state: str,
    event: str,
    *,
    cause: str | None = None,
) -> ApplicationSemanticObservation:
    try:
        next_state = _CANCELLATION_TRANSITIONS[(state, event)]
    except KeyError as exc:
        raise SemanticReactionError(f"illegal application cancellation transition: {state} + {event}") from exc
    return ApplicationSemanticObservation(
        domain="cancellation",
        previous_state=state,
        event=event,
        state=next_state,
        source="tigrbl-runtime",
        cause=cause,
    )


def _reject_protocol_specific_application_terms(*values: str) -> None:
    lowered = " ".join(values).lower()
    if any(token in lowered for token in _PROTOCOL_SPECIFIC_TOKENS):
        raise SemanticReactionError("protocol-specific lifecycle mechanics are not application semantics")


__all__ = [
    "ApplicationSemanticObservation",
    "OperationSemanticReaction",
    "SemanticReactionError",
    "acknowledge_application_cancellation",
    "complete_application_cancellation",
    "observe_application_cancellation",
    "react_to_contract_semantic",
]
