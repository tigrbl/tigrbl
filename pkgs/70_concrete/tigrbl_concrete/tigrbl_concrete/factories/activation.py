"""Explicit activation for provided table specifications."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from tigrbl_core._spec.hook_spec import HookSpec
from tigrbl_core._spec.op_spec import OpSpec
from tigrbl_core._spec.table_spec import TableSpec

from .table import provideTableSpec


def _hook_key(hook: Any) -> tuple[Any, Any, Any]:
    return (
        getattr(hook, "name", None),
        getattr(hook, "phase", None),
        getattr(hook, "ops", None),
    )


def activateTableSpec(source: type | TableSpec) -> tuple[OpSpec, ...]:
    """Install a specification on its table and rebuild bound operations."""

    spec = provideTableSpec(source)
    table = spec.model
    merged_ops: dict[tuple[Any, Any], Any] = {}
    for operation in (
        *tuple(getattr(table, "__tigrbl_ops__", ()) or ()),
        *tuple(spec.ops),
    ):
        alias = getattr(operation, "alias", None)
        target = getattr(operation, "target", None)
        key = (
            (alias, target)
            if alias is not None and target is not None
            else ("legacy", operation)
        )
        merged_ops[key] = operation
    table.__tigrbl_ops__ = tuple(merged_ops.values())

    merged_hooks: dict[tuple[Any, Any, Any], Any] = {}
    for hook in (*tuple(getattr(table, "HOOKS", ()) or ()), *tuple(spec.hooks)):
        if isinstance(hook, HookSpec):
            merged_hooks[_hook_key(hook)] = hook
    table.HOOKS = tuple(merged_hooks.values())

    from tigrbl_concrete._mapping.model import rebind

    return tuple(rebind(table))


def activateTableSpecs(
    sources: Iterable[type | TableSpec],
) -> dict[str, tuple[OpSpec, ...]]:
    """Activate multiple provided specifications by concrete model name."""

    out: dict[str, tuple[OpSpec, ...]] = {}
    for source in sources:
        spec = provideTableSpec(source)
        out[spec.model.__name__] = activateTableSpec(spec)
    return out


__all__ = ["activateTableSpec", "activateTableSpecs"]
