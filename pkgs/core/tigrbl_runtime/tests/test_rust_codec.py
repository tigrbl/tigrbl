from __future__ import annotations

from tigrbl_core._spec.app_spec import AppSpec
from tigrbl_runtime.rust.codec import build_rust_app_spec


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
