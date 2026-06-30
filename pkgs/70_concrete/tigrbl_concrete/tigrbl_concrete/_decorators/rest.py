"""Reusable REST decorator aliases over ``op_ctx``."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from tigrbl_core._spec.binding_spec import HttpRestBindingSpec, TransportBindingSpec

from .op import op_ctx


def _normalize_path(path: str) -> str:
    value = str(path or "").strip()
    if not value:
        return "/"
    if not value.startswith("/"):
        value = f"/{value}"
    return value.rstrip("/") or "/"


def _merge_bindings(
    binding: TransportBindingSpec,
    bindings: TransportBindingSpec | Iterable[TransportBindingSpec] | None,
) -> tuple[TransportBindingSpec, ...]:
    if bindings is None:
        return (binding,)
    if isinstance(bindings, Iterable) and not isinstance(bindings, (str, bytes)):
        return (binding, *tuple(bindings))
    return (binding, bindings)


def _rest_ctx(path: str, *, method: str, **kwargs: Any):
    existing_bindings = kwargs.pop("bindings", None)
    binding = HttpRestBindingSpec(
        proto="http.rest",
        path=_normalize_path(path),
        methods=(str(method).upper(),),
    )
    return op_ctx(bindings=_merge_bindings(binding, existing_bindings), **kwargs)


def get(path: str, **kwargs: Any):
    return _rest_ctx(path, method="GET", **kwargs)


def post(path: str, **kwargs: Any):
    return _rest_ctx(path, method="POST", **kwargs)


def put(path: str, **kwargs: Any):
    return _rest_ctx(path, method="PUT", **kwargs)


def patch(path: str, **kwargs: Any):
    return _rest_ctx(path, method="PATCH", **kwargs)


def delete(path: str, **kwargs: Any):
    return _rest_ctx(path, method="DELETE", **kwargs)


__all__ = ["get", "post", "put", "patch", "delete"]
