from tigrbl_atoms.protocol_scope import scope_type as projected_scope_type

"""Request, transport, stream, and invocation identity at ingress."""

from collections.abc import Mapping
import re
from uuid import uuid4


def _opaque(value):
    return value if isinstance(value, str) and value.strip() else None


def _legacy_transport_session(scope, extensions, scope_type):
    unit = extensions.get("tigrcorn.unit")
    unit = unit if isinstance(unit, Mapping) else {}
    state = scope.get("ext")
    state = state if isinstance(state, Mapping) else {}
    lane = state.get("webtransport")
    lane = lane if isinstance(lane, Mapping) else {}
    if scope_type not in {"websocket", "webtransport"}:
        return None
    candidates = {
        str(value) for value in (scope.get("session_id"), lane.get("session_id"), unit.get("session_id"))
        if value is not None
    }
    if len(candidates) > 1 and "tigr.transport_identity" in extensions:
        raise ValueError("conflicting ASGI transport session identities")
    return next(
        (str(value) for value in (scope.get("session_id"), lane.get("session_id"), unit.get("session_id"))
         if value is not None),
        None,
    )


def _trusted_correlation(scope):
    state = scope.get("state")
    if not isinstance(state, Mapping) or state.get("tigrbl_trusted_correlation") is not True:
        return None
    values = [value for key, value in scope.get("headers", ()) if key.lower() == b"x-correlation-id"]
    if len(values) == 1 and re.fullmatch(rb"[A-Za-z0-9_.:-]{1,128}", values[0]):
        return values[0].decode("ascii")
    return None


def _trace_identity(scope):
    values = [value for key, value in scope.get("headers", ()) if key.lower() == b"traceparent"]
    if len(values) == 1 and re.fullmatch(rb"00-[a-f0-9]{32}-[a-f0-9]{16}-[a-f0-9]{2}", values[0]):
        _, trace_id, parent_id, flags = values[0].decode("ascii").split("-")
        if int(trace_id, 16) and int(parent_id, 16):
            return {
                "trace_id": trace_id, "parent_span_id": parent_id,
                "span_id": uuid4().hex[:16], "trace_flags": flags,
            }
    return {"trace_id": uuid4().hex, "span_id": uuid4().hex[:16]}


def prepare_transport_identity(scope):
    """Resolve carrier metadata once, retaining WT identity across dispatches."""
    scope_type = projected_scope_type(scope)
    if scope_type not in {"http", "websocket", "webtransport"}:
        return {}
    state = scope.setdefault("state", {})
    if not isinstance(state, dict):
        state = {}
        scope["state"] = state
    existing = state.get("_tigrbl_transport_identity")
    if isinstance(existing, dict):
        return existing.copy()

    extensions = scope.get("extensions")
    extensions = extensions if isinstance(extensions, Mapping) else {}
    normalized = scope.get("ext")
    normalized = normalized if isinstance(normalized, Mapping) else {}
    metadata = extensions.get("tigr.transport_identity", normalized.get("transport_identity"))
    legacy_session = _legacy_transport_session(scope, extensions, scope_type)
    identity = {}
    if metadata is not None:
        if not isinstance(metadata, Mapping) or type(metadata.get("version")) not in {int, float} or metadata["version"] != 1:
            identity["identity_diagnostic"] = "unsupported_transport_identity"
        else:
            connection = _opaque(metadata.get("connection_id"))
            request = _opaque(metadata.get("request_id"))
            session = _opaque(metadata.get("transport_session_id"))
            if not connection or (scope_type == "http" and (not request or session)) or (
                scope_type != "http" and not session
            ):
                identity["identity_diagnostic"] = "invalid_transport_identity"
            elif legacy_session and session != legacy_session:
                raise ValueError("conflicting ASGI transport session identities")
            else:
                identity["connection_id"] = connection
                if request:
                    identity["request_id" if scope_type == "http" else "opening_request_id"] = request
                if session:
                    identity["transport_session_id"] = session
                carrier_stream = metadata.get("http_stream_id")
                if isinstance(carrier_stream, str) and re.fullmatch(r"0|[1-9][0-9]*", carrier_stream):
                    identity["http_stream_id"] = carrier_stream

    if scope_type == "http":
        identity.setdefault("request_id", uuid4().hex)
        identity["correlation_id"] = _trusted_correlation(scope) or uuid4().hex
        identity.update(_trace_identity(scope))
    else:
        identity.setdefault("transport_session_id", legacy_session or uuid4().hex)
        if scope_type == "webtransport":
            identity["correlation_id"] = uuid4().hex
    state["_tigrbl_transport_identity"] = identity.copy()
    return identity


def stream_correlation_id(correlations, stream_id):
    key = str(stream_id)
    correlation = correlations.get(key)
    if correlation is None:
        correlation = correlations[key] = uuid4().hex
    return correlation


def webtransport_lane_identity(scope, message, carrier):
    """Resolve identity for one lane event without modifying its wire fields."""
    identity = {
        key: value for key, value in carrier.items()
        if key not in {"stream_id", "stream_correlation_id", "datagram_id"}
    }
    session = message.get("session_id")
    if session is not None and str(session) != identity.get("transport_session_id"):
        # An ASGI adapter with the canonical extension declares the owner.
        extensions = scope.get("extensions") or {}
        if isinstance(extensions, Mapping) and "tigr.transport_identity" in extensions:
            raise ValueError("WebTransport event belongs to another session")
    if "datagram_id" in message:
        identity["datagram_id"] = message["datagram_id"]
    elif "stream_id" in message:
        stream_id = message["stream_id"]
        state = scope["state"].setdefault("_tigrbl_stream_correlations", {})
        identity.update(stream_id=stream_id, stream_correlation_id=stream_correlation_id(state, stream_id))
    return identity


def invocation_identity(carrier, *, websocket=False, rpc_envelope=None):
    identity = dict(carrier)
    if rpc_envelope is not None and "id" in rpc_envelope:
        identity["rpc_id"] = rpc_envelope["id"]
    identity.setdefault("invocation_id", uuid4().hex)
    if websocket:
        identity["request_id"] = uuid4().hex
        identity["correlation_id"] = uuid4().hex
    if "attempt_id" not in identity:
        identity["attempt_id"] = uuid4().hex
        identity.setdefault("trace_id", uuid4().hex)
        if "span_id" in identity:
            identity["parent_span_id"] = identity["span_id"]
        identity["span_id"] = uuid4().hex[:16]
    return identity
