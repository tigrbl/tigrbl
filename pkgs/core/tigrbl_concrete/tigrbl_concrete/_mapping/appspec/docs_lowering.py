from __future__ import annotations

from typing import Any

from tigrbl_core._spec.docs_spec import DocsPayloadSpec, DocsProjectionSelection, DocsUixSpec
from tigrbl_core._spec.path_spec import PathSpec


def canonical_paths(owner: Any) -> tuple[PathSpec, ...]:
    return tuple(getattr(owner, "_tigrbl_path_specs", ()) or ())


def canonical_docs_payloads(owner: Any) -> dict[str, DocsPayloadSpec]:
    return dict(getattr(owner, "_tigrbl_docs_payloads", {}) or {})


def canonical_docs_uix(owner: Any) -> dict[str, DocsUixSpec]:
    return dict(getattr(owner, "_tigrbl_docs_uix", {}) or {})


def projection_for_docs_path(
    owner: Any,
    *,
    docs_path: str | None,
    payload_kind: str,
) -> DocsPayloadSpec | None:
    if not docs_path:
        return None
    payload = canonical_docs_payloads(owner).get(docs_path)
    if payload is None or payload.kind != payload_kind:
        return None
    return payload


def selected_projection_entries(
    owner: Any,
    *,
    docs_path: str | None,
    payload_kind: str,
) -> tuple[DocsProjectionSelection, ...]:
    payload = projection_for_docs_path(owner, docs_path=docs_path, payload_kind=payload_kind)
    if payload is None:
        return ()
    return payload.projection.select(canonical_paths(owner))


def selected_projection_entries_if_configured(
    owner: Any,
    *,
    docs_path: str | None,
    payload_kind: str,
) -> tuple[DocsProjectionSelection, ...] | None:
    payload = projection_for_docs_path(
        owner,
        docs_path=docs_path,
        payload_kind=payload_kind,
    )
    if payload is None:
        return None
    return payload.projection.select(canonical_paths(owner))
