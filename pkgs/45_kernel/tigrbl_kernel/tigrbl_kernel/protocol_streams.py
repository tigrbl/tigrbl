from __future__ import annotations

from typing import Any

_INITIATORS = {"client", "server"}
_DIRECTIONS = {"client_to_server", "server_to_client", "bidirectional", "control"}
_EXTENSION_CONTEXTS = {"connect", "tunnel", "websocket", "extension"}

_H11_REQUEST_BODY = {"request_body", "http_request_body", "http_body_request"}
_H11_RESPONSE_BODY = {"response_body", "http_response_body", "http_body_response"}
_H11_BODY = _H11_REQUEST_BODY | _H11_RESPONSE_BODY | {"http_body"}

_H2_REQUEST = {"request_stream", "h2_request_stream", "http2_request_stream"}
_H2_PUSH = {"push_stream", "h2_push_stream", "http2_push_stream"}

_H3_REQUEST = {"request_stream", "h3_request_stream", "http3_request_stream"}
_H3_PUSH = {"push_stream", "h3_push_stream", "http3_push_stream"}
_H3_CONTROL = {
    "control_stream",
    "qpack_encoder_stream",
    "qpack_decoder_stream",
    "h3_control_stream",
    "h3_qpack_encoder_stream",
    "h3_qpack_decoder_stream",
}

_WT_STREAM = {"webtransport_stream", "wt_stream"}
_WT_BIDI = {"bidi_stream", "webtransport_bidi_stream", "wt_bidi_stream"}
_WT_UNIDI_CLIENT = {
    "unidi_client_stream",
    "webtransport_unidi_client_stream",
    "wt_unidi_client_stream",
}
_WT_UNIDI_SERVER = {
    "unidi_server_stream",
    "webtransport_unidi_server_stream",
    "wt_unidi_server_stream",
}


def validate_protocol_stream_shape(
    *,
    protocol: str,
    carrier_kind: str,
    exchange: str,
    stream_initiator: str | None = None,
    direction: str | None = None,
    extension_context: str | None = None,
) -> dict[str, object]:
    """Validate protocol stream legality before app frame-codec dispatch."""

    selected_protocol = _normalize_protocol(protocol)
    selected_carrier = str(carrier_kind)
    selected_exchange = _normalize_exchange(exchange)
    selected_extension = _normalize_optional(extension_context)

    if selected_protocol == "h11":
        return _validate_h11(
            carrier_kind=selected_carrier,
            exchange=selected_exchange,
            stream_initiator=stream_initiator,
            direction=direction,
        )
    if selected_protocol == "h2":
        return _validate_h2(
            carrier_kind=selected_carrier,
            exchange=selected_exchange,
            stream_initiator=stream_initiator,
            direction=direction,
            extension_context=selected_extension,
        )
    if selected_protocol == "h3":
        return _validate_h3(
            carrier_kind=selected_carrier,
            exchange=selected_exchange,
            stream_initiator=stream_initiator,
            direction=direction,
            extension_context=selected_extension,
        )
    if selected_protocol == "webtransport":
        return _validate_webtransport(
            carrier_kind=selected_carrier,
            exchange=selected_exchange,
            stream_initiator=stream_initiator,
            direction=direction,
        )
    raise ValueError(f"unsupported stream protocol {protocol!r}")


