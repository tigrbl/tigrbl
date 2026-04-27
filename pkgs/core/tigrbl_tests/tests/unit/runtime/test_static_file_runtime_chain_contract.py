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


def test_static_file_chain_resolves_route_and_emits_file_response() -> None:
    run = _require("tigrbl_runtime.protocol.static_files", "run_static_file_chain")

    result = run(
        request={"path": "/assets/app.css", "method": "GET"},
        mount={"path": "/assets", "directory": "/srv/assets"},
        file_exists=lambda path: True,
        read_file=lambda path: b"body{}",
    )

    assert result["status_code"] == 200
    assert result["file_path"] == "/srv/assets/app.css"
    assert result["body"] == b"body{}"
    assert result["completed_subevent"] == "static_file.emit_complete"


def test_static_file_chain_rejects_path_traversal_before_file_lookup() -> None:
    run = _require("tigrbl_runtime.protocol.static_files", "run_static_file_chain")
    looked_up: list[str] = []

    result = run(
        request={"path": "/assets/../secret.txt", "method": "GET"},
        mount={"path": "/assets", "directory": "/srv/assets"},
        file_exists=lambda path: looked_up.append(path) or True,
        capture_errors=True,
    )

    assert looked_up == []
    assert result["status_code"] == 404
    assert result["error_ctx"]["subevent"] == "static_file.security.reject"


def test_static_file_chain_returns_governed_404_for_missing_file() -> None:
    run = _require("tigrbl_runtime.protocol.static_files", "run_static_file_chain")

    result = run(
        request={"path": "/assets/missing.txt", "method": "GET"},
        mount={"path": "/assets", "directory": "/srv/assets"},
        file_exists=lambda path: False,
    )

    assert result["status_code"] == 404
    assert result["subevent"] == "static_file.not_found"
    assert result["completed"] is True


def test_static_file_chain_compiles_range_and_cache_header_atoms() -> None:
    compile_chain = _require("tigrbl_kernel.protocol_chains.static_files", "compile_static_file_chain")

    chain = compile_chain(range_requests=True, cache_headers=True, pathsend=True)

    assert "static_file.range.parse" in chain["atoms"]
    assert "static_file.cache.headers" in chain["atoms"]
    assert "transport.pathsend" in chain["atoms"]
    assert chain["atoms"][-1] == "transport.emit_complete"


def test_static_file_range_request_emits_partial_content_metadata() -> None:
    run = _require("tigrbl_runtime.protocol.static_files", "run_static_file_chain")

    result = run(
        request={"path": "/assets/video.bin", "method": "GET", "headers": {"range": "bytes=0-3"}},
        mount={"path": "/assets", "directory": "/srv/assets"},
        file_exists=lambda path: True,
        stat_file=lambda path: {"size": 10, "etag": "abc"},
        read_file_range=lambda path, start, end: b"0123",
    )

    assert result["status_code"] == 206
    assert result["body"] == b"0123"
    assert result["headers"]["content-range"] == "bytes 0-3/10"
    assert result["headers"]["etag"] == "abc"
