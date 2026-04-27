from __future__ import annotations

from importlib import import_module
import math

import pytest


def _canonicalize(payload):
    candidates = (
        ("tigrbl.runtime.canonical_json", "canonical_json_bytes"),
        ("tigrbl.runtime.canonical_json", "canonicalize"),
        ("tigrbl.canonical_json", "canonical_json_bytes"),
        ("tigrbl.canonical_json", "canonicalize"),
    )
    for module_name, attr in candidates:
        try:
            module = import_module(module_name)
        except ModuleNotFoundError:
            continue
        func = getattr(module, attr, None)
        if callable(func):
            result = func(payload)
            return result.encode("utf-8") if isinstance(result, str) else result
    pytest.xfail("feat:rfc-8785-jcs-rejection-semantics-001 is absent; no JCS helper is exported yet.")


def test_jcs_canonicalizer_orders_object_members_deterministically() -> None:
    assert _canonicalize({"b": 1, "a": 2}) == b'{"a":2,"b":1}'


def test_jcs_canonicalizer_emits_stable_utf8_bytes_for_equivalent_payloads() -> None:
    first = {"outer": {"z": [3, 2, 1], "a": True}, "name": "tigrbl"}
    second = {"name": "tigrbl", "outer": {"a": True, "z": [3, 2, 1]}}
    assert _canonicalize(first) == _canonicalize(second)


@pytest.mark.parametrize("bad_number", [math.nan, math.inf, -math.inf])
def test_jcs_canonicalizer_rejects_non_finite_numbers(bad_number: float) -> None:
    with pytest.raises((TypeError, ValueError), match="finite|NaN|Infinity|JCS|JSON"):
        _canonicalize({"value": bad_number})
