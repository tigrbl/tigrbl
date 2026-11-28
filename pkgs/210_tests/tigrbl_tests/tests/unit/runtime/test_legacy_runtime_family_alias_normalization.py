from __future__ import annotations

import importlib

import pytest


def _require(module_name: str, attr_name: str):
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        pytest.xfail(f"{module_name} is not implemented")
    value = getattr(module, attr_name, None)
    if value is None:
        pytest.xfail(f"{module_name}.{attr_name} is not implemented")
    return value


@pytest.mark.xfail(reason="Legacy family alias normalization is not complete in the current checkout.")
def test_socket_alias_normalizes_to_governed_runtime_families() -> None:
    normalize = _require("tigrbl_kernel.subevent_taxonomy", "normalize_family_alias")

    result = normalize("socket")

    assert set(result) == {"session", "message"}


@pytest.mark.xfail(reason="Legacy family alias normalization is not complete in the current checkout.")
def test_event_stream_alias_normalizes_to_governed_runtime_families() -> None:
    normalize = _require("tigrbl_kernel.subevent_taxonomy", "normalize_family_alias")

    result = normalize("event_stream")

    assert set(result) == {"stream", "message", "session"}


@pytest.mark.xfail(reason="Repo-local response family normalization is not complete in the current checkout.")
def test_repo_local_response_alias_does_not_remain_canonical_runtime_family() -> None:
    normalize = _require("tigrbl_kernel.subevent_taxonomy", "normalize_family_alias")

    result = normalize("response")

    assert "response" not in set(result)
    assert "request" in set(result)