def classify_plain_h3_stream(
    *,
    stream_type: str,
    initiator: str | None = None,
    extension_context: str | None = None,
) -> dict[str, object]:
    """Classify HTTP/3 streams without borrowing WebTransport lane semantics."""

    selected = str(stream_type)
    selected_extension = _normalize_optional(extension_context)
    if selected in _H3_REQUEST:
        return _projection(
            protocol="h3",
            carrier_kind="h3_request_stream",
            exchange="request_response",
            stream_initiator=_expect("stream_initiator", initiator, "client"),
            direction="bidirectional",
            app_payload=True,
            transport_stream=True,
            response_only=False,
            extension_context=selected_extension,
        )
    if selected in _H3_PUSH:
        return _projection(
            protocol="h3",
            carrier_kind="h3_push_stream",
            exchange="server_stream",
            stream_initiator=_expect("stream_initiator", initiator, "server"),
            direction="server_to_client",
            app_payload=True,
            transport_stream=True,
            response_only=True,
            extension_context=None,
        )
    if selected in _H3_CONTROL:
        if initiator is not None and str(initiator) not in _INITIATORS:
            raise ValueError("stream_initiator must be client or server")
        return _projection(
            protocol="h3",
            carrier_kind=selected,
            exchange="fire_and_forget",
            stream_initiator=str(initiator) if initiator is not None else None,
            direction="control",
            app_payload=False,
            transport_stream=True,
            response_only=False,
            extension_context=None,
        )
    if selected == "server_bidi_stream":
        if selected_extension is None:
            raise ValueError(
                "plain h3 server-initiated bidirectional streams require an extension context"
            )
        if selected_extension == "webtransport":
            raise ValueError("WebTransport-over-h3 is governed by WebTransport lanes")
        return _projection(
            protocol="h3",
            carrier_kind="extension_bidi_stream",
            exchange="bidirectional_stream",
            stream_initiator=_expect("stream_initiator", initiator, "server"),
            direction="bidirectional",
            app_payload=True,
            transport_stream=True,
            response_only=False,
            extension_context=selected_extension,
        )
    raise ValueError(f"unsupported plain h3 stream type {stream_type!r}")


def _validate_h11(
    *,
    carrier_kind: str,
    exchange: str,
    stream_initiator: str | None,
    direction: str | None,
) -> dict[str, object]:
    if carrier_kind not in _H11_BODY:
        raise ValueError(f"unsupported h11 stream carrier {carrier_kind!r}")
    if exchange == "client_stream" or carrier_kind in _H11_REQUEST_BODY:
        if carrier_kind in _H11_RESPONSE_BODY:
            raise ValueError("h11 response-body carrier cannot use client_stream")
        return _projection(
            protocol="h11",
            carrier_kind="http_request_body",
            exchange="client_stream",
            stream_initiator=_expect("stream_initiator", stream_initiator, "client"),
            direction=_expect("direction", direction, "client_to_server"),
            app_payload=True,
            transport_stream=False,
            response_only=False,
            extension_context=None,
        )
    if exchange == "server_stream" or carrier_kind in _H11_RESPONSE_BODY:
        if carrier_kind in _H11_REQUEST_BODY:
            raise ValueError("h11 request-body carrier cannot use server_stream")
        return _projection(
            protocol="h11",
            carrier_kind="http_response_body",
            exchange="server_stream",
            stream_initiator=_expect("stream_initiator", stream_initiator, "server"),
            direction=_expect("direction", direction, "server_to_client"),
            app_payload=True,
            transport_stream=False,
            response_only=False,
            extension_context=None,
        )
    raise ValueError("h11 does not provide native bidirectional application streams")


def _validate_h2(
    *,
    carrier_kind: str,
    exchange: str,
    stream_initiator: str | None,
    direction: str | None,
    extension_context: str | None,
) -> dict[str, object]:
    if carrier_kind in _H2_REQUEST:
        if exchange == "bidirectional_stream" and extension_context is None:
            raise ValueError("h2 bidirectional app streams require an extension context")
        if exchange not in {
            "request_response",
            "client_stream",
            "server_stream",
            "bidirectional_stream",
        }:
            raise ValueError(f"unsupported h2 request stream exchange {exchange!r}")
        return _projection(
            protocol="h2",
            carrier_kind="h2_request_stream",
            exchange=exchange,
            stream_initiator=_expect("stream_initiator", stream_initiator, "client"),
            direction=_expect("direction", direction, _h2_direction(exchange)),
            app_payload=True,
            transport_stream=True,
            response_only=False,
            extension_context=extension_context,
        )
    if carrier_kind in _H2_PUSH:
        if exchange != "server_stream":
            raise ValueError("h2 push streams are response-only server streams")
        return _projection(
            protocol="h2",
            carrier_kind="h2_push_stream",
            exchange="server_stream",
            stream_initiator=_expect("stream_initiator", stream_initiator, "server"),
            direction=_expect("direction", direction, "server_to_client"),
            app_payload=True,
            transport_stream=True,
            response_only=True,
            extension_context=None,
        )
    if stream_initiator == "server" and exchange == "bidirectional_stream":
        raise ValueError("plain h2 server-initiated bidirectional streams are invalid")
    raise ValueError(f"unsupported h2 stream carrier {carrier_kind!r}")


