"""Planned conformance coverage for runtime frame codec semantics."""

import pytest


pytestmark = pytest.mark.skip(
    reason="Runtime frame codec conformance is not fully implemented yet."
)


def test_runtime_frame_codec_registry_static_t0() -> None:
    raise NotImplementedError


def test_runtime_frame_envelope_schema_static_t0() -> None:
    raise NotImplementedError


def test_framing_support_matrix_codec_coverage_t0() -> None:
    raise NotImplementedError


def test_jsonrpc_ndjson_distinction_static_t0() -> None:
    raise NotImplementedError


def test_webtransport_inner_codec_legality_static_t0() -> None:
    raise NotImplementedError


def test_runtime_json_codec_roundtrip_t1() -> None:
    raise NotImplementedError


def test_runtime_jsonrpc_codec_strict_validation_t1() -> None:
    raise NotImplementedError


def test_runtime_ndjson_codec_record_boundary_t1() -> None:
    raise NotImplementedError


def test_runtime_text_bytes_binary_codec_t1() -> None:
    raise NotImplementedError


def test_runtime_sse_codec_event_format_t1() -> None:
    raise NotImplementedError


def test_runtime_websocket_text_codec_adapter_t1() -> None:
    raise NotImplementedError


def test_webtransport_inner_codec_dispatch_t1() -> None:
    raise NotImplementedError


def test_binding_policy_to_codec_runtime_integration_t2() -> None:
    raise NotImplementedError


def test_framing_negative_corpus_runtime_t2() -> None:
    raise NotImplementedError


def test_websocket_jsonrpc_subprotocol_codec_t2() -> None:
    raise NotImplementedError


def test_webtransport_stream_inner_codec_runtime_t2() -> None:
    raise NotImplementedError


def test_webtransport_datagram_inner_codec_runtime_t2() -> None:
    raise NotImplementedError


def test_transport_demo_frame_codec_matrix_t2() -> None:
    raise NotImplementedError


def test_codec_errors_map_to_runtime_fail_closed_t2() -> None:
    raise NotImplementedError
