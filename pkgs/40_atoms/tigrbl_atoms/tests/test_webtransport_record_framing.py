from __future__ import annotations

from tigrbl_atoms.atoms.framing import (
    WebTransportRecordDecoder,
    decode_jsonrpc_records,
    encode_jsonrpc_record,
)


def test_webtransport_record_decoder_preserves_partial_and_multiple_records() -> None:
    first = {"jsonrpc": "2.0", "id": "1", "method": "Room.join", "params": {}}
    second = {"jsonrpc": "2.0", "id": "2", "method": "Chat.submit", "params": {}}
    payload = encode_jsonrpc_record(first) + encode_jsonrpc_record(second)
    decoder = WebTransportRecordDecoder()

    assert decoder.feed(payload[:3]) == []
    assert decoder.feed(payload[3:9]) == []
    assert decoder.feed(payload[9:]) == [first, second]
    assert decoder.remainder == b""


def test_webtransport_record_decoder_rejects_incomplete_final_record() -> None:
    decoder = WebTransportRecordDecoder()
    payload = encode_jsonrpc_record(
        {"jsonrpc": "2.0", "id": "1", "method": "Room.join"}
    )

    try:
        decoder.feed(payload[:-1], final=True)
    except ValueError as exc:
        assert "incomplete" in str(exc)
    else:
        raise AssertionError("incomplete final record was accepted")


def test_webtransport_record_decode_returns_remainder() -> None:
    message = {"jsonrpc": "2.0", "id": "1", "result": {"ok": True}}
    payload = encode_jsonrpc_record(message)
    records, remainder = decode_jsonrpc_records(payload + b"\x00\x00")
    assert records == [message]
    assert remainder == b"\x00\x00"
