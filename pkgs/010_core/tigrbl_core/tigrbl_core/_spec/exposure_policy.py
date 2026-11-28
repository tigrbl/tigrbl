from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from .binding_spec import canonical_binding_kind


DOCS_SURFACES = frozenset({"openapi", "openrpc"})
RUNTIME_SURFACES = frozenset({"http", "jsonrpc", "stream", "sse", "websocket", "webtransport"})
SUPPORTED_BINDING_KINDS = frozenset(
    {
        "http.rest",
        "http.jsonrpc",
        "http.stream",
        "http.sse",
        "ws",
        "webtransport",
    }
)


@dataclass(frozen=True, slots=True)
class ExposureDecision:
    docs: bool
    runtime: bool
    docs_source: str
    runtime_source: str


class ExposurePolicyError(ValueError):
    pass


def resolve_exposure_policy(
    *,
    docs_exposure: str = "default",
    runtime_exposure: str = "none",
    binding: Any | None = None,
) -> ExposureDecision:
    docs = _enabled(docs_exposure, default=True)
    runtime = _enabled(runtime_exposure, default=False)
    if runtime:
        if binding is None:
            raise ExposurePolicyError("runtime exposure requires declared transport binding")
        _require_supported_binding(binding)
    if docs and binding is not None:
        _require_supported_binding(binding)
    return ExposureDecision(
        docs=docs,
        runtime=runtime,
        docs_source=str(docs_exposure),
        runtime_source=str(runtime_exposure),
    )


def exposed_surfaces(decision: ExposureDecision, binding: Any | None = None) -> tuple[str, ...]:
    surfaces: list[str] = []
    if decision.docs:
        surfaces.extend(("openapi", "openrpc"))
    if decision.runtime:
        if binding is None:
            raise ExposurePolicyError("runtime exposure requires declared transport binding")
        surfaces.append(_runtime_surface(binding))
    return tuple(surfaces)


def _enabled(value: str, *, default: bool) -> bool:
    token = str(value or "default").strip().lower()
    if token == "default":
        return default
    if token in {"enabled", "on", "true"}:
        return True
    if token in {"disabled", "none", "off", "false"}:
        return False
    raise ExposurePolicyError(f"unsupported exposure value: {value!r}")


def _require_supported_binding(binding: Any) -> str:
    kind = _binding_kind(binding)
    if kind not in SUPPORTED_BINDING_KINDS:
        raise ExposurePolicyError(f"unsupported transport binding: {kind}")
    return kind


def _runtime_surface(binding: Any) -> str:
    kind = _require_supported_binding(binding)
    return {
        "http.rest": "http",
        "http.jsonrpc": "jsonrpc",
        "http.stream": "stream",
        "http.sse": "sse",
        "ws": "websocket",
        "webtransport": "webtransport",
    }[kind]


def _binding_kind(binding: Any) -> str:
    if isinstance(binding, Mapping):
        return str(binding.get("kind") or binding.get("proto") or "")
    return canonical_binding_kind(binding)


__all__ = [
    "DOCS_SURFACES",
    "RUNTIME_SURFACES",
    "ExposureDecision",
    "ExposurePolicyError",
    "exposed_surfaces",
    "resolve_exposure_policy",
]
