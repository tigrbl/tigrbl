"""Helpers for mounting RFC 8615 well-known URI resources."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from tigrbl_core._spec.path_spec import PathSpec
from tigrbl_core._spec.well_known_spec import (
    WELL_KNOWN_PREFIX,
    WellKnownResourceSpec,
    normalize_well_known_name,
    well_known_op_alias,
    well_known_path,
)


@dataclass(frozen=True)
class WellKnownResource:
    """A single resource exposed under ``/.well-known/{name}``."""

    name: str
    payload: Any
    media_type: str = "application/json"
    status_code: int = 200
    headers: Mapping[str, str] | None = None


def well_known_route_name(name: str) -> str:
    return well_known_op_alias(name)


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
        if hasattr(resource, "name") and hasattr(resource, "payload"):
            coerced.append(
                WellKnownResource(
                    name=str(getattr(resource, "name")),
                    payload=getattr(resource, "payload"),
                    media_type=str(getattr(resource, "media_type", "application/json")),
                    status_code=int(getattr(resource, "status_code", 200)),
                    headers=getattr(resource, "headers", None),
                )
            )
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

    mounted: list[str] = []
    seen: set[str] = set()
    del tags
    path_specs = list(getattr(router, "_tigrbl_path_specs", ()) or ())
    for resource in _coerce_resources(resources):
        paths = [well_known_path(resource.name)]

        for path in paths:
            if path in seen:
                continue
            seen.add(path)
            path_specs.append(
                PathSpec(
                    path=path,
                    kind="well-known",
                    well_known=WellKnownResourceSpec(
                        name=resource.name,
                        payload=resource.payload,
                        media_type=resource.media_type,
                        status_code=resource.status_code,
                        headers=resource.headers,
                    ),
                )
            )
            mounted.append(path)

    setattr(router, "_tigrbl_path_specs", tuple(path_specs))
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
