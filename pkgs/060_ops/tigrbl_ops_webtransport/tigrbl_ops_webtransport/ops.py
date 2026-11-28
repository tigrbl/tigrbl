from __future__ import annotations

from typing import Any, Dict, Mapping

_INITIATORS = {"client", "server"}
_BIDI_KIND = "bidi_stream"
_UNIDI_BY_INITIATOR = {
    "client": "unidi_client_stream",
    "server": "unidi_server_stream",
}


def _body(payload: Any) -> Mapping[str, Any]:
    if not isinstance(payload, Mapping):
        raise TypeError("WebTransport control-plane operations require mapping payloads")
    return payload


def _initiator(body: Mapping[str, Any]) -> str:
    value = str(body.get("initiator", body.get("opens", "client"))).lower()
    if value not in _INITIATORS:
        raise ValueError("WebTransport stream initiator must be 'client' or 'server'")
    return value


def _stream_id(body: Mapping[str, Any]) -> Any:
    return body.get("stream_id") or body.get("lane_id")


def _control_command(
    *,
    action: str,
    stream_kind: str | None = None,
    initiator: str | None = None,
    body: Mapping[str, Any],
) -> Dict[str, Any]:
    command: Dict[str, Any] = {
        "control_plane": "webtransport",
        "action": action,
    }
    session_id = body.get("session_id")
    if session_id is not None:
        command["session_id"] = session_id
    stream_id = _stream_id(body)
    if stream_id is not None:
        command["stream_id"] = stream_id
    if stream_kind is not None:
        command["stream_kind"] = stream_kind
        command["lane"] = stream_kind
    if initiator is not None:
        command["initiator"] = initiator
    purpose = body.get("purpose")
    if purpose is not None:
        command["purpose"] = str(purpose)
    framing = body.get("inner_framing") or body.get("framing")
    if framing is not None:
        command["inner_framing"] = str(framing)
    return command


async def open_bidi_stream(payload: Any) -> Dict[str, Any]:
    body = _body(payload)
    return _control_command(
        action="open_stream",
        stream_kind=_BIDI_KIND,
        initiator=_initiator(body),
        body=body,
    )


async def open_unidi_stream(payload: Any) -> Dict[str, Any]:
    body = _body(payload)
    initiator = _initiator(body)
    return _control_command(
        action="open_stream",
        stream_kind=_UNIDI_BY_INITIATOR[initiator],
        initiator=initiator,
        body=body,
    )


async def close_stream(payload: Any) -> Dict[str, Any]:
    body = _body(payload)
    command = _control_command(action="close_stream", body=body)
    code = body.get("code")
    if code is not None:
        command["code"] = int(code)
    reason = body.get("reason")
    if reason is not None:
        command["reason"] = str(reason)
    return command


async def close_session(payload: Any) -> Dict[str, Any]:
    body = _body(payload)
    command = _control_command(action="close_session", body=body)
    code = body.get("code")
    if code is not None:
        command["code"] = int(code)
    reason = body.get("reason")
    if reason is not None:
        command["reason"] = str(reason)
    return command
