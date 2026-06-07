"""Helpers for mounting RFC 8615 well-known URI resources."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
import re
from typing import Any

from tigrbl_concrete._concrete._response import Response

WELL_KNOWN_PREFIX = "/.well-known"


@dataclass(frozen=True)
class WellKnownResource:
    """A single resource exposed under ``/.well-known/{name}``."""

    name: str
    payload: Any
    media_type: str = "application/json"
    status_code: int = 200
    headers: Mapping[str, str] | None = None


def normalize_well_known_name(name: str) -> str:
    token = str(name or "").strip()
    if token.startswith(f"{WELL_KNOWN_PREFIX}/"):
        token = token[len(WELL_KNOWN_PREFIX) + 1 :]
    elif token.startswith("/"):
        raise ValueError(
            "Well-known resource names must be relative or start with "
            f"{WELL_KNOWN_PREFIX}/."
        )
    token = token.strip("/")
    if not token:
        raise ValueError("Well-known resource name must not be empty.")
    parts = token.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError(f"Invalid well-known resource name: {name!r}.")
    if any("?" in part or "#" in part for part in parts):
        raise ValueError(f"Invalid well-known resource name: {name!r}.")
    return "/".join(parts)


def well_known_path(name: str) -> str:
    return f"{WELL_KNOWN_PREFIX}/{normalize_well_known_name(name)}"


def well_known_route_name(name: str) -> str:
    token = normalize_well_known_name(name)
    slug = re.sub(r"[^0-9A-Za-z_]+", "_", token).strip("_")
    return f"well_known_{slug or 'resource'}"


def _resource_endpoint(resource: WellKnownResource) -> Callable[[], Any]:
    payload = resource.payload
    if callable(payload):
        return payload

    async def _endpoint() -> Response:
        if resource.media_type == "application/json":
            return Response.from_json(
                payload,
                status_code=resource.status_code,
                headers=resource.headers,
            )
        if resource.media_type.startswith("text/"):
            return Response.text(
                str(payload),
                status_code=resource.status_code,
                headers=resource.headers,
            )
        content = payload if isinstance(payload, bytes) else str(payload).encode()
        return Response(
            status_code=resource.status_code,
            body=content,
            media_type=resource.media_type,
            headers=resource.headers,
        )

    _endpoint.__name__ = well_known_route_name(resource.name)
    return _endpoint


def _coerce_resources(
    resources: Sequence[WellKnownResource | Mapping[str, Any]] | Mapping[str, Any],
) -> tuple[WellKnownResource, ...]:
    if isinstance(resources, Mapping):
        return tuple(
            WellKnownResource(name=str(name), payload=payload)
            for name, payload in resources.items()
        )

    coerced: list[WellKnownResource] = []
    for resource in resources:
        if isinstance(resource, WellKnownResource):
            coerced.append(resource)
            continue
        if isinstance(resource, Mapping):
            coerced.append(WellKnownResource(**dict(resource)))
            continue
        raise TypeError(
            "Well-known resources must be WellKnownResource instances or mappings."
        )
    return tuple(coerced)


def mount_well_known(
    router: Any,
    resources: Sequence[WellKnownResource | Mapping[str, Any]] | Mapping[str, Any],
    *,
    tags: list[str] | None = None,
) -> tuple[str, ...]:
    """Mount explicit resources under ``/.well-known``.

    No resources are mounted implicitly. Callers must provide every well-known
    resource they intend to publish.
    """

    add_route = getattr(router, "add_route", None)
    if not callable(add_route):
        raise TypeError("Router-like object must provide add_route(...).")

    mounted: list[str] = []
    seen: set[str] = set()
    route_tags = tags if tags is not None else ["well-known"]
    for resource in _coerce_resources(resources):
        paths = [well_known_path(resource.name)]

        for path in paths:
            if path in seen:
                continue
            seen.add(path)
            add_route(
                path,
                _resource_endpoint(resource),
                methods=["GET"],
                name=well_known_route_name(resource.name),
                tags=route_tags,
                include_in_schema=False,
                inherit_owner_dependencies=False,
            )
            mounted.append(path)

    mounts = list(getattr(router, "_well_known_mounts", ()) or ())
    mounts.extend(mounted)
    setattr(router, "_well_known_mounts", mounts)
    return tuple(mounted)


__all__ = [
    "WELL_KNOWN_PREFIX",
    "WellKnownResource",
    "mount_well_known",
    "normalize_well_known_name",
    "well_known_path",
]
