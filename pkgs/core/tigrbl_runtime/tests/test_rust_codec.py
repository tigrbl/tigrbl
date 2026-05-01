from __future__ import annotations

from tigrbl_core._spec.app_spec import AppSpec
from tigrbl_core.config.constants import (
    TIGRBL_DEFAULT_ROOT_ALIAS,
    TIGRBL_DEFAULT_ROOT_METHOD,
)
from tigrbl_kernel.rust_spec import build_rust_app_spec


def test_rust_codec_normalizes_runtime_callbacks_and_metadata() -> None:
    payload = build_rust_app_spec(
        {
            "name": "payload-demo",
            "metadata": {"owner": "rust"},
            "runtime": {"strict_rust": True},
            "callbacks": [{"name": "demo.hook", "kind": "hook", "language": "python"}],
        }
    )

    assert payload["name"] == "payload-demo"
    assert payload["metadata"] == {"owner": "rust"}
    assert payload["runtime"] == {"strict_rust": True}
    assert payload["callbacks"][0]["name"] == "demo.hook"


def test_rust_codec_uses_spec_title_as_name_when_name_is_absent() -> None:
    payload = build_rust_app_spec(AppSpec(title="rust-echo"))

    assert payload["name"] == "rust-echo"
    assert payload["title"] == "rust-echo"


def test_rust_codec_appends_default_root_binding_when_missing() -> None:
    payload = build_rust_app_spec(
        {
            "name": "rootless-demo",
            "bindings": [
                {
                    "alias": "widgets.list",
                    "transport": "rest",
                    "family": "rest",
                    "path": "/widgets",
                    "methods": ("GET",),
                    "op": {"name": "widgets.list", "kind": "list", "route": "/widgets"},
                    "table": {"name": "widgets"},
                }
            ],
            "tables": [{"name": "widgets"}],
        }
    )

    root_bindings = [
        binding
        for binding in payload["bindings"]
        if binding["transport"] == "rest" and binding["path"] == "/"
    ]

    assert len(root_bindings) == 1
    assert root_bindings[0]["alias"] == TIGRBL_DEFAULT_ROOT_ALIAS
    assert root_bindings[0]["methods"] == (TIGRBL_DEFAULT_ROOT_METHOD,)


def test_rust_codec_preserves_explicit_root_binding_without_default_alias() -> None:
    payload = build_rust_app_spec(
        {
            "name": "explicit-root-demo",
            "bindings": [
                {
                    "alias": "custom.root",
                    "transport": "rest",
                    "family": "rest",
                    "path": "/",
                    "methods": ("GET",),
                    "op": {"name": "custom.root", "kind": "read", "route": "/"},
                    "table": {"name": "custom_root"},
                }
            ],
            "tables": [{"name": "custom_root"}],
        }
    )

    root_bindings = [
        binding
        for binding in payload["bindings"]
        if binding["transport"] == "rest" and binding["path"] == "/"
    ]

    assert len(root_bindings) == 1
    assert root_bindings[0]["alias"] == "custom.root"
    assert all(binding["alias"] != TIGRBL_DEFAULT_ROOT_ALIAS for binding in root_bindings)
