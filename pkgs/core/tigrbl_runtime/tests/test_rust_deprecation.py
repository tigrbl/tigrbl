from __future__ import annotations

import pytest

from tigrbl_runtime import Runtime
from tigrbl_runtime.rust import (
    RustBindingsUnavailableError,
    build_rust_app_spec,
    compiled_extension_available,
    create_runtime,
    rust_available,
)


def test_rust_availability_helpers_report_disabled() -> None:
    with pytest.warns(DeprecationWarning):
        assert rust_available() is False
    with pytest.warns(DeprecationWarning):
        assert compiled_extension_available() is False


def test_runtime_rejects_rust_executor_backend() -> None:
    with pytest.warns(DeprecationWarning):
        with pytest.raises(RustBindingsUnavailableError, match="Python-only"):
            Runtime(executor_backend="rust")


def test_runtime_rust_handle_and_execute_rust_raise() -> None:
    runtime = Runtime()

    with pytest.raises(RustBindingsUnavailableError, match="Python-only"):
        runtime.rust_handle({"name": "demo"})
    with pytest.raises(RustBindingsUnavailableError, match="Python-only"):
        runtime.execute_rust({"transport": "rest"})


def test_rust_codec_and_runtime_factories_raise() -> None:
    with pytest.warns(DeprecationWarning):
        with pytest.raises(RustBindingsUnavailableError, match="Python-only"):
            build_rust_app_spec({"name": "demo"})
    with pytest.warns(DeprecationWarning):
        with pytest.raises(RustBindingsUnavailableError, match="Python-only"):
            create_runtime({"name": "demo"})
