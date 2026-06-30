from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from hashlib import sha256
from typing import Any


REQUIRED_ATOM_REQUIREMENTS = frozenset(
    {
        "semantic_identity",
        "concrete_identity",
        "engine",
        "transport_delivery",
        "framing",
        "idempotency",
        "retry",
        "replay",
        "session_isolation",
        "engine_session_isolation",
    }
)


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    max_attempts: int
    retryable_errors: tuple[str, ...]
    backoff_ms: tuple[int, ...]
    requires_idempotency_or_replay: bool = True
    owner: str = "runtime"


def stable_semantic_id(*parts: str) -> str:
    if not parts or any(not str(part).strip() for part in parts):
        raise ValueError("semantic id parts must be non-empty")
    return sha256("::".join(str(part) for part in parts).encode("utf-8")).hexdigest()


def concrete_id(kind: str, parent_scope: str, local_id: str) -> str:
    if not kind or not parent_scope or not local_id:
        raise ValueError("concrete id requires kind, parent scope, and local id")
    return f"{kind}:{stable_semantic_id(parent_scope, local_id)[:16]}"


def ensure_unique_concrete_ids(ids: Iterable[str]) -> tuple[str, ...]:
    values = tuple(ids)
    if len(set(values)) != len(values):
        raise ValueError("concrete ids must be unique within parent scope")
    return values


def attempt_record(
    *,
    app_id: str,
    router_id: str,
    table_id: str,
    op_id: str,
    attempt_id: str,
) -> dict[str, str]:
    return {
        "app_id": app_id,
        "router_id": router_id,
        "table_id": table_id,
        "op_id": op_id,
        "attempt_id": attempt_id,
    }


def atom_execution_record(
    *,
    atom_id: str,
    attempt_id: str,
    runtime_plan_id: str,
) -> dict[str, str]:
    return {
        "atom_id": atom_id,
        "attempt_id": attempt_id,
        "runtime_plan_id": runtime_plan_id,
    }


def replay_record(*, replay_id: str, original_attempt_id: str) -> dict[str, str]:
    return {"replay_id": replay_id, "original_attempt_id": original_attempt_id}


def project_atom_chain_requirements(
    chain: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    if not chain:
        raise ValueError("atom chain must contain at least one atom")
    atom_order: list[str] = []
    hook_order: list[str] = []
    capability_vector: set[str] = set()
    merged: dict[str, Any] = {}
    diagnostics: list[dict[str, str]] = []
    for index, atom in enumerate(chain):
        atom_id = str(atom.get("atom_id") or "")
        hook_id = str(atom.get("hook_id") or "")
        requirements = atom.get("requirements")
        if not atom_id or not hook_id or not isinstance(requirements, Mapping):
            raise ValueError("atom requirement metadata is required")
        missing = REQUIRED_ATOM_REQUIREMENTS - set(requirements)
        if missing:
            raise ValueError(f"missing atom requirement metadata: {sorted(missing)[0]}")
        atom_order.append(atom_id)
        hook_order.append(hook_id)
        diagnostics.append(
            {
                "atom_id": atom_id,
                "hook_id": hook_id,
                "requirement_source": str(atom.get("source") or f"chain[{index}]"),
            }
        )
        for key, value in requirements.items():
            merged[key] = _merge_requirement(merged.get(key), value)
            capability_vector.add(f"{key}:{_freeze(value)!r}")
    return {
        "requirements": dict(sorted(merged.items())),
        "capability_vector": tuple(sorted(capability_vector)),
        "atom_order": tuple(atom_order),
        "hook_order": tuple(hook_order),
        "diagnostics": tuple(diagnostics),
        "rollup": {
            "atom_count": len(atom_order),
            "capability_count": len(capability_vector),
        },
        "compaction": {
            "atom_order_hash": stable_semantic_id(*atom_order),
            "capability_hash": stable_semantic_id(*tuple(sorted(capability_vector))),
        },
    }


def compile_retry_policy(
    *,
    max_attempts: int,
    retryable_errors: Iterable[str],
    backoff_ms: Iterable[int],
    requires_idempotency_or_replay: bool = True,
    owner: str = "runtime",
) -> RetryPolicy:
    errors = tuple(str(item) for item in retryable_errors)
    backoff = tuple(int(item) for item in backoff_ms)
    if max_attempts < 1:
        raise ValueError("retry max_attempts must be at least one")
    if owner != "runtime":
        raise ValueError("retry owner must be runtime")
    if len(backoff) > max_attempts - 1:
        raise ValueError("retry backoff cannot exceed retry budget")
    return RetryPolicy(max_attempts, errors, backoff, requires_idempotency_or_replay, owner)


def evaluate_retry_attempts(
    *,
    policy: RetryPolicy | None,
    failures: Sequence[str],
    idempotency_key: str | None = None,
    replay_policy: str | None = None,
    original_attempt_id: str = "attempt-1",
    session_scope: str = "session-1",
    retry_session_scope: str = "session-1",
    transaction_open: bool = False,
) -> tuple[dict[str, Any], ...]:
    if policy is None:
        raise ValueError("retry policy is required before attempt execution")
    if policy.requires_idempotency_or_replay and not (idempotency_key or replay_policy):
        raise ValueError("retry requires idempotency key or replay policy")
    if session_scope != retry_session_scope:
        raise ValueError("retry cannot cross session stream datagram or engine session scope")
    if transaction_open:
        raise ValueError("retry cannot reuse open transaction from failed attempt")
    attempts: list[dict[str, Any]] = [
        {
            "attempt_id": original_attempt_id,
            "parent_attempt_id": None,
            "decision": "original",
            "backoff_ms": 0,
        }
    ]
    for index, failure in enumerate(failures):
        if failure not in policy.retryable_errors:
            attempts.append(
                {
                    "attempt_id": f"attempt-{index + 2}",
                    "parent_attempt_id": original_attempt_id,
                    "decision": "stop",
                    "error": failure,
                    "backoff_ms": 0,
                }
            )
            break
        if len(attempts) >= policy.max_attempts:
            attempts.append(
                {
                    "attempt_id": f"attempt-{index + 2}",
                    "parent_attempt_id": original_attempt_id,
                    "decision": "budget-exhausted",
                    "error": failure,
                    "backoff_ms": 0,
                }
            )
            break
        attempts.append(
            {
                "attempt_id": f"attempt-{index + 2}",
                "parent_attempt_id": original_attempt_id,
                "decision": "retry",
                "error": failure,
                "backoff_ms": policy.backoff_ms[min(index, len(policy.backoff_ms) - 1)]
                if policy.backoff_ms
                else 0,
            }
        )
    return tuple(attempts)


def _merge_requirement(existing: Any, incoming: Any) -> Any:
    if existing is None:
        return _freeze(incoming)
    if existing == incoming:
        return existing
    if isinstance(existing, tuple):
        values = set(existing)
    else:
        values = {existing}
    if isinstance(incoming, (tuple, list, set)):
        values.update(_freeze(item) for item in incoming)
    else:
        values.add(_freeze(incoming))
    return tuple(sorted(values, key=repr))


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return tuple((key, _freeze(value[key])) for key in sorted(value))
    if isinstance(value, (list, tuple, set, frozenset)):
        return tuple(_freeze(item) for item in value)
    return value


__all__ = [
    "REQUIRED_ATOM_REQUIREMENTS",
    "RetryPolicy",
    "attempt_record",
    "atom_execution_record",
    "compile_retry_policy",
    "concrete_id",
    "ensure_unique_concrete_ids",
    "evaluate_retry_attempts",
    "project_atom_chain_requirements",
    "replay_record",
    "stable_semantic_id",
]
