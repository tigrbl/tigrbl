from __future__ import annotations

from pathlib import Path


CORE_ROOT = Path(__file__).resolve().parents[3]
TIGRBL_ROOT = CORE_ROOT / "tigrbl" / "tigrbl"
CONCRETE_ROOT = CORE_ROOT / "tigrbl_concrete" / "tigrbl_concrete"
TESTS_ROOT = CORE_ROOT / "tigrbl_tests" / "tests"


DEPRECATED_SHIMS = (
    TIGRBL_ROOT / "transport" / "jsonrpc" / "models.py",
    TIGRBL_ROOT / "transport" / "jsonrpc" / "helpers.py",
    TIGRBL_ROOT / "transport" / "rest" / "aggregator.py",
    CONCRETE_ROOT / "transport" / "jsonrpc" / "models.py",
    CONCRETE_ROOT / "transport" / "jsonrpc" / "helpers.py",
    CONCRETE_ROOT / "transport" / "rest" / "aggregator.py",
)

COMPATIBILITY_TESTS = (
    TESTS_ROOT / "unit" / "test_transport_deprecation_warnings.py",
    TESTS_ROOT / "unit" / "test_transport_compat_imports.py",
    TESTS_ROOT / "unit" / "test_jsonrpc_schema_namespace.py",
    TESTS_ROOT / "unit" / "test_jsonrpc_codec_authority.py",
    TESTS_ROOT / "architecture" / "test_transport_hot_path_boundary.py",
)


def test_deprecated_transport_shims_have_runtime_warnings() -> None:
    for path in DEPRECATED_SHIMS:
        text = path.read_text(encoding="utf-8")

        assert "DeprecationWarning" in text or "warn_deprecated_transport_module" in text


def test_jsonrpc_schema_namespace_replaces_transport_models() -> None:
    assert (TIGRBL_ROOT / "schema" / "jsonrpc.py").exists()
    assert (CONCRETE_ROOT / "schema" / "jsonrpc.py").exists()

    public_models = (
        TIGRBL_ROOT / "transport" / "jsonrpc" / "models.py"
    ).read_text(encoding="utf-8")
    concrete_models = (
        CONCRETE_ROOT / "transport" / "jsonrpc" / "models.py"
    ).read_text(encoding="utf-8")

    assert "tigrbl_concrete.transport.jsonrpc.models" in public_models
    assert "tigrbl_concrete.schema.jsonrpc" in concrete_models
    assert "class RPCRequest" not in public_models
    assert "class RPCRequest" not in concrete_models


def test_transport_deprecation_has_removal_readiness_coverage() -> None:
    missing = [str(path.relative_to(CORE_ROOT)) for path in COMPATIBILITY_TESTS if not path.exists()]

    assert missing == []
