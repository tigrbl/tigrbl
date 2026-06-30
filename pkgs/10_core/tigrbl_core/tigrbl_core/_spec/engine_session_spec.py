from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any, Mapping, MutableMapping, Optional, Union

from .serde import SerdeMixin

EngineSessionCfg = Union["EngineSessionSpec", Mapping[str, Any], None]


@dataclass(frozen=True)
class EngineSessionSpec(SerdeMixin):
    """
    Per-session policy for Tigrbl engine database sessions.

    These fields are backend-agnostic hints and constraints. Adapters should
    validate and apply them where supported; critical ones (like isolation and
    read_only) SHOULD be validated and enforced.
    """

    # Transaction policy
    isolation: Optional[str] = (
        None  # "read_committed" | "repeatable_read" | "snapshot" | "serializable"
    )
    read_only: Optional[bool] = None
    autobegin: Optional[bool] = True
    expire_on_commit: Optional[bool] = None

    # Retries & backoff
    retry_on_conflict: Optional[bool] = None
    max_retries: int = 0
    backoff_ms: int = 0
    backoff_jitter: bool = True

    # Timeouts / resources
    statement_timeout_ms: Optional[int] = None
    lock_timeout_ms: Optional[int] = None
    fetch_rows: Optional[int] = None
    stream_chunk_rows: Optional[int] = None

    # Consistency coordinates
    min_lsn: Optional[str] = None
    as_of_ts: Optional[str] = None
    consistency: Optional[str] = None  # "strong" | "bounded_staleness" | "eventual"
    staleness_ms: Optional[int] = None

    # Tenancy & security
    tenant_id: Optional[str] = None
    role: Optional[str] = None
    rls_context: Mapping[str, str] = None

    # Observability
    trace_id: Optional[str] = None
    query_tag: Optional[str] = None
    tag: Optional[str] = None
    tracing_sample: Optional[float] = None

    # Cache / index hints
    cache_read: Optional[bool] = None
    cache_write: Optional[bool] = None
    namespace: Optional[str] = None

    # Data protection / compliance
    kms_key_alias: Optional[str] = None
    classification: Optional[str] = None
    audit: Optional[bool] = None

    # Idempotency & pagination
    idempotency_key: Optional[str] = None
    page_snapshot: Optional[str] = None

    def merge(
        self, higher: "EngineSessionSpec | Mapping[str, Any] | None"
    ) -> "EngineSessionSpec":
        """
        Overlay another spec on top of this one (explicit fields take precedence).
        Use to implement op > model > router > app precedence.
        """
        if higher is None:
            return self
        h = (
            higher
            if isinstance(higher, EngineSessionSpec)
            else EngineSessionSpec.from_any(higher)
        )
        if h is None:
            return self
        defaults = EngineSessionSpec()
        vals: MutableMapping[str, Any] = {
            f.name: getattr(self, f.name) for f in fields(EngineSessionSpec)
        }
        for f in fields(EngineSessionSpec):
            hv = getattr(h, f.name)
            if hv is None:
                continue
            default = getattr(defaults, f.name)
            if hv == default and vals[f.name] != default:
                continue
            vals[f.name] = hv
        return EngineSessionSpec(**vals)  # type: ignore[arg-type]

    def to_kwargs(self) -> dict[str, Any]:
        """Return only non-None items as a plain dict (adapters can **kwargs this)."""
        return {
            f.name: getattr(self, f.name)
            for f in fields(EngineSessionSpec)
            if getattr(self, f.name) is not None
        }

    @staticmethod
    def from_any(x: EngineSessionCfg) -> Optional["EngineSessionSpec"]:
        if x is None:
            return None
        if isinstance(x, EngineSessionSpec):
            return x
        if isinstance(x, Mapping):
            m = dict(x)
            if "readonly" in m and "read_only" not in m:
                m["read_only"] = bool(m.pop("readonly"))
            if "iso" in m and "isolation" not in m:
                m["isolation"] = str(m.pop("iso"))
            allowed = {f.name for f in fields(EngineSessionSpec)}
            return EngineSessionSpec(**{k: v for k, v in m.items() if k in allowed})
        raise TypeError(f"Unsupported EngineSessionSpec input: {type(x)}")


def engine_session_spec(
    cfg: EngineSessionCfg = None, /, **kw: Any
) -> EngineSessionSpec:
    """Build an EngineSessionSpec from either a mapping/spec or kwargs."""
    if cfg is not None and kw:
        raise ValueError("Provide either a mapping/spec or kwargs, not both")
    return EngineSessionSpec.from_any(cfg or kw) or EngineSessionSpec()


def tx_read_committed(*, read_only: Optional[bool] = None) -> EngineSessionSpec:
    return EngineSessionSpec(isolation="read_committed", read_only=read_only)


def tx_repeatable_read(*, read_only: Optional[bool] = None) -> EngineSessionSpec:
    return EngineSessionSpec(isolation="repeatable_read", read_only=read_only)


def tx_serializable(*, read_only: Optional[bool] = None) -> EngineSessionSpec:
    return EngineSessionSpec(isolation="serializable", read_only=read_only)


def readonly() -> EngineSessionSpec:
    return EngineSessionSpec(read_only=True)


__all__ = [
    "EngineSessionCfg",
    "EngineSessionSpec",
    "engine_session_spec",
    "tx_read_committed",
    "tx_repeatable_read",
    "tx_serializable",
    "readonly",
]
