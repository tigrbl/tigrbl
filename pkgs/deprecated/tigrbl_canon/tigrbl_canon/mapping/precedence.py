from __future__ import annotations

from dataclasses import replace
from typing import Dict

from tigrbl_core._spec import OpSpec
from tigrbl_core._spec.monotone import highest_precedence, keyed_overlay
from .context import MappingKey


SPEC_PRECEDENCE = ("app", "router", "op", "default")


def key_for(spec: OpSpec) -> MappingKey:
    return (spec.alias, spec.target)


def merge_op_specs(
    base_specs: tuple[OpSpec, ...], ctx_specs: tuple[OpSpec, ...]
) -> tuple[OpSpec, ...]:
    """Apply OpSpec-over-base precedence for operation mapping resolution."""
    merged_by_key: Dict[MappingKey, OpSpec] = keyed_overlay(base_specs, key=key_for)

    for sp in ctx_specs:
        key = key_for(sp)
        base = merged_by_key.get(key)
        if base is None:
            merged_by_key[key] = sp
            continue

        merged_by_key[key] = replace(
            sp,
            http_methods=highest_precedence(
                base.http_methods, sp.http_methods, is_set=bool
            ),
            path_suffix=highest_precedence(
                base.path_suffix, sp.path_suffix, is_set=bool
            ),
            tags=highest_precedence(base.tags, sp.tags, is_set=bool),
            deps=highest_precedence(base.deps, sp.deps, is_set=bool),
            secdeps=highest_precedence(base.secdeps, sp.secdeps, is_set=bool),
            request_model=highest_precedence(base.request_model, sp.request_model),
            response_model=highest_precedence(base.response_model, sp.response_model),
        )

    return tuple(merged_by_key.values())
