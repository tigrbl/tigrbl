from __future__ import annotations

from tigrbl_kernel.startup_payload import build_startup_payload


def test_startup_payload_normalizes_runtime_callbacks_and_metadata() -> None:
    payload = build_startup_payload(
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
