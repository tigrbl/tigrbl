from __future__ import annotations

import pytest

from tigrbl_core._spec import hook_spec
from tigrbl_core._spec.hook_spec import HookSpec
from tigrbl_core._spec.hook_types import HookPhase


def _noop(*_args: object, **_kwargs: object) -> None:
    return None


def _validate(hook: HookSpec) -> object:
    validator = getattr(hook_spec, "validate_hook_legality", None)
    if validator is None:
        pytest.xfail("runtime hook legality validator is not implemented")
    return validator(hook)


def test_user_hook_is_legal_on_public_lifecycle_phase() -> None:
    hook = HookSpec(phase=HookPhase.PRE_HANDLER, fn=_noop, name="public_pre_handler")

    result = _validate(hook)

    assert result in (None, (), [])


def test_user_hook_cannot_target_runtime_owned_post_emit_fence() -> None:
    hook = HookSpec(phase="POST_EMIT", fn=_noop, name="illegal_post_emit")

    with pytest.raises(ValueError, match="POST_EMIT|runtime-owned|completion fence"):
        _validate(hook)


def test_user_hook_cannot_target_removed_ingress_route_phase() -> None:
    hook = HookSpec(phase="INGRESS_ROUTE", fn=_noop, name="illegal_ingress_route")

    with pytest.raises(ValueError, match="INGRESS_ROUTE|canonical phase"):
        _validate(hook)
