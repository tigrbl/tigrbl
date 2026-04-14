from __future__ import annotations

from tigrbl_core._spec.app_spec import AppSpec
from tigrbl_runtime.native.codec import build_native_app_spec


def test_native_codec_normalizes_runtime_callbacks_and_metadata() -> None:
    payload = build_native_app_spec(
        {
            "name": "payload-demo",
            "metadata": {"owner": "native"},
            "runtime": {"strict_native": True},
            "callbacks": [{"name": "demo.hook", "kind": "hook", "language": "python"}],
        }
    )

    assert payload["name"] == "payload-demo"
    assert payload["metadata"] == {"owner": "native"}
    assert payload["runtime"] == {"strict_native": True}
    assert payload["callbacks"][0]["name"] == "demo.hook"


def test_native_codec_uses_spec_title_as_name_when_name_is_absent() -> None:
    payload = build_native_app_spec(AppSpec(title="native-echo"))

    assert payload["name"] == "native-echo"
    assert payload["title"] == "native-echo"
