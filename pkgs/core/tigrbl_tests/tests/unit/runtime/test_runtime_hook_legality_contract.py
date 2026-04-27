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


def test_raw_string_runtime_phase_cannot_bypass_hook_legality() -> None:
    hook = HookSpec(phase="POST_EMIT", fn=_noop, name="raw_post_emit")

    with pytest.raises(ValueError, match="POST_EMIT|runtime-owned|hook"):
        _validate(hook)


@pytest.mark.parametrize("phase", ("INGRESS_ROUTE", "POST_EMIT"))
def test_hook_legality_error_names_the_illegal_runtime_phase(phase: str) -> None:
    hook = HookSpec(phase=phase, fn=_noop, name=f"illegal_{phase.lower()}")

    with pytest.raises(ValueError) as exc_info:
        _validate(hook)

    assert phase in str(exc_info.value)


def test_hook_legality_rejects_selector_metadata_for_runtime_owned_phase() -> None:
    validate_selector = getattr(hook_spec, "validate_hook_selector_legality", None)
    if validate_selector is None:
        pytest.xfail("runtime hook selector legality validator is not implemented")

    with pytest.raises(ValueError, match="POST_EMIT|runtime-owned|selector"):
        validate_selector(
            {
                "phase": "POST_EMIT",
                "exchange": "server_stream",
                "family": "stream",
                "subevent": "stream.emit_complete",
            }
        )


def test_hook_legality_allows_public_phase_with_stream_selector_metadata() -> None:
    validate_selector = getattr(hook_spec, "validate_hook_selector_legality", None)
    if validate_selector is None:
        pytest.xfail("runtime hook selector legality validator is not implemented")

    result = validate_selector(
        {
            "phase": "PRE_HANDLER",
            "exchange": "server_stream",
            "family": "stream",
            "subevent": "stream.chunk",
        }
    )

    assert result in (None, (), [])