def _validate_h3(
    *,
    carrier_kind: str,
    exchange: str,
    stream_initiator: str | None,
    direction: str | None,
    extension_context: str | None,
) -> dict[str, object]:
    if carrier_kind in _H3_CONTROL:
        classified = classify_plain_h3_stream(
            stream_type=carrier_kind,
            initiator=stream_initiator,
        )
        if exchange != "fire_and_forget":
            raise ValueError("h3 control and qpack streams are not app exchange carriers")
        return classified
    if carrier_kind in _H3_PUSH:
        if exchange != "server_stream":
            raise ValueError("h3 push streams are response-only server streams")
        classified = classify_plain_h3_stream(
            stream_type=carrier_kind,
            initiator=stream_initiator,
        )
        if direction is not None and direction != classified["direction"]:
            raise ValueError("h3 push stream direction mismatch")
        return classified
    if carrier_kind in _H3_REQUEST:
        if exchange == "bidirectional_stream" and extension_context is None:
            raise ValueError("plain h3 bidirectional app streams require an extension context")
        if exchange not in {
            "request_response",
            "client_stream",
            "server_stream",
            "bidirectional_stream",
        }:
            raise ValueError(f"unsupported h3 request stream exchange {exchange!r}")
        return _projection(
            protocol="h3",
            carrier_kind="h3_request_stream",
            exchange=exchange,
            stream_initiator=_expect("stream_initiator", stream_initiator, "client"),
            direction=_expect("direction", direction, _h2_direction(exchange)),
            app_payload=True,
            transport_stream=True,
            response_only=False,
            extension_context=extension_context,
        )
    if carrier_kind == "server_bidi_stream":
        if extension_context is None:
            raise ValueError(
                "plain h3 server-initiated bidirectional streams require an extension context"
            )
        if extension_context == "webtransport":
            raise ValueError("WebTransport-over-h3 is governed by WebTransport lanes")
        return _projection(
            protocol="h3",
            carrier_kind="extension_bidi_stream",
            exchange="bidirectional_stream",
            stream_initiator=_expect("stream_initiator", stream_initiator, "server"),
            direction=_expect("direction", direction, "bidirectional"),
            app_payload=True,
            transport_stream=True,
            response_only=False,
            extension_context=extension_context,
        )
    raise ValueError(f"unsupported plain h3 stream carrier {carrier_kind!r}")


