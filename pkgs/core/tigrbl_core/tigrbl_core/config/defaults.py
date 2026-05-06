# tigrbl/v3/config/defaults.py
from __future__ import annotations

from typing import Any, Mapping

# Canonical defaults used by config.resolver and runtime atoms.
# Keep these conservative; adapters/apps can override at any scope.
DEFAULTS: Mapping[str, Any] = {
    # ── wire/out (response shaping) ────────────────────────────────────────────
    "exclude_none": False,  # drop null-valued keys in wire:dump
    "omit_nulls": False,  # alias; resolver normalizes both ways
    "response_extras_overwrite": False,  # allow extras to replace existing keys
    "extras_overwrite": False,  # alias; resolver normalizes both ways
    # ── wire/in (request validation) ───────────────────────────────────────────
    "reject_unknown_fields": False,  # if True, unknown input keys cause 422
    # ── refresh / hydration policy ────────────────────────────────────────────
    "refresh_policy": "auto",  # 'auto' | 'always' | 'never'
    "refresh_after_write": None,  # Optional[bool]; resolver maps → policy
    # ── validation/docs policy buckets (deep-merged) ──────────────────────────
    # Shape: dict[op][field] = bool (true means "required for inbound")
    "required_policy": {},
    # ── docs/openapi knobs (deep-merged) ──────────────────────────────────────
    "openapi": {},
    "docs": {},
    # ── lens/openrpc knobs (deep-merged) ──────────────────────────────────────
    "openrpc": {},
    "lens": {},
    # ── tracing (deep-merged) ─────────────────────────────────────────────────
    "trace": {
        "enabled": True,
    },
    # Batch scheduling is opt-in. The conservative defaults avoid changing
    # scalar execution while giving the kernel and atoms one normalized policy
    # shape once an op explicitly enables batching.
    "batch": {
        "enabled": False,
        "max_size": 64,
        "max_bytes": 1_048_576,
        "max_delay_ms": 1,
        "admission_timeout_ms": 5,
        "conflict_policy": "single_fallback",
        "overflow_policy": "backpressure",
        "result_fanout": "by_admission",
        "allow_reads": False,
    },
}
