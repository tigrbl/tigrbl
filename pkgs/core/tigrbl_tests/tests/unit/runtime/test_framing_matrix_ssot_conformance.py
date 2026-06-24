from __future__ import annotations

from pathlib import Path

from tigrbl_core._spec.binding_spec import (
    APP_LEVEL_FRAMING_SUPPORT,
    BINDING_PROFILE_EXCHANGE_SUPPORT,
    WEBTRANSPORT_INNER_FRAMING_SUPPORT,
)


def test_framing_matrix_http_client_stream_rows_are_runtime_supported() -> None:
    note = _repo_root() / "docs" / "notes" / "tigrbl-framing-matrix.md"
    text = note.read_text(encoding="utf-8")

    assert "`http.stream.request`" in text
    assert "`https.stream.request`" in text
    assert "client_stream" in BINDING_PROFILE_EXCHANGE_SUPPORT["http.stream"]
    assert "client_stream" in BINDING_PROFILE_EXCHANGE_SUPPORT["https.stream"]
    assert set(APP_LEVEL_FRAMING_SUPPORT["http.stream"]) >= {
        "bytes",
        "binary",
        "text",
        "json",
        "ndjson",
    }


def test_framing_matrix_keeps_webtransport_outer_and_inner_framing_separate() -> None:
    assert APP_LEVEL_FRAMING_SUPPORT["webtransport"] == ("webtransport",)
    assert set(WEBTRANSPORT_INNER_FRAMING_SUPPORT["bidi_stream"]) >= {
        "bytes",
        "binary",
        "text",
        "json",
        "jsonrpc",
        "ndjson",
    }
    assert "jsonrpc" in WEBTRANSPORT_INNER_FRAMING_SUPPORT["datagram"]
    assert "ndjson" not in WEBTRANSPORT_INNER_FRAMING_SUPPORT["datagram"]


def test_framing_matrix_preserves_jsonrpc_ndjson_distinction() -> None:
    note = _repo_root() / "docs" / "notes" / "tigrbl-framing-matrix.md"
    text = note.read_text(encoding="utf-8")

    assert "ndjson-jsonrpc" in text
    assert "ndjson-jsonrpc" not in APP_LEVEL_FRAMING_SUPPORT["http.stream"]
    assert "ndjson-jsonrpc" not in WEBTRANSPORT_INNER_FRAMING_SUPPORT["bidi_stream"]


def _repo_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists() and (parent / ".ssot").exists():
            return parent
    raise RuntimeError("repo root not found")