def _validate_webtransport(
    *,
    carrier_kind: str,
    exchange: str,
    stream_initiator: str | None,
    direction: str | None,
) -> dict[str, object]:
    if carrier_kind in _WT_STREAM:
        if exchange == "bidirectional_stream":
            carrier_kind = "bidi_stream"
        elif exchange == "client_stream":
            carrier_kind = "unidi_client_stream"
        elif exchange == "server_stream":
            carrier_kind = "unidi_server_stream"
    if carrier_kind in _WT_BIDI:
        initiator = _normalize_initiator(stream_initiator)
        if initiator is None:
            raise ValueError("WebTransport bidirectional streams require stream_initiator")
        return _projection(
            protocol="webtransport",
            carrier_kind="bidi_stream",
            exchange=_expect("exchange", exchange, "bidirectional_stream"),
            stream_initiator=initiator,
            direction=_expect("direction", direction, "bidirectional"),
            app_payload=True,
            transport_stream=True,
            response_only=False,
            extension_context=None,
        )
    if carrier_kind in _WT_UNIDI_CLIENT:
        return _projection(
            protocol="webtransport",
            carrier_kind="unidi_client_stream",
            exchange=_expect("exchange", exchange, "client_stream"),
            stream_initiator=_expect("stream_initiator", stream_initiator, "client"),
            direction=_expect("direction", direction, "client_to_server"),
            app_payload=True,
            transport_stream=True,
            response_only=False,
            extension_context=None,
        )
    if carrier_kind in _WT_UNIDI_SERVER:
        return _projection(
            protocol="webtransport",
            carrier_kind="unidi_server_stream",
            exchange=_expect("exchange", exchange, "server_stream"),
            stream_initiator=_expect("stream_initiator", stream_initiator, "server"),
            direction=_expect("direction", direction, "server_to_client"),
            app_payload=True,
            transport_stream=True,
            response_only=False,
            extension_context=None,
        )
    raise ValueError(f"unsupported WebTransport stream carrier {carrier_kind!r}")


def _normalize_protocol(protocol: str) -> str:
    token = str(protocol).lower().replace("_", "-")
    aliases = {
        "http/1.1": "h11",
        "http1.1": "h11",
        "http-1.1": "h11",
        "h11": "h11",
        "http/2": "h2",
        "http2": "h2",
        "h2": "h2",
        "http/3": "h3",
        "http3": "h3",
        "h3": "h3",
        "webtransport": "webtransport",
        "wt": "webtransport",
    }
    return aliases.get(token, token)


def _normalize_exchange(exchange: str) -> str:
    token = str(exchange)
    aliases = {
        "unary": "request_response",
        "duplex": "bidirectional_stream",
        "bidirectional": "bidirectional_stream",
    }
    return aliases.get(token, token)


def _normalize_optional(value: str | None) -> str | None:
    if value is None or value == "":
        return None
    token = str(value)
    if token not in _EXTENSION_CONTEXTS and token != "webtransport":
        raise ValueError(f"unsupported stream extension context {value!r}")
    return token


def _normalize_initiator(value: str | None) -> str | None:
    if value is None:
        return None
    token = str(value)
    if token not in _INITIATORS:
        raise ValueError("stream_initiator must be client or server")
    return token


def _expect(field: str, value: str | None, expected: str) -> str:
    if value is None:
        return expected
    token = str(value)
    if token != expected:
        raise ValueError(f"{field} must be {expected}")
    return token


def _h2_direction(exchange: str) -> str:
    if exchange == "client_stream":
        return "client_to_server"
    if exchange == "server_stream":
        return "server_to_client"
    return "bidirectional"


def _projection(
    *,
    protocol: str,
    carrier_kind: str,
    exchange: str,
    stream_initiator: str | None,
    direction: str,
    app_payload: bool,
    transport_stream: bool,
    response_only: bool,
    extension_context: str | None,
) -> dict[str, object]:
    if stream_initiator is not None and stream_initiator not in _INITIATORS:
        raise ValueError("stream_initiator must be client or server")
    if direction not in _DIRECTIONS:
        raise ValueError("direction must be client_to_server, server_to_client, bidirectional, or control")
    out: dict[str, object] = {
        "protocol": protocol,
        "carrier_kind": carrier_kind,
        "exchange": exchange,
        "stream_initiator": stream_initiator,
        "direction": direction,
        "family": "stream" if direction != "control" else "control",
        "app_payload": app_payload,
        "transport_stream": transport_stream,
        "response_only": response_only,
    }
    if extension_context is not None:
        out["extension_context"] = extension_context
    return out


__all__ = [
    "classify_plain_h3_stream",
    "validate_protocol_stream_shape",
]
