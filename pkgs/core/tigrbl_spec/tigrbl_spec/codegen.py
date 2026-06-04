from __future__ import annotations

from importlib import import_module

from tigrbl_spec.schema import CURRENT_SCHEMA_VERSION, spec_kinds


class CodegenFreshnessError(AssertionError):
    """Raised when checked-in generated models do not match packaged schemas."""


def generated_module_name(version: str = CURRENT_SCHEMA_VERSION) -> str:
    normalized = version.replace(".", "_")
    return f"tigrbl_spec.models.v{normalized}"


def check_generated_model_freshness(version: str = CURRENT_SCHEMA_VERSION) -> None:
    module = import_module(generated_module_name(version))
    expected = set(spec_kinds(version))
    actual = {name for name in getattr(module, "__all__", ()) if name != "SpecDataclass"}
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing or extra:
        raise CodegenFreshnessError(
            f"Generated tigrbl_spec dataclasses are stale for {version}: "
            f"missing={missing}, extra={extra}"
        )
