from __future__ import annotations

import asyncio
from collections.abc import Mapping
from dataclasses import dataclass
import inspect
import json
import uuid as _uuid
import decimal as _dc
import datetime as _dt
import zlib
from importlib import import_module
from typing import Any, ClassVar
from operator import attrgetter
from types import SimpleNamespace
from urllib.parse import unquote_plus

from tigrbl_atoms._ctx import _ctx_view
from tigrbl_core.config.constants import __JSONRPC_DEFAULT_ENDPOINT_MAPPINGS__
from tigrbl_atoms.types import build_error_ctx, error_phase_for, select_error_edge
from tigrbl_atoms.atoms.wire.validate_in import _coerce_if_needed
from tigrbl_kernel.models import (
    KernelPlan,
    OpKey,
    PackedHotSection,
    PackedHotSectionDirectory,
    PackedKernel,
)
from tigrbl_typing.status.exceptions import HTTPException
from tigrbl_typing.phases import normalize_phase
from tigrbl_typing.status.mappings import status as _status
from tigrbl_atoms._request import Request

from .base import ExecutorBase
from .types import HotCtx, _Ctx

_HOT_RUNNER_GENERIC = 0
_HOT_RUNNER_LINEAR_DIRECT = 1
_HOT_RUNNER_COMPILED_PARAM = 2
_HOT_RUNNER_WS_UNARY_TEXT = 3
_DIRECT_INVOKE_STEP = 0
_DIRECT_INVOKE_RUN = 1
_DIRECT_INVOKE_RUN_WITH_NONE = 2
_DIRECT_INVOKE_RUN_WITH_DEP = 3
_TRANSPORT_KIND_GENERIC = 0
_TRANSPORT_KIND_REST = 1
_TRANSPORT_KIND_JSONRPC = 2
_TRANSPORT_KIND_CHANNEL = 3
_PARAM_SOURCE_BODY = 1
_PARAM_SOURCE_QUERY = 2
_PARAM_SOURCE_PATH = 4
_PARAM_SOURCE_HEADER = 8
_DECODE_STRATEGY_GENERIC_HASHED = 0
_DECODE_STRATEGY_BODY_ONLY_MAPPING = 1
_DECODE_STRATEGY_BODY_ONLY_SINGLE_FIELD = 2
_DECODER_NONE = 0
_DECODER_STR = 1
_DECODER_INT = 2
_DECODER_FLOAT = 3
_DECODER_BOOL = 4
_DECODER_UUID = 5
_DECODER_DECIMAL = 6
_DECODER_DATETIME = 7
_DECODER_DATE = 8
_DECODER_TIME = 9
_QUERY_VALUE_HAS_PLUS = 1
_QUERY_VALUE_HAS_PERCENT = 2
_WRAPPER_KEYS = frozenset({"data", "payload", "body", "item"})
_HTTP_METHOD_ID_BY_NAME = {
    "GET": 1,
    "HEAD": 2,
    "POST": 3,
    "PUT": 4,
    "PATCH": 5,
    "DELETE": 6,
    "OPTIONS": 7,
    "TRACE": 8,
    "CONNECT": 9,
}


@dataclass(frozen=True, slots=True)
class _CompiledInputDescriptor:
    slot_id: int
    lookup_name: str
    source_mask: int
    decoder_id: int
    max_length: int
    lookup_hash: int
    header_hash: int


@dataclass(frozen=True, slots=True)
class _CompiledFieldPlan:
    slot_id: int
    field_name: str
    required: bool
    nullable: bool | None
    py_type: Any
    coerce: bool
    max_length: int
    validator: Any
    in_enabled: bool
    is_virtual: bool
    default_factory: Any


@dataclass(frozen=True, slots=True)
class _CompiledParamPlan:
    field_names: tuple[str, ...]
    field_index: Mapping[str, int]
    field_plans: tuple[_CompiledFieldPlan, ...]
    descriptor_plans: tuple[_CompiledInputDescriptor, ...]
    strategy_kind: int
    strategy_rows: tuple[tuple[int, str, int, int], ...]
    assemble_order: tuple[int, ...]
    body_lookup_names: frozenset[str]
    reserved_input_keys: frozenset[str]
    needs_query: bool
    needs_header: bool
    needs_path: bool


class _DirectWebSocketUnary:
    __slots__ = (
        "_receive",
        "_send",
        "_buffered",
        "_buffered_text",
        "_buffered_bytes",
        "_path",
        "_path_params",
        "_scope",
        "accepted",
        "closed",
        "sent_payload",
    )

    def __init__(
        self,
        *,
        receive: Any,
        send: Any,
        path: str,
        path_params: Mapping[str, Any] | None,
        buffered_message: Mapping[str, Any] | None,
    ) -> None:
        self._receive = receive
        self._send = send
        self._buffered = None
        self._buffered_text = None
        self._buffered_bytes = None
        self._path = path
        self._scope = None
        if isinstance(buffered_message, Mapping):
            if buffered_message.get("type") == "websocket.receive":
                text = buffered_message.get("text")
                if isinstance(text, str):
                    self._buffered_text = text
                else:
                    raw = buffered_message.get("bytes")
                    if isinstance(raw, bytes):
                        self._buffered_bytes = raw
                    elif isinstance(raw, bytearray):
                        self._buffered_bytes = bytes(raw)
                    else:
                        self._buffered = (
                            buffered_message
                            if isinstance(buffered_message, dict)
                            else dict(buffered_message)
                        )
            else:
                self._buffered = (
                    buffered_message
                    if isinstance(buffered_message, dict)
                    else dict(buffered_message)
                )
        if isinstance(path_params, dict):
            self._path_params = path_params
        elif path_params:
            self._path_params = dict(path_params)
        else:
            self._path_params = None
        self.accepted = False
        self.closed = False
        self.sent_payload = False

    @property
    def scope(self) -> dict[str, Any]:
        scope = self._scope
        if scope is None:
            scope = {"type": "websocket", "path": self._path}
            self._scope = scope
        return scope

    @property
    def path_params(self) -> dict[str, Any]:
        path_params = self._path_params
        if path_params is None:
            path_params = {}
            self._path_params = path_params
        return path_params

    async def accept(self, subprotocol: str | None = None) -> None:
        if self.accepted:
            return
        if callable(self._send):
            message = {"type": "websocket.accept"}
            if subprotocol is not None:
                message["subprotocol"] = subprotocol
            await self._send(message)
        self.accepted = True

    async def receive(self) -> dict[str, Any]:
        if self._buffered is not None:
            message = self._buffered
            self._buffered = None
            return message
        if callable(self._receive):
            message = await self._receive()
            return dict(message) if isinstance(message, Mapping) else {"type": "websocket.disconnect", "code": 1006}
        return {"type": "websocket.disconnect", "code": 1006}

    async def receive_text(self) -> str:
        if self._buffered_text is not None:
            text = self._buffered_text
            self._buffered_text = None
            return text
        if self._buffered_bytes is not None:
            raw = self._buffered_bytes
            self._buffered_bytes = None
            return raw.decode("utf-8")
        message = await self.receive()
        if message.get("type") == "websocket.disconnect":
            self.closed = True
            raise RuntimeError("websocket disconnected")
        text = message.get("text")
        if isinstance(text, str):
            return text
        raw = message.get("bytes")
        if isinstance(raw, (bytes, bytearray)):
            return bytes(raw).decode("utf-8")
        return ""

    async def send_text(self, data: str) -> None:
        await self.accept()
        if callable(self._send):
            await self._send({"type": "websocket.send", "text": data})
        self.sent_payload = True

    async def send_bytes(self, data: bytes) -> None:
        await self.accept()
        if callable(self._send):
            payload = data if isinstance(data, bytes) else bytes(data)
            await self._send({"type": "websocket.send", "bytes": payload})
        self.sent_payload = True

    async def close(self, code: int = 1000) -> None:
        if self.closed:
            return
        await self.accept()
        if callable(self._send):
            await self._send({"type": "websocket.close", "code": code})
        self.closed = True


class PackedPlanExecutor(ExecutorBase):
    """Executes packed kernel plans via kernel-attached packed execution hooks."""

    name: ClassVar[str] = "packed"
    _PHASE_EXECUTION_ORDER: ClassVar[tuple[str, ...]] = (
        "INGRESS_BEGIN",
        "INGRESS_PARSE",
        "INGRESS_DISPATCH",
        "PRE_TX_BEGIN",
        "START_TX",
        "PRE_HANDLER",
        "HANDLER",
        "POST_HANDLER",
        "PRE_COMMIT",
        "TX_COMMIT",
        "POST_COMMIT",
        "POST_RESPONSE",
        "EGRESS_SHAPE",
        "EGRESS_FINALIZE",
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._program_segments_cache: dict[
            tuple[int, int], tuple[tuple[int, ...], tuple[int, ...]]
        ] = {}
        self._request_program_cache: dict[tuple[int, str, str], int] = {}
        self._templated_route_cache: dict[int, tuple[tuple[str, Any, int], ...]] = {}
        self._opview_cache: dict[tuple[int, int], Any] = {}
        self._segment_steps_cache: dict[int, tuple[tuple[int, ...], ...]] = {}
        self._segment_runners_cache: dict[int, tuple[Any, ...]] = {}
        self._program_error_segments_cache: dict[
            tuple[int, int], tuple[tuple[int, ...], Mapping[str, tuple[int, ...]]]
        ] = {}
        self._program_runner_cache: dict[tuple[int, ...], Any] = {}
        self._program_runner_mode_cache: dict[tuple[int, int, int], Any] = {}
        self._db_acquire_cache: dict[tuple[int, int], Any] = {}
        self._hot_exact_route_cache: dict[int, Mapping[int, tuple[int, int]]] = {}
        self._hot_exact_route_verify_cache: dict[
            int, Mapping[int, Mapping[int, tuple[tuple[str, int], ...]]]
        ] = {}
        self._hot_exact_jsonrpc_cache: dict[
            int, Mapping[str, Mapping[str, tuple[int, str, str]]]
        ] = {}
        self._hot_exact_websocket_route_cache: dict[
            int, Mapping[tuple[str, str], int]
        ] = {}
        self._param_shape_decode_strategy_cache: dict[
            tuple[int, int, int], tuple[int, tuple[tuple[int, str, int, int], ...]]
        ] = {}
        self._compiled_param_plan_cache: dict[
            tuple[int, int, int], _CompiledParamPlan
        ] = {}
        self._model_row_serializer_cache: dict[type[Any], tuple[str, ...]] = {}

    @classmethod
    def _resolve_transport_senders(cls):
        from tigrbl_runtime.channel import channel_senders

        return channel_senders()

    def should_skip_channel_prelude(
        self,
        *,
        runtime: Any,
        env: Any,
        ctx: Any,
        plan: Any,
        packed_plan: Any | None = None,
    ) -> bool:
        del runtime
        if not isinstance(plan, KernelPlan) or not isinstance(packed_plan, PackedKernel):
            return False
        scope = getattr(env, "scope", {}) or {}
        if str(scope.get("type") or "") != "websocket":
            return False
        protocol = str(scope.get("scheme") or "ws").lower()
        path = str(scope.get("path") or "")
        if not path:
            return False
        program_id = self._resolve_program_id_from_exact_websocket(
            plan, packed_plan, protocol, path
        )
        if program_id < 0:
            return False
        hot_op_plan = (
            packed_plan.hot_op_plans[program_id]
            if program_id < len(getattr(packed_plan, "hot_op_plans", ()))
            else None
        )
        if (
            self._resolve_program_hot_runner_id(
                packed_plan, program_id, hot_op_plan
            )
            != _HOT_RUNNER_WS_UNARY_TEXT
        ):
            return False
        if isinstance(ctx, Mapping):
            temp = ctx.get("temp")
            if not isinstance(temp, dict):
                temp = {}
                try:
                    ctx["temp"] = temp
                except Exception:
                    temp = None
            if isinstance(temp, dict):
                temp["program_id"] = program_id
        return True

    @classmethod
    def _resolve_error_helpers(cls):
        from tigrbl_runtime.runtime.status import (
            StatusDetailError,
            create_standardized_error,
        )

        return StatusDetailError, create_standardized_error

    @staticmethod
    def _is_persistence_exception(exc: BaseException) -> bool:
        from tigrbl_typing.status.utils import is_persistence_exception

        return is_persistence_exception(exc)

    @staticmethod
    def _jsonrpc_error_payload(
        ctx: _Ctx,
        status_code: int,
        detail: Any,
        *,
        sanitize_detail: bool = False,
    ) -> dict[str, Any] | None:
        temp = getattr(ctx, "temp", None)
        if not isinstance(temp, dict):
            return None

        hot = dict.get(temp, "hot_ctx")
        rpc_id = temp.get("jsonrpc_request_id")
        is_jsonrpc = "jsonrpc_request_id" in temp
        if isinstance(hot, HotCtx):
            if hot.dispatch_jsonrpc_request_id is not None:
                rpc_id = hot.dispatch_jsonrpc_request_id
                is_jsonrpc = True
            protocol = hot.dispatch_binding_protocol or hot.route_protocol or hot.protocol
            if str(protocol).endswith(".jsonrpc"):
                is_jsonrpc = True
            for payload in (hot.route_rpc_envelope, hot.dispatch_rpc_envelope):
                if isinstance(payload, dict) and payload.get("jsonrpc") == "2.0":
                    is_jsonrpc = True
                    if rpc_id is None:
                        rpc_id = payload.get("id")
        if not is_jsonrpc:
            for section_key in ("route", "dispatch"):
                section = temp.get(section_key)
                if not isinstance(section, Mapping):
                    continue
                for payload_key in ("rpc_envelope", "rpc"):
                    payload = section.get(payload_key)
                    if isinstance(payload, Mapping) and payload.get("jsonrpc") == "2.0":
                        is_jsonrpc = True
                        if rpc_id is None:
                            rpc_id = payload.get("id")

        if not is_jsonrpc:
            return None

        from tigrbl_typing.status.mappings import ERROR_MESSAGES, _HTTP_TO_RPC

        if sanitize_detail:
            status_code = 500
            detail = {"detail": "Internal error"}

        rpc_code = _HTTP_TO_RPC.get(int(status_code), -32603)
        data = dict(detail) if isinstance(detail, Mapping) else {"detail": detail}
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": rpc_code,
                "message": ERROR_MESSAGES.get(rpc_code, "Internal error"),
                "data": data,
            },
            "id": rpc_id,
        }

    @staticmethod
    def _reject_jsonrpc_wrapper_keys(
        payload: Any, *, field_names: tuple[str, ...]
    ) -> None:
        allowed_wrapper_keys = set(field_names) & set(_WRAPPER_KEYS)

        def _check_mapping(item: Mapping[str, Any]) -> None:
            disallowed = sorted(
                key
                for key in item
                if key in _WRAPPER_KEYS and key not in allowed_wrapper_keys
            )
            if disallowed:
                raise HTTPException(
                    status_code=422,
                    detail={
                        "reason": "Wrapper keys are not allowed; params must match the operation schema.",
                        "disallowed_keys": disallowed,
                    },
                )

        if isinstance(payload, Mapping):
            _check_mapping(payload)
            return

        if isinstance(payload, list):
            for item in payload:
                if isinstance(item, Mapping):
                    _check_mapping(item)

    async def _execute_jsonrpc_batch(
        self,
        ctx: _Ctx,
        hot: HotCtx,
        batch_payload: list[Any],
    ) -> list[dict[str, Any]]:
        router_or_app = getattr(ctx, "router", None) or getattr(ctx, "app", None)
        scope = dict(hot.raw_scope or {}) if isinstance(hot.raw_scope, Mapping) else {}
        if scope:
            scope["method"] = "POST"
            headers = list(scope.get("headers", ()) or ())
            if not any(
                bytes(key).lower() == b"content-type"
                for key, _value in headers
                if isinstance(key, (bytes, bytearray))
            ):
                headers.append((b"content-type", b"application/json"))
            scope["headers"] = headers
        responses: list[dict[str, Any]] = []

        for item in batch_payload:
            if not isinstance(item, Mapping):
                responses.append(
                    {
                        "jsonrpc": "2.0",
                        "error": {"code": -32600, "message": "Invalid Request"},
                        "id": None,
                    }
                )
                continue

            rpc_id = item.get("id")
            method = item.get("method")
            if not isinstance(method, str):
                responses.append(
                    {
                        "jsonrpc": "2.0",
                        "error": {"code": -32601, "message": "Method not found"},
                        "id": rpc_id,
                    }
                )
                continue

            if not callable(router_or_app) or not scope:
                responses.append(
                    {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32603,
                            "message": "Internal error",
                            "data": {"detail": "RPC invoker unavailable."},
                        },
                        "id": rpc_id,
                    }
                )
                continue

            body = json.dumps(dict(item), separators=(",", ":")).encode("utf-8")
            messages = [{"type": "http.request", "body": body, "more_body": False}]
            sent: list[dict[str, Any]] = []

            try:
                async def _receive() -> dict[str, Any]:
                    if messages:
                        return messages.pop(0)
                    return {"type": "http.request", "body": b"", "more_body": False}

                async def _send(message: dict[str, Any]) -> None:
                    sent.append(dict(message))

                await router_or_app(dict(scope), _receive, _send)
            except Exception as exc:
                responses.append(
                    {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32603,
                            "message": "Internal error",
                            "data": {"detail": str(exc)},
                        },
                        "id": rpc_id,
                    }
                )
                continue

            body_parts = [
                message.get("body", b"")
                for message in sent
                if message.get("type") == "http.response.body"
            ]
            response_body = b"".join(
                bytes(part) if isinstance(part, (bytes, bytearray)) else b""
                for part in body_parts
            )
            if not response_body:
                continue
            try:
                decoded = json.loads(response_body.decode("utf-8"))
            except Exception:
                decoded = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": "Internal error",
                        "data": {"detail": response_body.decode("utf-8", errors="replace")},
                    },
                    "id": rpc_id,
                }
            if isinstance(decoded, Mapping):
                response = dict(decoded)
                if response.get("id") is None:
                    response["id"] = rpc_id
                error = response.get("error")
                if isinstance(error, dict):
                    data = error.get("data")
                    detail = data.get("detail") if isinstance(data, Mapping) else None
                    if detail == "No runtime operation matched request.":
                        error["code"] = -32601
                        error["message"] = "Method not found"
                responses.append(response)
                continue
            responses.append({"jsonrpc": "2.0", "result": decoded, "id": rpc_id})

        return responses

    @staticmethod
    def _hot_block_view(packed: PackedKernel) -> Mapping[str, Any]:
        view = getattr(packed, "hot_block_view", None)
        return view if isinstance(view, Mapping) else {}

    @staticmethod
    def _hot_block_sections(packed: PackedKernel) -> PackedHotSectionDirectory | None:
        sections = getattr(packed, "hot_block_sections", None)
        return (
            sections
            if isinstance(sections, PackedHotSectionDirectory)
            else None
        )

    @classmethod
    def _hot_section(cls, packed: PackedKernel, key: str) -> PackedHotSection | None:
        directory = cls._hot_block_sections(packed)
        if directory is None:
            return None
        return directory.get(key)

    @classmethod
    def _hot_array(cls, packed: PackedKernel, key: str, fallback: tuple[Any, ...] | tuple[int, ...] | tuple[str, ...]) -> tuple[Any, ...]:
        view = cls._hot_block_view(packed)
        values = view.get(key)
        if isinstance(values, tuple):
            return values
        if isinstance(values, list):
            return tuple(values)
        return fallback

    @classmethod
    def _hot_int_at(
        cls,
        packed: PackedKernel,
        key: str,
        index: int,
        fallback: tuple[int, ...] | tuple[Any, ...],
    ) -> int | None:
        section = cls._hot_section(packed, key)
        if section is not None:
            if 0 <= index < int(section.count):
                return section.get_int(index)
            return None
        if 0 <= index < len(fallback):
            return int(fallback[index])
        return None

    @classmethod
    def _hot_count(
        cls,
        packed: PackedKernel,
        key: str,
        fallback: tuple[int, ...] | tuple[Any, ...] | tuple[str, ...],
    ) -> int:
        section = cls._hot_section(packed, key)
        if section is not None:
            return int(section.count)
        return len(fallback)

    @staticmethod
    def _stable_name_hash64(value: str, *, lowercase: bool = False) -> int:
        normalized = value.lower() if lowercase else value
        encoded = normalized.encode("utf-8")
        lo = zlib.crc32(encoded) & 0xFFFFFFFF
        hi = zlib.crc32(encoded, 0x9E3779B9) & 0xFFFFFFFF
        return (hi << 32) | lo

    @classmethod
    def _http_method_id(cls, method: str) -> int:
        normalized = str(method or "").upper()
        cached = _HTTP_METHOD_ID_BY_NAME.get(normalized)
        if cached is not None:
            return cached
        return 1024 + (cls._stable_name_hash64(normalized) & 0xFFFF)

    @staticmethod
    def _coerce_header_pairs(
        raw_scope: Mapping[str, Any] | None,
    ) -> tuple[tuple[bytes, bytes], ...]:
        if not isinstance(raw_scope, Mapping):
            return ()
        raw_headers = raw_scope.get("headers", ())
        out: list[tuple[bytes, bytes]] = []
        for key, value in raw_headers or ():
            if not isinstance(key, (bytes, bytearray)):
                continue
            if not isinstance(value, (bytes, bytearray)):
                continue
            out.append((bytes(key).lower(), bytes(value)))
        return tuple(out)

    @staticmethod
    def _content_type_from_raw_headers(raw_headers: tuple[tuple[bytes, bytes], ...]) -> str:
        for key, value in reversed(raw_headers):
            if key == b"content-type":
                return value.decode("latin-1").lower()
        return ""

    @staticmethod
    def _decode_scalar(value: Any, decoder_id: int) -> Any:
        if value is None or decoder_id == _DECODER_NONE:
            return value
        if isinstance(value, bytes):
            raw_text = value.decode("utf-8")
        else:
            raw_text = value if isinstance(value, str) else str(value)
        text = raw_text.strip()
        if decoder_id == _DECODER_STR:
            return raw_text if isinstance(value, str) else text
        if decoder_id == _DECODER_INT:
            return int(text)
        if decoder_id == _DECODER_FLOAT:
            return float(text)
        if decoder_id == _DECODER_BOOL:
            lowered = text.lower()
            if lowered in {"true", "1", "yes", "y", "on"}:
                return True
            if lowered in {"false", "0", "no", "n", "off"}:
                return False
            return value
        if decoder_id == _DECODER_UUID:
            return _uuid.UUID(text)
        if decoder_id == _DECODER_DECIMAL:
            return _dc.Decimal(text)
        if decoder_id == _DECODER_DATETIME:
            return _dt.datetime.fromisoformat(text)
        if decoder_id == _DECODER_DATE:
            return _dt.date.fromisoformat(text)
        if decoder_id == _DECODER_TIME:
            return _dt.time.fromisoformat(text)
        return value

    @staticmethod
    def _parse_query_spans(raw_query: bytes) -> tuple[tuple[int, int, int, int], ...]:
        if not raw_query:
            return ()
        out: list[tuple[int, int, int, int]] = []
        cursor = 0
        for chunk in raw_query.split(b"&"):
            chunk_start = cursor
            cursor += len(chunk) + 1
            if not chunk:
                continue
            raw_key, _, raw_value = chunk.partition(b"=")
            try:
                key = unquote_plus(raw_key.decode("latin-1"))
            except Exception:
                continue
            flags = 0
            if b"+" in raw_value:
                flags |= _QUERY_VALUE_HAS_PLUS
            if b"%" in raw_value:
                flags |= _QUERY_VALUE_HAS_PERCENT
            value_start = chunk_start + len(raw_key) + (1 if b"=" in chunk else 0)
            value_end = chunk_start + len(chunk)
            out.append(
                (
                    PackedPlanExecutor._stable_name_hash64(key),
                    value_start,
                    value_end,
                    flags,
                )
            )
        return tuple(out)

    @staticmethod
    def _decode_query_span_value(
        raw_query: bytes, start: int, end: int, flags: int
    ) -> str:
        raw_value = raw_query[start:end]
        text = raw_value.decode("latin-1")
        if flags & (_QUERY_VALUE_HAS_PLUS | _QUERY_VALUE_HAS_PERCENT):
            return unquote_plus(text)
        return text

    @classmethod
    def _ensure_hot_request(cls, ctx: _Ctx, hot: HotCtx) -> Request | Any | None:
        request = getattr(ctx, "request", None)
        if request is not None:
            return request
        raw_scope = hot.raw_scope
        if not isinstance(raw_scope, Mapping):
            return None
        request = Request(dict(raw_scope), app=getattr(ctx, "app", None))
        if hot.body_bytes is not None:
            request.body = hot.body_bytes
        ctx.request = request
        return request

    @staticmethod
    async def _ensure_body_bytes(ctx: _Ctx, hot: HotCtx) -> bytes:
        if isinstance(hot.body_bytes, bytes):
            return hot.body_bytes
        body = getattr(ctx, "body", None)
        if isinstance(body, bytes):
            hot.body_bytes = body
            hot.body_view = memoryview(body)
            return body
        if isinstance(body, bytearray):
            hot.body_bytes = bytes(body)
            hot.body_view = memoryview(hot.body_bytes)
            return hot.body_bytes
        if isinstance(body, memoryview):
            hot.body_bytes = body.tobytes()
            hot.body_view = memoryview(hot.body_bytes)
            return hot.body_bytes
        if hot.scope_type != "http" or not callable(hot.raw_receive):
            hot.body_bytes = b""
            hot.body_view = memoryview(hot.body_bytes)
            return hot.body_bytes
        message = await hot.raw_receive()
        chunks: list[bytes] = []
        while isinstance(message, dict) and message.get("type") == "http.request":
            chunk = message.get("body", b"")
            if isinstance(chunk, (bytes, bytearray)):
                chunks.append(bytes(chunk))
            if not bool(message.get("more_body", False)):
                break
            message = await hot.raw_receive()
        hot.body_bytes = b"".join(chunks)
        hot.body_view = memoryview(hot.body_bytes)
        if hot.body_bytes:
            ctx.body = hot.body_bytes
        return hot.body_bytes

    @classmethod
    def _body_hash_items(cls, body: Any) -> Mapping[int, Any]:
        if not isinstance(body, Mapping):
            return {}
        out: dict[int, Any] = {}
        for key, value in body.items():
            if not isinstance(key, str):
                continue
            out[cls._stable_name_hash64(key)] = value
        return out

    @classmethod
    def _header_hash_pairs(
        cls, raw_headers: tuple[tuple[bytes, bytes], ...]
    ) -> tuple[tuple[int, bytes], ...]:
        return tuple(
            (
                cls._stable_name_hash64(
                    key_bytes.decode("latin-1"), lowercase=True
                ),
                raw_value,
            )
            for key_bytes, raw_value in raw_headers
        )

    @classmethod
    def _path_hash_items(cls, path_params: Mapping[str, Any] | None) -> Mapping[int, Any]:
        if not isinstance(path_params, Mapping):
            return {}
        out: dict[int, Any] = {}
        for key, value in path_params.items():
            out[cls._stable_name_hash64(str(key))] = value
        return out

    @classmethod
    def _lookup_query_value(
        cls,
        raw_query: bytes,
        query_spans: tuple[tuple[int, int, int, int], ...],
        target_hash: int,
    ) -> tuple[bool, Any]:
        for item_hash, value_start, value_end, flags in query_spans:
            if int(item_hash) != int(target_hash):
                continue
            return True, cls._decode_query_span_value(
                raw_query, int(value_start), int(value_end), int(flags)
            )
        return False, None

    @staticmethod
    def _lookup_hashed_mapping(
        items: Mapping[int, Any], target_hash: int
    ) -> tuple[bool, Any]:
        if int(target_hash) in items:
            return True, items[int(target_hash)]
        return False, None

    @staticmethod
    def _lookup_hashed_pairs(
        items: tuple[tuple[int, bytes], ...], target_hash: int
    ) -> tuple[bool, Any]:
        for item_hash, raw_value in items:
            if int(item_hash) == int(target_hash):
                return True, raw_value.decode("latin-1")
        return False, None

    @classmethod
    def _param_shape_descriptor_slice(
        cls,
        packed: PackedKernel,
        param_shape_id: int,
    ) -> tuple[int, int]:
        offsets_fallback = tuple(getattr(packed, "param_shape_offsets", ()) or ())
        lengths_fallback = tuple(getattr(packed, "param_shape_lengths", ()) or ())
        if not (0 <= param_shape_id < cls._hot_count(packed, "param_shape_offsets", offsets_fallback)):
            return (0, 0)
        offset = cls._hot_int_at(
            packed,
            "param_shape_offsets",
            param_shape_id,
            offsets_fallback,
        )
        length = cls._hot_int_at(
            packed,
            "param_shape_lengths",
            param_shape_id,
            lengths_fallback,
        )
        return int(offset or 0), int(length or 0)

    @classmethod
    def _segment_phase_names(cls, packed: PackedKernel) -> tuple[str, ...]:
        phase_names = tuple(getattr(packed, "phase_names", ()) or ())
        phase_ids = cls._hot_array(
            packed,
            "segment_phase_ids",
            tuple(getattr(packed, "segment_catalog_phase_ids", ()) or ()),
        )
        if phase_names and phase_ids:
            return tuple(
                str(phase_names[int(phase_id)]) if 0 <= int(phase_id) < len(phase_names) else str(phase_id)
                for phase_id in phase_ids
        )
        return tuple(getattr(packed, "segment_phases", ()) or ())

    @classmethod
    def _resolve_program_param_shape_id(
        cls, packed: PackedKernel, program_id: int, hot_op_plan: Any | None
    ) -> int:
        if hot_op_plan is not None:
            plan_value = cls._coerce_int(getattr(hot_op_plan, "param_shape_id", None))
            if plan_value is not None:
                return plan_value
        fallback = tuple(getattr(packed, "program_param_shape_ids", ()) or ())
        value = cls._hot_int_at(
            packed,
            "program_param_shape_ids",
            program_id,
            fallback,
        )
        return int(value) if value is not None else -1

    @classmethod
    def _resolve_program_transport_kind_id(
        cls, packed: PackedKernel, program_id: int, hot_op_plan: Any | None
    ) -> int:
        if hot_op_plan is not None:
            plan_value = cls._coerce_int(
                getattr(hot_op_plan, "transport_kind_id", None)
            )
            if plan_value is not None:
                return plan_value
        fallback = tuple(getattr(packed, "program_transport_kind_ids", ()) or ())
        value = cls._hot_int_at(
            packed,
            "program_transport_kind_ids",
            program_id,
            fallback,
        )
        return int(value) if value is not None else _TRANSPORT_KIND_GENERIC

    @staticmethod
    def _active_transport_kind(hot: HotCtx, fallback: int) -> int:
        protocol = str(
            hot.dispatch_binding_protocol or hot.route_protocol or hot.protocol or ""
        )
        if protocol.endswith(".jsonrpc"):
            return _TRANSPORT_KIND_JSONRPC
        if protocol.endswith(".rest"):
            return _TRANSPORT_KIND_REST
        if protocol in {"ws", "wss", "webtransport"} or hot.scope_type in {
            "websocket",
            "webtransport",
        }:
            return _TRANSPORT_KIND_CHANNEL
        return fallback

    @staticmethod
    def _compiled_lookup_name(field_name: str, field_meta: Any) -> str:
        if isinstance(field_meta, Mapping):
            alias_in = field_meta.get("alias_in")
            if alias_in:
                return str(alias_in)
        return field_name

    @staticmethod
    def _publish_compiled_slots(
        hot: HotCtx,
        field_names: tuple[str, ...],
        field_index: Mapping[str, int],
        slot_values: list[Any],
        slot_present: bytearray,
    ) -> None:
        hot.slot_field_names = field_names
        hot.slot_field_index = field_index
        hot.slot_values = slot_values
        hot.slot_present = slot_present
        hot.in_values_view = None
        hot.route_payload = None
        hot.in_present_names = tuple(
            field_names[idx] for idx in range(len(field_names)) if slot_present[idx]
        )
        hot.assembled_slot_values = None
        hot.assembled_slot_present = None
        hot.virtual_slot_values = None
        hot.virtual_slot_present = None
        hot.assembled_values_view = None
        hot.virtual_in_view = None
        hot.absent_fields = ()
        hot.used_default_factory = ()
        hot.compiled_in_invalid = None
        hot.compiled_in_errors = None
        hot.compiled_in_coerced = ()
        hot.compiled_input_ready = True
        hot.lazy_published = True

    def _resolve_param_shape_decode_strategy(
        self,
        packed: PackedKernel,
        program_id: int,
        param_shape_id: int,
        field_names: tuple[str, ...],
        by_field: Mapping[str, Any],
    ) -> tuple[int, tuple[tuple[int, str, int, int], ...]]:
        cache_key = (id(packed), program_id, param_shape_id)
        cached = self._param_shape_decode_strategy_cache.get(cache_key)
        if cached is not None:
            return cached

        start, length = self._param_shape_descriptor_slice(packed, param_shape_id)
        strategy: tuple[int, tuple[tuple[int, str, int, int], ...]] = (
            _DECODE_STRATEGY_GENERIC_HASHED,
            (),
        )
        if length > 0 and field_names:
            source_masks_fallback = tuple(
                getattr(packed, "param_shape_source_masks", ()) or ()
            )
            slot_ids_fallback = tuple(getattr(packed, "param_shape_slot_ids", ()) or ())
            decoder_ids_fallback = tuple(
                getattr(packed, "param_shape_decoder_ids", ()) or ()
            )
            max_lengths_fallback = tuple(
                getattr(packed, "param_shape_max_lengths", ()) or ()
            )
            rows: list[tuple[int, str, int, int]] = []
            body_only = True
            for idx in range(start, start + length):
                source_mask = self._hot_int_at(
                    packed,
                    "param_shape_source_masks",
                    idx,
                    source_masks_fallback,
                )
                if source_mask != _PARAM_SOURCE_BODY:
                    body_only = False
                    break
                slot_id = self._hot_int_at(
                    packed,
                    "param_shape_slot_ids",
                    idx,
                    slot_ids_fallback,
                )
                if not (0 <= slot_id < len(field_names)):
                    body_only = False
                    break
                field_name = field_names[slot_id]
                field_meta = by_field.get(field_name, {}) if isinstance(by_field, Mapping) else {}
                rows.append(
                    (
                        slot_id,
                        self._compiled_lookup_name(field_name, field_meta),
                        self._hot_int_at(
                            packed,
                            "param_shape_decoder_ids",
                            idx,
                            decoder_ids_fallback,
                        ),
                        self._hot_int_at(
                            packed,
                            "param_shape_max_lengths",
                            idx,
                            max_lengths_fallback,
                        ),
                    )
                )
            if body_only and rows:
                strategy_kind = (
                    _DECODE_STRATEGY_BODY_ONLY_SINGLE_FIELD
                    if len(rows) == 1
                    else _DECODE_STRATEGY_BODY_ONLY_MAPPING
                )
                strategy = (strategy_kind, tuple(rows))

        self._param_shape_decode_strategy_cache[cache_key] = strategy
        return strategy

    async def _prepare_compiled_input(
        self,
        ctx: _Ctx,
        hot: HotCtx,
        packed: PackedKernel,
        program_id: int,
        hot_op_plan: Any | None,
    ) -> None:
        param_shape_id = self._resolve_program_param_shape_id(
            packed, program_id, hot_op_plan
        )
        if hot.slot_values is not None and hot.param_shape_id == param_shape_id:
            return

        hot.param_shape_id = param_shape_id
        hot.transport_kind_id = self._resolve_program_transport_kind_id(
            packed, program_id, hot_op_plan
        )
        raw_scope = hot.raw_scope or {}
        if hot.raw_headers is None:
            hot.raw_headers = self._coerce_header_pairs(raw_scope)
        if not hot.content_type:
            hot.content_type = self._content_type_from_raw_headers(hot.raw_headers or ())
        if not hot.raw_query_string:
            query_string = raw_scope.get("query_string", b"")
            if isinstance(query_string, (bytes, bytearray)):
                hot.raw_query_string = bytes(query_string)
        if hot.path_params is None and hot.route_path_params is not None:
            hot.path_params = hot.route_path_params
        request = self._ensure_hot_request(ctx, hot)
        hot.transport_kind_id = self._active_transport_kind(hot, hot.transport_kind_id)
        if param_shape_id < 0:
            method = str(hot.method or "").upper()
            if method not in {"GET", "HEAD", "OPTIONS"}:
                body_bytes = await self._ensure_body_bytes(ctx, hot)
                if request is not None and body_bytes is not None and hasattr(request, "body"):
                    request.body = body_bytes
                if body_bytes and "json" in hot.content_type:
                    try:
                        parsed = json.loads(body_bytes)
                    except Exception:
                        parsed = None
                    hot.parsed_json = parsed
                    hot.parsed_json_loaded = True
                    if hot.transport_kind_id == _TRANSPORT_KIND_JSONRPC and isinstance(parsed, dict):
                        hot.route_rpc_envelope = parsed
                        params = parsed.get("params", {})
                        hot.route_payload = params if isinstance(params, dict) else None
                    elif isinstance(parsed, dict):
                        hot.route_payload = parsed
            return
        body_bytes = await self._ensure_body_bytes(ctx, hot)
        if request is not None and body_bytes is not None and hasattr(request, "body"):
            request.body = body_bytes
        if hot.transport_kind_id in {_TRANSPORT_KIND_REST, _TRANSPORT_KIND_JSONRPC}:
            if not hot.parsed_json_loaded:
                parsed = None
                if body_bytes and "json" in hot.content_type:
                    try:
                        parsed = json.loads(body_bytes)
                    except Exception:
                        parsed = None
                hot.parsed_json = parsed
                hot.parsed_json_loaded = True

        if hot.transport_kind_id == _TRANSPORT_KIND_JSONRPC and isinstance(hot.parsed_json, dict):
            rpc_envelope = hot.parsed_json
            hot.route_rpc_envelope = rpc_envelope
            hot.dispatch_rpc_envelope = rpc_envelope
            hot.dispatch_jsonrpc_request_id = rpc_envelope.get("id")
            method = rpc_envelope.get("method")
            hot.dispatch_rpc_method = method if isinstance(method, str) else None

        plan = self._resolve_compiled_param_plan(ctx, packed, program_id, param_shape_id)
        if not plan.descriptor_plans:
            return

        body_payload = hot.parsed_json
        if hot.transport_kind_id == _TRANSPORT_KIND_JSONRPC and isinstance(body_payload, dict):
            body_payload = body_payload.get("params", {})
        if hot.transport_kind_id == _TRANSPORT_KIND_JSONRPC:
            self._reject_jsonrpc_wrapper_keys(
                body_payload,
                field_names=plan.field_names,
            )
        body_mapping = body_payload if isinstance(body_payload, dict) else None
        if body_mapping is not None and plan.reserved_input_keys:
            reserved_body_keys = sorted(
                key for key in body_mapping if key in plan.reserved_input_keys
            )
            if reserved_body_keys:
                raise HTTPException(
                    status_code=_status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=[
                        {
                            "field": key,
                            "code": "extra_forbidden",
                            "message": "Field is not permitted in request input.",
                        }
                        for key in reserved_body_keys
                    ],
                )
        path_mapping = hot.route_path_params or hot.path_params
        field_names = plan.field_names
        slot_values: list[Any] = [None] * len(field_names)
        slot_present = bytearray(len(field_names))

        if (
            plan.strategy_kind == _DECODE_STRATEGY_BODY_ONLY_SINGLE_FIELD
            and body_mapping is not None
            and plan.strategy_rows
        ):
            hot.body_hashed_items = None
            hot.query_hashed_spans = None
            hot.header_hashed_pairs = None
            slot_id, lookup_name, decoder_id, max_length = plan.strategy_rows[0]
            value = body_mapping.get(lookup_name)
            if value is not None:
                try:
                    coerced = self._decode_scalar(value, decoder_id)
                except Exception:
                    coerced = value
                if max_length > 0 and isinstance(coerced, str) and len(coerced) > max_length:
                    coerced = coerced[:max_length]
                slot_values[slot_id] = coerced
                slot_present[slot_id] = 1
            self._publish_compiled_slots(
                hot, field_names, plan.field_index, slot_values, slot_present
            )
            return

        if (
            plan.strategy_kind == _DECODE_STRATEGY_BODY_ONLY_MAPPING
            and body_mapping is not None
            and plan.strategy_rows
        ):
            hot.body_hashed_items = None
            hot.query_hashed_spans = None
            hot.header_hashed_pairs = None
            for slot_id, lookup_name, decoder_id, max_length in plan.strategy_rows:
                value = body_mapping.get(lookup_name)
                if value is None:
                    continue
                try:
                    coerced = self._decode_scalar(value, decoder_id)
                except Exception:
                    coerced = value
                if max_length > 0 and isinstance(coerced, str) and len(coerced) > max_length:
                    coerced = coerced[:max_length]
                slot_values[slot_id] = coerced
                slot_present[slot_id] = 1
            self._publish_compiled_slots(
                hot, field_names, plan.field_index, slot_values, slot_present
            )
            return

        hot.body_hashed_items = None
        query_spans: tuple[tuple[int, int, int, int], ...] = ()
        if plan.needs_query:
            if hot.query_hashed_spans is None:
                hot.query_hashed_spans = self._parse_query_spans(hot.raw_query_string)
            query_spans = hot.query_hashed_spans
        else:
            hot.query_hashed_spans = None
        header_pairs: tuple[tuple[int, bytes], ...] = ()
        if plan.needs_header:
            raw_headers = hot.raw_headers or ()
            if hot.header_hashed_pairs is None:
                hot.header_hashed_pairs = self._header_hash_pairs(raw_headers)
            header_pairs = hot.header_hashed_pairs
        else:
            hot.header_hashed_pairs = None

        for row in plan.descriptor_plans:
            slot_id = row.slot_id
            value = None
            found = False
            if row.source_mask & _PARAM_SOURCE_BODY and body_mapping is not None:
                if row.lookup_name in body_mapping:
                    found, value = True, body_mapping[row.lookup_name]
            if not found and row.source_mask & _PARAM_SOURCE_PATH and path_mapping is not None:
                if row.lookup_name in path_mapping:
                    found, value = True, path_mapping[row.lookup_name]
            if not found and row.source_mask & _PARAM_SOURCE_QUERY:
                found, value = self._lookup_query_value(
                    hot.raw_query_string, query_spans, row.lookup_hash
                )
            if not found and row.source_mask & _PARAM_SOURCE_HEADER and row.header_hash:
                found, value = self._lookup_hashed_pairs(header_pairs, row.header_hash)
            if not found:
                continue
            try:
                coerced = self._decode_scalar(value, row.decoder_id)
            except Exception:
                coerced = value
            if row.max_length > 0 and isinstance(coerced, str) and len(coerced) > row.max_length:
                coerced = coerced[: row.max_length]
            slot_values[slot_id] = coerced
            slot_present[slot_id] = 1

        self._publish_compiled_slots(
            hot, field_names, plan.field_index, slot_values, slot_present
        )

    @staticmethod
    def _compiled_schema_in(
        ctx: _Ctx,
    ) -> tuple[tuple[str, ...], Mapping[str, Mapping[str, Any]], tuple[str, ...]]:
        opview = getattr(ctx, "opview", None)
        schema_in = getattr(opview, "schema_in", None) if opview is not None else None
        if isinstance(schema_in, Mapping):
            fields = tuple(schema_in.get("fields", ()) or ())
            by_field = schema_in.get("by_field", {}) or {}
            required = tuple(schema_in.get("required", ()) or ())
        else:
            fields = tuple(getattr(schema_in, "fields", ()) or ())
            by_field = getattr(schema_in, "by_field", {}) or {}
            required = tuple(getattr(schema_in, "required", ()) or ())
        if not required:
            required = tuple(
                name
                for name, meta in by_field.items()
                if isinstance(meta, Mapping) and meta.get("required")
            )
        return fields, by_field, required

    def _resolve_compiled_param_plan(
        self,
        ctx: _Ctx,
        packed: PackedKernel,
        program_id: int,
        param_shape_id: int,
    ) -> _CompiledParamPlan:
        cache_key = (id(packed), program_id, param_shape_id)
        cached = self._compiled_param_plan_cache.get(cache_key)
        if cached is not None:
            return cached

        field_names, by_field, required = self._compiled_schema_in(ctx)
        opview = getattr(ctx, "opview", None)
        field_index = {field_name: idx for idx, field_name in enumerate(field_names)}
        required_set = frozenset(required)
        field_plans = tuple(
            _CompiledFieldPlan(
                slot_id=idx,
                field_name=field_name,
                required=field_name in required_set,
                nullable=(
                    bool(meta.get("nullable"))
                    if meta.get("nullable") is not None
                    else None
                ),
                py_type=meta.get("py_type"),
                coerce=bool(meta.get("coerce", True)),
                max_length=(
                    int(meta.get("max_length"))
                    if isinstance(meta.get("max_length"), int)
                    else 0
                ),
                validator=meta.get("validator"),
                in_enabled=bool(meta.get("in_enabled", True)),
                is_virtual=bool(meta.get("virtual", False)),
                default_factory=meta.get("default_factory"),
            )
            for idx, field_name in enumerate(field_names)
            for meta in ((by_field.get(field_name, {}) or {}),)
        )

        start, length = self._param_shape_descriptor_slice(packed, param_shape_id)
        lookup_hashes_fallback = tuple(
            getattr(packed, "param_shape_lookup_hashes", ()) or ()
        )
        header_hashes_fallback = tuple(
            getattr(packed, "param_shape_header_hashes", ()) or ()
        )
        source_masks_fallback = tuple(
            getattr(packed, "param_shape_source_masks", ()) or ()
        )
        slot_ids_fallback = tuple(getattr(packed, "param_shape_slot_ids", ()) or ())
        decoder_ids_fallback = tuple(
            getattr(packed, "param_shape_decoder_ids", ()) or ()
        )
        max_lengths_fallback = tuple(
            getattr(packed, "param_shape_max_lengths", ()) or ()
        )

        descriptor_rows: list[_CompiledInputDescriptor] = []
        body_lookup_names: set[str] = set()
        reserved_input_keys: set[str] = set()
        needs_query = False
        needs_header = False
        needs_path = False
        for idx in range(start, start + length):
            slot_id = self._hot_int_at(
                packed,
                "param_shape_slot_ids",
                idx,
                slot_ids_fallback,
            )
            if not (0 <= slot_id < len(field_names)):
                continue
            field_name = field_names[slot_id]
            field_meta = by_field.get(field_name, {}) if isinstance(by_field, Mapping) else {}
            source_mask = self._hot_int_at(
                packed,
                "param_shape_source_masks",
                idx,
                source_masks_fallback,
            )
            lookup_name = self._compiled_lookup_name(field_name, field_meta)
            if bool(source_mask & _PARAM_SOURCE_BODY):
                body_lookup_names.add(lookup_name)
            needs_query = needs_query or bool(source_mask & _PARAM_SOURCE_QUERY)
            needs_header = needs_header or bool(source_mask & _PARAM_SOURCE_HEADER)
            needs_path = needs_path or bool(source_mask & _PARAM_SOURCE_PATH)
            descriptor_rows.append(
                _CompiledInputDescriptor(
                    slot_id=slot_id,
                    lookup_name=lookup_name,
                    source_mask=source_mask,
                    decoder_id=self._hot_int_at(
                        packed,
                        "param_shape_decoder_ids",
                        idx,
                        decoder_ids_fallback,
                    ),
                    max_length=self._hot_int_at(
                        packed,
                        "param_shape_max_lengths",
                        idx,
                        max_lengths_fallback,
                    ),
                    lookup_hash=self._hot_int_at(
                        packed,
                        "param_shape_lookup_hashes",
                        idx,
                        lookup_hashes_fallback,
                    ),
                    header_hash=self._hot_int_at(
                        packed,
                        "param_shape_header_hashes",
                        idx,
                        header_hashes_fallback,
                    ),
                )
            )

        strategy_kind, strategy_rows = self._resolve_param_shape_decode_strategy(
            packed,
            program_id,
            param_shape_id,
            field_names,
            by_field if isinstance(by_field, Mapping) else {},
        )
        paired_index = getattr(opview, "paired_index", {}) or {}
        for field_name, desc in paired_index.items():
            if isinstance(field_name, str) and field_name and field_name not in field_index:
                reserved_input_keys.add(field_name)
            alias = desc.get("alias") if isinstance(desc, Mapping) else None
            if isinstance(alias, str) and alias:
                reserved_input_keys.add(alias)
        plan = _CompiledParamPlan(
            field_names=field_names,
            field_index=field_index,
            field_plans=field_plans,
            descriptor_plans=tuple(descriptor_rows),
            strategy_kind=strategy_kind,
            strategy_rows=strategy_rows,
            assemble_order=tuple(field_index[name] for name in sorted(field_names)),
            body_lookup_names=frozenset(body_lookup_names),
            reserved_input_keys=frozenset(reserved_input_keys),
            needs_query=needs_query,
            needs_header=needs_header,
            needs_path=needs_path,
        )
        self._compiled_param_plan_cache[cache_key] = plan
        return plan

    def _compiled_validate_and_assemble(
        self,
        ctx: _Ctx,
        hot: HotCtx,
        plan: _CompiledParamPlan,
    ) -> None:
        field_names = plan.field_names
        slot_values = hot.slot_values or []
        slot_present = hot.slot_present or bytearray()
        errors: list[dict[str, Any]] = []
        coerced: list[str] = []

        for field_plan in plan.field_plans:
            slot_id = field_plan.slot_id
            present = 0 <= slot_id < len(slot_present) and bool(slot_present[slot_id])
            if field_plan.required and not present:
                errors.append(
                    {
                        "field": field_plan.field_name,
                        "code": "required",
                        "message": "Field is required but was not provided.",
                    }
                )
                continue
            if not present or not (0 <= slot_id < len(slot_values)):
                continue

            value = slot_values[slot_id]
            if value is None and field_plan.nullable is False:
                errors.append(
                    {
                        "field": field_plan.field_name,
                        "code": "null_not_allowed",
                        "message": "Null is not allowed for this field.",
                    }
                )
                continue

            target_type = field_plan.py_type
            if value is not None and isinstance(target_type, type):
                ok, new_val, msg = _coerce_if_needed(
                    value,
                    target_type,
                    allow=field_plan.coerce,
                )
                if not ok:
                    errors.append(
                        {
                            "field": field_plan.field_name,
                            "code": "type_mismatch",
                            "message": msg or f"Expected {target_type.__name__}.",
                        }
                    )
                    continue
                if new_val is not value:
                    slot_values[slot_id] = new_val
                    value = new_val
                    coerced.append(field_plan.field_name)

            if (
                field_plan.max_length > 0
                and isinstance(value, str)
                and len(value) > field_plan.max_length
            ):
                errors.append(
                    {
                        "field": field_plan.field_name,
                        "code": "max_length",
                        "message": f"String exceeds max_length={field_plan.max_length}.",
                    }
                )
                continue

            validator = field_plan.validator
            if callable(validator) and value is not None:
                try:
                    out = validator(value, ctx)
                    if out is not None:
                        slot_values[slot_id] = out
                except Exception as exc:
                    errors.append(
                        {
                            "field": field_plan.field_name,
                            "code": "validator_failed",
                            "message": f"{type(exc).__name__}: {exc}",
                        }
                    )

        hot.compiled_in_invalid = bool(errors)
        hot.compiled_in_errors = tuple(dict(error) for error in errors) if errors else None
        hot.compiled_in_coerced = tuple(coerced)
        hot.in_present_names = tuple(
            field_names[idx]
            for idx in range(min(len(field_names), len(slot_present)))
            if slot_present[idx]
        )

        if errors:
            raise HTTPException(
                status_code=_status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=[dict(error) for error in errors],
            )

        assembled_values = list(slot_values)
        assembled_present = bytearray(len(field_names))
        virtual_values = list(slot_values)
        virtual_present = bytearray(len(field_names))
        absent: list[str] = []
        used_default: list[str] = []
        view = None

        for slot_id in plan.assemble_order:
            if not (0 <= slot_id < len(plan.field_plans)):
                continue
            field_plan = plan.field_plans[slot_id]
            present = 0 <= slot_id < len(slot_present) and bool(slot_present[slot_id])
            if present:
                value = slot_values[slot_id]
                if field_plan.is_virtual:
                    virtual_values[slot_id] = value
                    virtual_present[slot_id] = 1
                elif field_plan.in_enabled:
                    assembled_values[slot_id] = value
                    assembled_present[slot_id] = 1
                continue

            absent.append(field_plan.field_name)
            default_fn = field_plan.default_factory
            if callable(default_fn) and field_plan.in_enabled and not field_plan.is_virtual:
                if view is None:
                    view = _ctx_view(ctx)
                try:
                    default_value = default_fn(view)
                except Exception:
                    continue
                assembled_values[slot_id] = default_value
                assembled_present[slot_id] = 1
                used_default.append(field_plan.field_name)

        hot.assembled_slot_values = assembled_values
        hot.assembled_slot_present = assembled_present
        hot.virtual_slot_values = virtual_values
        hot.virtual_slot_present = virtual_present
        hot.assembled_values_view = None
        hot.virtual_in_view = None
        hot.absent_fields = tuple(absent)
        hot.used_default_factory = tuple(used_default)

    def _resolve_segments_for_program(
        self, packed: PackedKernel, program_id: int
    ) -> tuple[tuple[int, ...], tuple[int, ...]]:
        cache_key = (id(packed), program_id)
        cached = self._program_segments_cache.get(cache_key)
        if cached is not None:
            return cached

        offsets_fallback = tuple(
            getattr(packed, "program_segment_ref_offsets", ())
            or getattr(packed, "op_segment_offsets", ())
            or ()
        )
        lengths_fallback = tuple(
            getattr(packed, "program_segment_ref_lengths", ())
            or getattr(packed, "op_segment_lengths", ())
            or ()
        )
        refs_fallback = tuple(
            getattr(packed, "program_segment_refs", ())
            or getattr(packed, "op_to_segment_ids", ())
            or ()
        )
        segment_phases = self._segment_phase_names(packed)
        seg_offset = self._hot_int_at(
            packed,
            "program_segment_offsets",
            program_id,
            offsets_fallback,
        )
        seg_length = self._hot_int_at(
            packed,
            "program_segment_lengths",
            program_id,
            lengths_fallback,
        )
        if seg_offset is None or seg_length is None:
            resolved = ((), ())
            self._program_segments_cache[cache_key] = resolved
            return resolved
        ordered_segments: list[int] = []
        by_phase: dict[str, list[int]] = {}
        remaining: list[int] = []
        seen_segment_ids: set[int] = set()
        for i in range(int(seg_offset), int(seg_offset) + int(seg_length)):
            seg_id = self._hot_int_at(
                packed,
                "program_segment_refs",
                i,
                refs_fallback,
            )
            if seg_id is None:
                continue
            phase = str(normalize_phase(segment_phases[seg_id]))
            if phase.startswith("ON_") or phase == "TX_ROLLBACK":
                continue
            by_phase.setdefault(phase, []).append(seg_id)

        for phase in self._PHASE_EXECUTION_ORDER:
            for seg_id in by_phase.pop(phase, ()):  # pragma: no branch
                if seg_id in seen_segment_ids:
                    continue
                seen_segment_ids.add(seg_id)
                ordered_segments.append(seg_id)

        for i in range(int(seg_offset), int(seg_offset) + int(seg_length)):
            seg_id = self._hot_int_at(
                packed,
                "program_segment_refs",
                i,
                refs_fallback,
            )
            if seg_id is None:
                continue
            if seg_id in seen_segment_ids:
                continue
            phase = str(segment_phases[seg_id])
            phase = str(normalize_phase(phase))
            if phase.startswith("ON_") or phase == "TX_ROLLBACK":
                continue
            seen_segment_ids.add(seg_id)
            remaining.append(seg_id)

        resolved = (tuple(ordered_segments), tuple(remaining))
        self._program_segments_cache[cache_key] = resolved
        return resolved

    @staticmethod
    def _coerce_int(value: Any) -> int | None:
        return value if isinstance(value, int) else None

    @staticmethod
    def _coerce_dict(value: Any) -> dict[str, Any] | None:
        if isinstance(value, dict):
            return value
        if isinstance(value, Mapping):
            return dict(value)
        return None

    @classmethod
    def _sync_hot_from_temp(cls, temp: dict[str, Any], hot: HotCtx) -> None:
        route = dict.get(temp, "route")
        if isinstance(route, dict):
            if "selector" in route and isinstance(route.get("selector"), str):
                hot.route_selector = str(route.get("selector"))
            if "protocol" in route and isinstance(route.get("protocol"), str):
                hot.route_protocol = str(route.get("protocol"))
            if "program_id" in route:
                program_id = cls._coerce_int(route.get("program_id"))
                if program_id is not None:
                    hot.route_program_id = program_id
                    hot.program_id = program_id
            if "opmeta_index" in route:
                opmeta_index = cls._coerce_int(route.get("opmeta_index"))
                if opmeta_index is not None:
                    hot.route_opmeta_index = opmeta_index
                    if hot.route_program_id < 0:
                        hot.route_program_id = opmeta_index
                    if hot.program_id < 0:
                        hot.program_id = opmeta_index
            if "method_not_allowed" in route:
                hot.route_method_not_allowed = bool(route.get("method_not_allowed"))
            if "short_circuit" in route:
                hot.route_short_circuit = bool(route.get("short_circuit"))
            if "payload" in route:
                hot.route_payload = cls._coerce_dict(route.get("payload"))
            if "path_params" in route:
                path_params = cls._coerce_dict(route.get("path_params"))
                hot.route_path_params = path_params
                hot.path_params = path_params
            if "rpc_envelope" in route:
                route_rpc_envelope = cls._coerce_dict(route.get("rpc_envelope"))
                hot.route_rpc_envelope = route_rpc_envelope
                if route_rpc_envelope is not None:
                    hot.dispatch_jsonrpc_request_id = route_rpc_envelope.get("id")
                    method = route_rpc_envelope.get("method")
                    hot.dispatch_rpc_method = method if isinstance(method, str) else None

        dispatch = dict.get(temp, "dispatch")
        if isinstance(dispatch, dict):
            if "binding_protocol" in dispatch and isinstance(
                dispatch.get("binding_protocol"), str
            ):
                hot.dispatch_binding_protocol = str(dispatch.get("binding_protocol"))
            if "binding_selector" in dispatch and isinstance(
                dispatch.get("binding_selector"), str
            ):
                hot.dispatch_binding_selector = str(dispatch.get("binding_selector"))
            if "channel_protocol" in dispatch and isinstance(
                dispatch.get("channel_protocol"), str
            ):
                hot.dispatch_channel_protocol = str(dispatch.get("channel_protocol"))
            if "channel_selector" in dispatch and isinstance(
                dispatch.get("channel_selector"), str
            ):
                hot.dispatch_channel_selector = str(dispatch.get("channel_selector"))
            if "rpc" in dispatch:
                dispatch_rpc_envelope = cls._coerce_dict(dispatch.get("rpc"))
                hot.dispatch_rpc_envelope = dispatch_rpc_envelope
                if dispatch_rpc_envelope is not None:
                    hot.dispatch_jsonrpc_request_id = dispatch_rpc_envelope.get("id")
                    method = dispatch_rpc_envelope.get("method")
                    hot.dispatch_rpc_method = method if isinstance(method, str) else None
            if "rpc_method" in dispatch and isinstance(dispatch.get("rpc_method"), str):
                hot.dispatch_rpc_method = str(dispatch.get("rpc_method"))
            if "normalized_input" in dispatch or "parsed_payload" in dispatch:
                hot.route_payload = cls._coerce_dict(
                    dispatch.get("normalized_input", dispatch.get("parsed_payload"))
                )

        egress = dict.get(temp, "egress")
        if isinstance(egress, dict):
            if "transport_response" in egress:
                hot.egress_transport_response = cls._coerce_dict(
                    egress.get("transport_response")
                )
            if "sent" in egress:
                hot.egress_sent = bool(egress.get("sent"))

        if "jsonrpc_request_id" in temp:
            hot.dispatch_jsonrpc_request_id = dict.get(temp, "jsonrpc_request_id")

    @classmethod
    def _ensure_hot_ctx(cls, ctx: _Ctx, env: Any) -> HotCtx:
        temp = getattr(ctx, "temp", None)
        if not isinstance(temp, dict):
            ctx.temp = {}
            temp = ctx.temp
        hot = temp.get("hot_ctx")
        if isinstance(hot, HotCtx):
            return hot

        scope = getattr(env, "scope", {}) or {}
        scope_dict = cls._coerce_dict(scope) or {}
        method = str(scope_dict.get("method") or "").upper()
        path = str(scope_dict.get("path") or "")
        scheme = str(scope_dict.get("scheme") or "").lower()
        scope_type = str(scope_dict.get("type") or "")
        protocol = ""
        selector = ""
        if scope_type == "http" and method and path:
            protocol = "https.rest" if scheme == "https" else "http.rest"
            selector = f"{method} {path}"
        elif scope_type in {"websocket", "webtransport"} and path:
            protocol = scheme or scope_type
            selector = path
        path_params = cls._coerce_dict(scope_dict.get("path_params"))
        raw_query_string = scope_dict.get("query_string", b"")

        hot = HotCtx(
            scope_type=scope_type,
            method=method,
            path=path,
            protocol=protocol,
            selector=selector,
            route_protocol=protocol,
            route_selector=selector,
            dispatch_binding_protocol=protocol,
            dispatch_binding_selector=selector,
            dispatch_channel_protocol=protocol if scope_type in {"websocket", "webtransport"} else "",
            dispatch_channel_selector=selector if scope_type in {"websocket", "webtransport"} else "",
            content_type="",
            raw_scope=scope_dict or None,
            raw_receive=getattr(env, "receive", None),
            raw_send=getattr(env, "send", None),
            raw_headers=cls._coerce_header_pairs(scope_dict or None),
            raw_query_string=bytes(raw_query_string)
            if isinstance(raw_query_string, (bytes, bytearray))
            else b"",
            path_params=path_params,
            route_path_params=path_params,
        )
        cls._sync_hot_from_temp(temp, hot)
        temp["hot_ctx"] = hot
        return hot

    @staticmethod
    def _coerce_model_column_keys(obj: Any) -> tuple[str, ...] | None:
        table = getattr(obj, "__table__", None)
        columns = getattr(table, "columns", None)
        if columns is None:
            return None
        out: list[str] = []
        for col in columns:
            key = getattr(col, "key", None)
            if isinstance(key, str) and key:
                out.append(key)
        return tuple(out)

    def _serialize_model_row(self, obj: Any) -> Any:
        if obj is None or isinstance(obj, Mapping):
            return obj
        model_type = type(obj)
        serializer = self._model_row_serializer_cache.get(model_type)
        if serializer is None:
            keys = self._coerce_model_column_keys(obj)
            if keys is None:
                return obj
            getter = attrgetter(*keys)
            serializer = (keys, getter)
            self._model_row_serializer_cache[model_type] = serializer
        keys, getter = serializer
        if not keys:
            return obj
        values = getter(obj)
        if len(keys) == 1:
            values = (values,)
        return dict(zip(keys, values))

    def _require_program_id_from_ctx(self, ctx: _Ctx) -> int:
        temp = getattr(ctx, "temp", None)
        if not isinstance(temp, dict):
            ctx.temp = {}
            temp = ctx.temp

        hot = dict.get(temp, "hot_ctx")
        if isinstance(hot, HotCtx):
            value = hot.route_program_id if hot.route_program_id >= 0 else hot.program_id
            if value >= 0:
                temp["program_id"] = value
                return value

        route = dict.get(temp, "route")
        if isinstance(route, dict):
            for key in ("program_id", "opmeta_index"):
                value = self._coerce_int(route.get(key))
                if value is not None:
                    temp["program_id"] = value
                    return value

        value = self._coerce_int(dict.get(temp, "program_id"))
        if value is not None:
            return value

        return -1

    def _resolve_program_id_from_dispatch(self, ctx: _Ctx, packed: PackedKernel) -> int:
        temp = getattr(ctx, "temp", None)
        if not isinstance(temp, dict):
            return -1

        hot = dict.get(temp, "hot_ctx")
        if isinstance(hot, HotCtx) and hot.program_id >= 0:
            temp["program_id"] = hot.program_id
            return hot.program_id

        selector = hot.dispatch_binding_selector if isinstance(hot, HotCtx) else ""
        protocol = hot.dispatch_binding_protocol if isinstance(hot, HotCtx) else ""
        if not selector or not protocol:
            dispatch = dict.get(temp, "dispatch")
            if not isinstance(dispatch, dict):
                return -1
            raw_selector = dispatch.get("binding_selector")
            raw_protocol = dispatch.get("binding_protocol")
            selector = raw_selector if isinstance(raw_selector, str) else ""
            protocol = raw_protocol if isinstance(raw_protocol, str) else ""
        if not selector or not protocol:
            return -1

        selector_to_id = getattr(packed, "selector_to_id", None)
        proto_to_id = getattr(packed, "proto_to_id", None)
        route_to_program = getattr(packed, "route_to_program", None)
        if not (
            isinstance(selector_to_id, Mapping)
            and isinstance(proto_to_id, Mapping)
            and route_to_program is not None
        ):
            return -1

        selector_id = self._coerce_int(selector_to_id.get(selector))
        proto_id = self._coerce_int(proto_to_id.get(protocol))
        if selector_id is None or proto_id is None:
            return -1
        if not (0 <= proto_id < len(route_to_program)):
            return -1

        row = route_to_program[proto_id]
        if not (0 <= selector_id < len(row)):
            return -1

        program_id = self._coerce_int(row[selector_id])
        if program_id is None or program_id < 0:
            return -1

        temp["program_id"] = program_id
        if isinstance(hot, HotCtx):
            hot.proto_id = proto_id
            hot.selector_id = selector_id
            hot.program_id = program_id
            hot.route_program_id = program_id
            hot.route_opmeta_index = program_id
        return program_id

    def _resolve_request_caches(
        self, plan: KernelPlan
    ) -> tuple[dict[tuple[int, str, str], int], tuple[tuple[str, Any, int], ...]]:
        plan_id = id(plan)
        templated = self._templated_route_cache.get(plan_id)
        if templated is None:
            exact: dict[tuple[int, str, str], int] = {}
            templated_routes: list[tuple[str, Any, int]] = []
            for proto in ("http.rest", "https.rest"):
                bucket = plan.proto_indices.get(proto)
                if not isinstance(bucket, Mapping):
                    continue
                exact_bucket = bucket.get("exact")
                if isinstance(exact_bucket, Mapping):
                    for selector, meta_index in exact_bucket.items():
                        if not (
                            isinstance(selector, str) and isinstance(meta_index, int)
                        ):
                            continue
                        method, _, path = selector.partition(" ")
                        if not path:
                            continue
                        exact[(plan_id, method.upper(), path)] = meta_index
                templated_bucket = bucket.get("templated")
                if isinstance(templated_bucket, list):
                    for entry in templated_bucket:
                        if not isinstance(entry, Mapping):
                            continue
                        meta_index = entry.get("meta_index")
                        pattern = entry.get("pattern")
                        if (
                            not isinstance(meta_index, int)
                            or pattern is None
                            or not hasattr(pattern, "match")
                        ):
                            continue
                        method = str(entry.get("method", "") or "").upper()
                        templated_routes.append((method, pattern, meta_index))
            self._request_program_cache.update(exact)
            templated = tuple(templated_routes)
            self._templated_route_cache[plan_id] = templated
        return self._request_program_cache, templated

    def _resolve_program_id_from_request(self, ctx: _Ctx, plan: KernelPlan) -> int:
        method = getattr(ctx, "method", None)
        path = getattr(ctx, "path", None)

        if not (isinstance(method, str) and isinstance(path, str) and path):
            raw = getattr(ctx, "raw", None)
            scope = getattr(raw, "scope", None) if raw is not None else None
            if isinstance(scope, Mapping):
                method = method or scope.get("method")
                path = path or scope.get("path")

        if not (isinstance(method, str) and isinstance(path, str) and path):
            return -1

        method = method.upper()
        exact_cache, templated_routes = self._resolve_request_caches(plan)
        maybe = exact_cache.get((id(plan), method, path))
        if isinstance(maybe, int):
            return maybe

        selector = f"{method} {path}"
        for proto in ("http.rest", "https.rest"):
            maybe = plan.opkey_to_meta.get(OpKey(proto=proto, selector=selector))
            if isinstance(maybe, int):
                exact_cache[(id(plan), method, path)] = maybe
                return maybe

        for entry_method, pattern, meta_index in templated_routes:
            if entry_method and entry_method != method:
                continue
            if pattern.match(path) is None:
                continue
            exact_cache[(id(plan), method, path)] = meta_index
            return meta_index

        return -1

    def _resolve_program_id_from_channel(
        self,
        ctx: _Ctx,
        plan: KernelPlan,
    ) -> int:
        channel = ctx.get("channel")
        protocol = getattr(channel, "protocol", None)
        path = getattr(channel, "path", None)
        if not (isinstance(protocol, str) and isinstance(path, str) and path):
            return -1

        for proto in (protocol, "ws", "wss", "webtransport"):
            bucket = plan.proto_indices.get(proto)
            if not isinstance(bucket, Mapping):
                continue
            exact_bucket = bucket.get("exact")
            if isinstance(exact_bucket, Mapping):
                maybe = exact_bucket.get(path)
                if isinstance(maybe, int):
                    return maybe
            templated_bucket = bucket.get("templated")
            if isinstance(templated_bucket, list):
                for entry in templated_bucket:
                    if not isinstance(entry, Mapping):
                        continue
                    pattern = entry.get("pattern")
                    meta_index = entry.get("meta_index")
                    if hasattr(pattern, "match") and isinstance(meta_index, int):
                        matched = pattern.match(path)
                        if matched is not None:
                            channel = ctx.get("channel")
                            if channel is not None:
                                channel.path_params = matched.groupdict()
                            temp = getattr(ctx, "temp", None)
                            if isinstance(temp, dict):
                                temp.setdefault("dispatch", {})["path_params"] = matched.groupdict()
                                temp.setdefault("route", {})["path_params"] = matched.groupdict()
                            return meta_index
        return -1

    def _resolve_hot_exact_websocket_routes(
        self,
        plan: KernelPlan,
        packed: PackedKernel,
    ) -> Mapping[tuple[str, str], int]:
        packed_id = id(packed)
        cached = self._hot_exact_websocket_route_cache.get(packed_id)
        if cached is not None:
            return cached
        exact: dict[tuple[str, str], int] = {}
        for proto in ("ws", "wss"):
            bucket = plan.proto_indices.get(proto)
            if not isinstance(bucket, Mapping):
                continue
            exact_bucket = bucket.get("exact")
            if not isinstance(exact_bucket, Mapping):
                continue
            for path, meta_index in exact_bucket.items():
                if isinstance(path, str) and isinstance(meta_index, int):
                    exact[(proto, path)] = meta_index
        self._hot_exact_websocket_route_cache[packed_id] = exact
        return exact

    def _resolve_program_id_from_exact_websocket(
        self,
        plan: KernelPlan,
        packed: PackedKernel,
        protocol: str,
        path: str,
    ) -> int:
        exact = self._resolve_hot_exact_websocket_routes(plan, packed)
        maybe = exact.get((protocol, path))
        return maybe if isinstance(maybe, int) else -1

    def _prime_exact_websocket_program(
        self,
        ctx: _Ctx,
        env: Any,
        plan: KernelPlan,
        packed: PackedKernel,
    ) -> int:
        hot = self._ensure_hot_ctx(ctx, env)
        if hot.scope_type != "websocket" or not hot.protocol or not hot.path:
            return -1
        program_id = self._resolve_program_id_from_exact_websocket(
            plan, packed, hot.protocol, hot.path
        )
        if program_id < 0:
            return -1
        temp = getattr(ctx, "temp", None)
        if not isinstance(temp, dict):
            return -1
        hot_op_plan = (
            packed.hot_op_plans[program_id]
            if program_id < len(getattr(packed, "hot_op_plans", ()))
            else None
        )
        hot_runner_id = self._resolve_program_hot_runner_id(
            packed, program_id, hot_op_plan
        )
        if hot_runner_id != _HOT_RUNNER_WS_UNARY_TEXT:
            return -1

        proto_to_id = getattr(packed, "proto_to_id", None)
        selector_to_id = getattr(packed, "selector_to_id", None)
        if isinstance(proto_to_id, Mapping):
            proto_id = self._coerce_int(proto_to_id.get(hot.protocol))
            if proto_id is not None:
                hot.proto_id = proto_id
        if isinstance(selector_to_id, Mapping):
            selector_id = self._coerce_int(selector_to_id.get(hot.selector))
            if selector_id is not None:
                hot.selector_id = selector_id
        hot.program_id = program_id
        hot.route_program_id = program_id
        hot.route_opmeta_index = program_id
        if not hot.route_protocol:
            hot.route_protocol = hot.protocol
        if not hot.route_selector:
            hot.route_selector = hot.selector
        if not hot.dispatch_channel_protocol:
            hot.dispatch_channel_protocol = hot.route_protocol or hot.protocol
        if not hot.dispatch_channel_selector:
            hot.dispatch_channel_selector = hot.route_selector or hot.selector
        hot.transport_kind_id = _TRANSPORT_KIND_CHANNEL
        ctx.path = hot.path
        temp["program_id"] = program_id
        return program_id

    def _resolve_hot_exact_route_slices(
        self, packed: PackedKernel
    ) -> Mapping[int, tuple[int, int]]:
        packed_id = id(packed)
        cached = self._hot_exact_route_cache.get(packed_id)
        if cached is not None:
            return cached
        method_ids = self._hot_section(packed, "exact_method_ids")
        path_hashes = self._hot_section(packed, "exact_path_hashes")
        program_ids = self._hot_section(packed, "exact_program_ids")
        if method_ids is None or path_hashes is None or program_ids is None:
            self._hot_exact_route_cache[packed_id] = {}
            return {}
        if not (
            int(method_ids.count) == int(path_hashes.count) == int(program_ids.count)
        ):
            self._hot_exact_route_cache[packed_id] = {}
            return {}
        directory: dict[int, tuple[int, int]] = {}
        total = int(method_ids.count)
        current_method_id = -1
        current_start = 0
        current_count = 0
        for index in range(total):
            method_id = int(method_ids.get_int(index))
            if method_id == current_method_id:
                current_count += 1
                continue
            if current_count > 0:
                directory[current_method_id] = (current_start, current_count)
            current_method_id = method_id
            current_start = index
            current_count = 1
        if current_count > 0:
            directory[current_method_id] = (current_start, current_count)
        frozen = {int(method_id): (int(start), int(count)) for method_id, (start, count) in directory.items()}
        self._hot_exact_route_cache[packed_id] = frozen
        return frozen

    def _resolve_program_id_from_exact_route(
        self, packed: PackedKernel, method: str, path: str
    ) -> int:
        method_id = self._http_method_id(method)
        path_hash = self._stable_name_hash64(path)
        path_hashes = self._hot_section(packed, "exact_path_hashes")
        program_ids = self._hot_section(packed, "exact_program_ids")
        method_slices = self._resolve_hot_exact_route_slices(packed)
        method_slice = method_slices.get(method_id)
        if (
            method_slice is not None
            and path_hashes is not None
            and program_ids is not None
            and int(path_hashes.count) == int(program_ids.count)
        ):
            start_index, count = method_slice
            found_index = path_hashes.find_aligned_u64(
                path_hash,
                start_index=start_index,
                count=count,
            )
            if start_index <= found_index < start_index + count:
                program_id = int(program_ids.get_int(found_index))
                verify = self._resolve_hot_exact_route_verify(packed)
                method_verify = verify.get(method_id, {})
                candidates = method_verify.get(path_hash, ())
                if candidates:
                    for candidate_path, candidate_program_id in candidates:
                        if candidate_path == path:
                            return int(candidate_program_id)
                    return -1
                return program_id
        method_ids = self._hot_array(packed, "exact_method_ids", tuple())
        path_hash_array = self._hot_array(packed, "exact_path_hashes", tuple())
        program_id_array = self._hot_array(packed, "exact_program_ids", tuple())
        for candidate_method_id, candidate_hash, program_id in zip(
            method_ids, path_hash_array, program_id_array
        ):
            if (
                int(candidate_method_id) == int(method_id)
                and int(candidate_hash) == int(path_hash)
            ):
                return int(program_id)
        route = getattr(packed, "rest_exact_route_to_program", None)
        if not isinstance(route, Mapping):
            return -1
        maybe = route.get((method.upper(), path))
        return maybe if isinstance(maybe, int) else -1

    def _resolve_hot_exact_route_verify(
        self, packed: PackedKernel
    ) -> Mapping[int, Mapping[int, tuple[tuple[str, int], ...]]]:
        packed_id = id(packed)
        cached = self._hot_exact_route_verify_cache.get(packed_id)
        if cached is not None:
            return cached

        route = getattr(packed, "rest_exact_route_to_program", None)
        if not isinstance(route, Mapping):
            self._hot_exact_route_verify_cache[packed_id] = {}
            return {}

        verify: dict[int, dict[int, list[tuple[str, int]]]] = {}
        for route_key, program_id in route.items():
            if (
                not isinstance(route_key, tuple)
                or len(route_key) != 2
                or not isinstance(route_key[0], str)
                or not isinstance(route_key[1], str)
                or not isinstance(program_id, int)
            ):
                continue
            method_name, exact_path = route_key
            method_id = self._http_method_id(method_name)
            path_hash = self._stable_name_hash64(exact_path)
            method_bucket = verify.setdefault(method_id, {})
            method_bucket.setdefault(path_hash, []).append((exact_path, program_id))

        frozen = {
            int(method_id): {
                int(path_hash): tuple(entries)
                for path_hash, entries in method_bucket.items()
            }
            for method_id, method_bucket in verify.items()
        }
        self._hot_exact_route_verify_cache[packed_id] = frozen
        return frozen

    def _resolve_hot_exact_jsonrpc_routes(
        self, plan: KernelPlan
    ) -> Mapping[str, Mapping[str, tuple[int, str, str]]]:
        plan_id = id(plan)
        cached = self._hot_exact_jsonrpc_cache.get(plan_id)
        if cached is not None:
            return cached

        proto_indices = getattr(plan, "proto_indices", {}) or {}
        exact_routes: dict[str, dict[str, tuple[int, str, str]]] = {}
        if isinstance(proto_indices, Mapping):
            for proto, bucket in proto_indices.items():
                if not isinstance(proto, str) or not proto.endswith(".jsonrpc"):
                    continue
                if not isinstance(bucket, Mapping):
                    continue
                endpoints = bucket.get("endpoints")
                if not isinstance(endpoints, Mapping):
                    continue
                for endpoint, endpoint_bucket in endpoints.items():
                    if not isinstance(endpoint, str) or not endpoint:
                        continue
                    if not isinstance(endpoint_bucket, Mapping):
                        continue
                    method_map = exact_routes.setdefault(endpoint, {})
                    for rpc_method, entry in endpoint_bucket.items():
                        if not isinstance(rpc_method, str) or not rpc_method:
                            continue
                        if not isinstance(entry, Mapping):
                            continue
                        meta_index = entry.get("meta_index")
                        if not isinstance(meta_index, int):
                            continue
                        selector = str(
                            entry.get("selector") or f"{endpoint}:{rpc_method}"
                        )
                        method_map[rpc_method] = (meta_index, str(proto), selector)

        frozen = {
            endpoint: dict(method_map)
            for endpoint, method_map in exact_routes.items()
        }
        self._hot_exact_jsonrpc_cache[plan_id] = frozen
        return frozen

    @staticmethod
    def _normalize_jsonrpc_mount_path(path: str) -> str:
        normalized = str(path or "").rstrip("/")
        return normalized or "/"

    def _resolve_jsonrpc_endpoint_for_path(self, ctx: _Ctx, hot: HotCtx) -> str | None:
        path = self._normalize_jsonrpc_mount_path(hot.path)
        for owner_key in ("router", "app"):
            owner = getattr(ctx, owner_key, None)
            if owner is None and hasattr(ctx, "get"):
                owner = ctx.get(owner_key)
            mounts = getattr(owner, "_jsonrpc_endpoint_mounts", None)
            if isinstance(mounts, Mapping):
                endpoint = mounts.get(path) or mounts.get(hot.path) or mounts.get(f"{path}/")
                if isinstance(endpoint, str) and endpoint:
                    return endpoint
        for endpoint, mapped_path in __JSONRPC_DEFAULT_ENDPOINT_MAPPINGS__.items():
            if path == self._normalize_jsonrpc_mount_path(str(mapped_path)):
                return str(endpoint)
        return None

    async def _prime_exact_jsonrpc_program(
        self,
        ctx: _Ctx,
        env: Any,
        plan: KernelPlan,
        packed: PackedKernel,
    ) -> int:
        hot = self._ensure_hot_ctx(ctx, env)
        if hot.scope_type != "http" or str(hot.method or "").upper() != "POST":
            return -1

        endpoint = self._resolve_jsonrpc_endpoint_for_path(ctx, hot)
        if not endpoint:
            return -1

        request = self._ensure_hot_request(ctx, hot)
        body_bytes = await self._ensure_body_bytes(ctx, hot)
        if request is not None and body_bytes is not None and hasattr(request, "body"):
            request.body = body_bytes

        if not hot.parsed_json_loaded:
            parsed = None
            if body_bytes:
                try:
                    parsed = json.loads(body_bytes)
                except Exception:
                    parsed = None
            hot.parsed_json = parsed
            hot.parsed_json_loaded = True

        rpc_envelope = hot.parsed_json
        if not isinstance(rpc_envelope, dict) or rpc_envelope.get("jsonrpc") != "2.0":
            return -1
        rpc_method = rpc_envelope.get("method")
        if not isinstance(rpc_method, str) or not rpc_method:
            return -1

        routes = self._resolve_hot_exact_jsonrpc_routes(plan)
        endpoint_bucket = routes.get(endpoint)
        if not isinstance(endpoint_bucket, Mapping):
            return -1
        entry = endpoint_bucket.get(rpc_method)
        if not (
            isinstance(entry, tuple)
            and len(entry) == 3
            and isinstance(entry[0], int)
            and isinstance(entry[1], str)
            and isinstance(entry[2], str)
        ):
            return -1

        program_id, binding_protocol, binding_selector = entry
        hot.program_id = int(program_id)
        hot.route_program_id = int(program_id)
        hot.route_opmeta_index = int(program_id)
        hot.route_protocol = binding_protocol
        hot.route_selector = binding_selector
        hot.dispatch_binding_protocol = binding_protocol
        hot.dispatch_binding_selector = binding_selector
        hot.dispatch_jsonrpc_request_id = rpc_envelope.get("id")
        hot.dispatch_rpc_method = rpc_method
        hot.route_rpc_envelope = rpc_envelope
        hot.dispatch_rpc_envelope = rpc_envelope
        params = rpc_envelope.get("params")
        hot.route_payload = params if isinstance(params, dict) else None
        hot.transport_kind_id = _TRANSPORT_KIND_JSONRPC

        temp = getattr(ctx, "temp", None)
        if isinstance(temp, dict):
            temp["program_id"] = int(program_id)

        ctx.method = hot.method
        ctx.path = hot.path
        ctx.selector = binding_selector
        ctx.endpoint = endpoint
        return int(program_id)

    def _prime_exact_route_program(
        self, ctx: _Ctx, env: Any, packed: PackedKernel
    ) -> int:
        hot = self._ensure_hot_ctx(ctx, env)
        if hot.scope_type != "http" or not hot.method or not hot.path:
            return -1
        program_id = self._resolve_program_id_from_exact_route(
            packed, hot.method, hot.path
        )
        if program_id < 0:
            return -1

        temp = getattr(ctx, "temp", None)
        if not isinstance(temp, dict):
            return -1

        proto_to_id = getattr(packed, "proto_to_id", None)
        selector_to_id = getattr(packed, "selector_to_id", None)
        if isinstance(proto_to_id, Mapping):
            proto_id = self._coerce_int(proto_to_id.get(hot.protocol))
            if proto_id is not None:
                hot.proto_id = proto_id
        if isinstance(selector_to_id, Mapping):
            selector_id = self._coerce_int(selector_to_id.get(hot.selector))
            if selector_id is not None:
                hot.selector_id = selector_id
        hot.program_id = program_id
        hot.route_program_id = program_id
        hot.route_opmeta_index = program_id
        if not hot.route_protocol:
            hot.route_protocol = hot.protocol
        if not hot.route_selector:
            hot.route_selector = hot.selector
        if not hot.dispatch_binding_protocol:
            hot.dispatch_binding_protocol = hot.route_protocol or hot.protocol
        if not hot.dispatch_binding_selector:
            hot.dispatch_binding_selector = hot.route_selector or hot.selector
        hot.transport_kind_id = _TRANSPORT_KIND_REST

        ctx.method = hot.method
        ctx.path = hot.path
        temp["program_id"] = program_id
        return program_id

    @classmethod
    def _prepare_compiled_dispatch_prelude(
        cls,
        ctx: _Ctx,
        packed: PackedKernel,
        program_id: int,
        hot_op_plan: Any | None,
    ) -> HotCtx | None:
        temp = getattr(ctx, "temp", None)
        if not isinstance(temp, dict):
            return None
        hot = dict.get(temp, "hot_ctx")
        if not isinstance(hot, HotCtx):
            return None
        hot.program_id = program_id
        hot.route_program_id = program_id
        hot.route_opmeta_index = program_id
        if not hot.route_protocol:
            hot.route_protocol = hot.protocol
        if not hot.route_selector:
            hot.route_selector = hot.selector
        if not hot.dispatch_binding_protocol:
            hot.dispatch_binding_protocol = hot.route_protocol or hot.protocol
        if not hot.dispatch_binding_selector:
            hot.dispatch_binding_selector = hot.route_selector or hot.selector
        if hot.scope_type in {"websocket", "webtransport"}:
            if not hot.dispatch_channel_protocol:
                hot.dispatch_channel_protocol = hot.route_protocol or hot.protocol
            if not hot.dispatch_channel_selector:
                hot.dispatch_channel_selector = hot.route_selector or hot.selector
        hot.transport_kind_id = cls._resolve_program_transport_kind_id(
            packed, program_id, hot_op_plan
        )
        if hot.method and getattr(ctx, "method", None) in (None, ""):
            ctx.method = hot.method
        if hot.path and getattr(ctx, "path", None) in (None, ""):
            ctx.path = hot.path
        proto_to_id = getattr(packed, "proto_to_id", None)
        if hot.proto_id < 0 and isinstance(proto_to_id, Mapping):
            proto_id = cls._coerce_int(proto_to_id.get(hot.protocol))
            if proto_id is not None:
                hot.proto_id = proto_id
        selector_to_id = getattr(packed, "selector_to_id", None)
        if hot.selector_id < 0 and isinstance(selector_to_id, Mapping):
            selector_id = cls._coerce_int(selector_to_id.get(hot.selector))
            if selector_id is not None:
                hot.selector_id = selector_id
        return hot

    async def _probe_ingress_for_program(
        self, ctx: _Ctx, plan: KernelPlan, packed: PackedKernel
    ) -> int:
        if not getattr(plan, "opmeta", None):
            return -1

        seed_program_id = 0
        segment_offsets = self._hot_array(
            packed,
            "program_segment_offsets",
            tuple(getattr(packed, "program_segment_ref_offsets", ()) or getattr(packed, "op_segment_offsets", ()) or ()),
        )
        segment_lengths = self._hot_array(
            packed,
            "program_segment_lengths",
            tuple(getattr(packed, "program_segment_ref_lengths", ()) or getattr(packed, "op_segment_lengths", ()) or ()),
        )
        segment_refs = self._hot_array(
            packed,
            "program_segment_refs",
            tuple(getattr(packed, "program_segment_refs", ()) or getattr(packed, "op_to_segment_ids", ()) or ()),
        )
        segment_phases = self._segment_phase_names(packed)
        seg_offset = segment_offsets[seed_program_id]
        seg_length = segment_lengths[seed_program_id]
        for i in range(seg_offset, seg_offset + seg_length):
            seg_id = segment_refs[i]
            phase = str(segment_phases[seg_id])
            if not phase.startswith("INGRESS_"):
                break
            await self._run_segment(ctx, packed, seg_id)

        temp = getattr(ctx, "temp", None)
        if isinstance(temp, dict):
            temp["ingress_probed"] = True

        return self._require_program_id_from_ctx(ctx)

    def _resolve_segment_step_ids(
        self, packed: PackedKernel
    ) -> tuple[tuple[int, ...], ...]:
        packed_id = id(packed)
        cached = self._segment_steps_cache.get(packed_id)
        if cached is not None:
            return cached
        offsets_fallback = tuple(
            getattr(packed, "segment_catalog_offsets", ())
            or getattr(packed, "segment_offsets", ())
            or ()
        )
        lengths_fallback = tuple(
            getattr(packed, "segment_catalog_lengths", ())
            or getattr(packed, "segment_lengths", ())
            or ()
        )
        atom_refs_fallback = tuple(
            getattr(packed, "segment_catalog_atom_ids", ())
            or getattr(packed, "segment_step_ids", ())
            or ()
        )
        compiled = []
        for segment_index in range(
            self._hot_count(packed, "segment_step_offsets", offsets_fallback)
        ):
            start = self._hot_int_at(
                packed,
                "segment_step_offsets",
                segment_index,
                offsets_fallback,
            )
            length = self._hot_int_at(
                packed,
                "segment_step_lengths",
                segment_index,
                lengths_fallback,
            )
            if start is None or length is None:
                compiled.append(())
                continue
            end = int(start) + int(length)
            compiled.append(
                tuple(
                    int(
                        self._hot_int_at(
                            packed,
                            "segment_step_atom_refs",
                            idx,
                            atom_refs_fallback,
                        )
                        or 0
                    )
                    for idx in range(int(start), end)
                )
            )
        frozen = tuple(compiled)
        self._segment_steps_cache[packed_id] = frozen
        return frozen

    def _resolve_segment_runners(self, packed: PackedKernel) -> tuple[Any, ...]:
        packed_id = id(packed)
        cached = self._segment_runners_cache.get(packed_id)
        if cached is not None:
            return cached

        step_ids_by_segment = self._resolve_segment_step_ids(packed)
        async_flags = tuple(
            1 if bool(flag) else 0
            for flag in self._hot_array(
                packed,
                "atom_flags",
                tuple(
                    getattr(packed, "atom_catalog_async_flags", ())
                    or getattr(packed, "step_async_flags", ())
                    or ()
                ),
            )
        )
        executor_kinds = tuple(
            self._hot_array(
                packed,
                "segment_executor_kind_ids",
                tuple(getattr(packed, "segment_catalog_executor_kinds", ()) or getattr(packed, "segment_executor_kinds", ()) or ()),
            )
        )

        step_table = packed.step_table

        def _make_fused_sync_runner(step_ids: tuple[int, ...]):
            steps = tuple(step_table[step_id] for step_id in step_ids)

            async def _runner(ctx: _Ctx) -> None:
                for step in steps:
                    step(ctx)

            return _runner

        def _make_async_direct_runner(step_ids: tuple[int, ...]):
            steps = tuple(step_table[step_id] for step_id in step_ids)

            async def _runner(ctx: _Ctx) -> None:
                for step in steps:
                    await step(ctx)

            return _runner

        def _make_mixed_runner(step_ids: tuple[int, ...]):
            steps = tuple(
                (
                    step_table[step_id],
                    async_flags[step_id] if step_id < len(async_flags) else False,
                )
                for step_id in step_ids
            )

            async def _runner(ctx: _Ctx) -> None:
                for step, is_async in steps:
                    if is_async:
                        await step(ctx)
                        continue
                    rv = step(ctx)
                    if inspect.isawaitable(rv):
                        await rv

            return _runner

        runners: list[Any] = []
        for seg_id, step_ids in enumerate(step_ids_by_segment):
            executor_kind = executor_kinds[seg_id] if seg_id < len(executor_kinds) else ""
            if executor_kind in {"sync.extractable", 1}:
                runners.append(_make_fused_sync_runner(step_ids))
            elif executor_kind in {"async.direct", 3}:
                runners.append(_make_async_direct_runner(step_ids))
            else:
                runners.append(_make_mixed_runner(step_ids))

        frozen = tuple(runners)
        self._segment_runners_cache[packed_id] = frozen
        return frozen

    @classmethod
    def _resolve_program_hot_runner_id(
        cls,
        packed: PackedKernel,
        program_id: int,
        hot_op_plan: Any | None,
    ) -> int:
        if hot_op_plan is not None:
            program_hot_runner_id = cls._coerce_int(
                getattr(hot_op_plan, "program_hot_runner_id", None)
            )
            if program_hot_runner_id is not None:
                return program_hot_runner_id
        fallback = tuple(getattr(packed, "program_hot_runner_ids", ()) or ())
        value = cls._hot_int_at(
            packed,
            "program_hot_runner_ids",
            program_id,
            fallback,
        )
        return int(value) if value is not None else _HOT_RUNNER_GENERIC

    def _resolve_program_linear_direct_runner(
        self,
        packed: PackedKernel,
        program_id: int,
        hot_op_plan: Any | None,
    ) -> Any:
        cache_key = (id(packed), program_id, _HOT_RUNNER_LINEAR_DIRECT)
        cached = self._program_runner_cache.get(cache_key)
        if cached is not None:
            return cached

        if hot_op_plan is not None:
            ordered = tuple(getattr(hot_op_plan, "ordered_segment_ids", ()) or ())
            remaining = tuple(getattr(hot_op_plan, "remaining_segment_ids", ()) or ())
        else:
            ordered, remaining = self._resolve_segments_for_program(packed, program_id)

        phase_names = self._segment_phase_names(packed)
        step_ids_by_segment = self._resolve_segment_step_ids(packed)
        async_flags = tuple(
            1 if bool(flag) else 0
            for flag in self._hot_array(
                packed,
                "atom_flags",
                tuple(
                    getattr(packed, "atom_catalog_async_flags", ())
                    or getattr(packed, "step_async_flags", ())
                    or ()
                ),
            )
        )
        compiled_steps: list[tuple[str, int, Any, Any, bool]] = []
        step_table = packed.step_table
        for seg_id in (*ordered, *remaining):
            phase_name = str(normalize_phase(phase_names[seg_id]))
            for step_id in step_ids_by_segment[seg_id]:
                step = step_table[step_id]
                direct_run = getattr(step, "__tigrbl_direct_run", None)
                if callable(direct_run):
                    direct_dep = getattr(step, "__tigrbl_direct_dep", None)
                    has_direct_dep = bool(
                        getattr(step, "__tigrbl_has_direct_dep", False)
                    )
                    direct_is_async = bool(
                        getattr(step, "__tigrbl_direct_is_async", False)
                    )
                    use_two_args = bool(getattr(step, "__tigrbl_use_two_args", False))
                    invoke_kind = (
                        _DIRECT_INVOKE_RUN_WITH_DEP
                        if has_direct_dep
                        else (
                            _DIRECT_INVOKE_RUN_WITH_NONE
                            if use_two_args
                            else _DIRECT_INVOKE_RUN
                        )
                    )
                    compiled_steps.append(
                        (
                            phase_name,
                            invoke_kind,
                            direct_run,
                            direct_dep,
                            direct_is_async,
                        )
                    )
                    continue
                compiled_steps.append(
                    (
                        phase_name,
                        _DIRECT_INVOKE_STEP,
                        step,
                        None,
                        bool(async_flags[step_id]) if step_id < len(async_flags) else False,
                    )
                )

        async def _runner(ctx: _Ctx) -> None:
            current_phase = ""
            for phase_name, invoke_kind, call, dep, is_async in compiled_steps:
                if phase_name != current_phase:
                    ctx.phase = phase_name
                    current_phase = phase_name
                if invoke_kind == _DIRECT_INVOKE_RUN_WITH_DEP:
                    rv = call(dep, ctx)
                elif invoke_kind == _DIRECT_INVOKE_RUN_WITH_NONE:
                    rv = call(None, ctx)
                else:
                    rv = call(ctx)
                if is_async:
                    await rv
                elif rv is not None and callable(getattr(type(rv), "__await__", None)):
                    close = getattr(rv, "close", None)
                    if callable(close):
                        close()
                    raise RuntimeError(
                        f"sync compiled step returned awaitable in phase {phase_name!r}"
                    )

        self._program_runner_cache[cache_key] = _runner
        return _runner

    def _resolve_program_compiled_param_runner(
        self,
        packed: PackedKernel,
        program_id: int,
        hot_op_plan: Any | None,
    ) -> Any:
        cache_key = (id(packed), program_id, _HOT_RUNNER_COMPILED_PARAM)
        cached = self._program_runner_cache.get(cache_key)
        if cached is not None:
            return cached

        if hot_op_plan is not None:
            ordered = tuple(getattr(hot_op_plan, "ordered_segment_ids", ()) or ())
            remaining = tuple(getattr(hot_op_plan, "remaining_segment_ids", ()) or ())
            compiled_param_phase_steps = tuple(
                getattr(hot_op_plan, "compiled_param_phase_steps", ()) or ()
            )
        else:
            ordered, remaining = self._resolve_segments_for_program(packed, program_id)
            compiled_param_phase_steps = ()

        phase_names = self._segment_phase_names(packed)
        step_ids_by_segment = self._resolve_segment_step_ids(packed)
        async_flags = tuple(
            1 if bool(flag) else 0
            for flag in self._hot_array(
                packed,
                "atom_flags",
                tuple(
                    getattr(packed, "atom_catalog_async_flags", ())
                    or getattr(packed, "step_async_flags", ())
                    or ()
                ),
            )
        )
        opcode_ids = tuple(
            int(value)
            for value in self._hot_array(
                packed,
                "atom_opcode_ids",
                tuple(getattr(packed, "atom_catalog_opcode_ids", ()) or ()),
            )
        )
        opcode_keys = tuple(getattr(packed, "atom_opcode_keys", ()) or ())
        skip_step_ids: set[int] = set()
        skip_names = {
            "ingress.transport_extract",
            "ingress.input_prepare",
            "dispatch.binding_match",
            "dispatch.binding_parse",
            "dispatch.input_normalize",
            "wire.build_in",
            "wire.validate_in",
            "resolve.assemble",
            "sys.phase_db",
        }
        for step_id, opcode_id in enumerate(opcode_ids):
            if 0 <= opcode_id < len(opcode_keys):
                if str(opcode_keys[opcode_id]) in skip_names:
                    skip_step_ids.add(step_id)

        compiled_steps: list[tuple[str, int, Any, Any, bool]] = []
        phase_requires_db: dict[str, bool] = {}
        step_table = packed.step_table
        def _append_compiled_step(
            phase_name: str,
            step: Any,
            *,
            is_async: bool,
        ) -> None:
            if bool(getattr(step, "__tigrbl_skip_in_compiled_param", False)):
                return
            if bool(getattr(step, "__tigrbl_requires_phase_db", False)):
                phase_requires_db[phase_name] = True
            direct_run = getattr(step, "__tigrbl_direct_run", None)
            if callable(direct_run):
                direct_dep = getattr(step, "__tigrbl_direct_dep", None)
                has_direct_dep = bool(
                    getattr(step, "__tigrbl_has_direct_dep", False)
                )
                direct_is_async = bool(
                    getattr(step, "__tigrbl_direct_is_async", False)
                )
                use_two_args = bool(getattr(step, "__tigrbl_use_two_args", False))
                invoke_kind = (
                    _DIRECT_INVOKE_RUN_WITH_DEP
                    if has_direct_dep
                    else (
                        _DIRECT_INVOKE_RUN_WITH_NONE
                        if use_two_args
                        else _DIRECT_INVOKE_RUN
                    )
                )
                compiled_steps.append(
                    (
                        phase_name,
                        invoke_kind,
                        direct_run,
                        direct_dep,
                        direct_is_async,
                    )
                )
                return
            compiled_steps.append(
                (
                    phase_name,
                    _DIRECT_INVOKE_STEP,
                    step,
                    None,
                    is_async,
                )
            )

        if compiled_param_phase_steps:
            for phase_name, phase_steps in compiled_param_phase_steps:
                normalized_phase = str(normalize_phase(phase_name))
                for step in phase_steps:
                    atom_name = getattr(step, "__tigrbl_atom_name__", None)
                    if atom_name in skip_names:
                        continue
                    step_is_async = bool(getattr(step, "_tigrbl_is_async", False))
                    if not step_is_async:
                        marker = getattr(step, "__code__", None)
                        step_is_async = bool(getattr(marker, "co_flags", 0) & 0x80)
                    _append_compiled_step(
                        normalized_phase,
                        step,
                        is_async=step_is_async,
                    )
        else:
            for seg_id in (*ordered, *remaining):
                phase_name = str(normalize_phase(phase_names[seg_id]))
                for step_id in step_ids_by_segment[seg_id]:
                    step = step_table[step_id]
                    if step_id in skip_step_ids:
                        continue
                    _append_compiled_step(
                        phase_name,
                        step,
                        is_async=bool(async_flags[step_id]) if step_id < len(async_flags) else False,
                    )

        async def _runner(ctx: _Ctx) -> None:
            hot = self._prepare_compiled_dispatch_prelude(
                ctx, packed, program_id, hot_op_plan
            )
            if hot is None:
                return
            await self._prepare_compiled_input(ctx, hot, packed, program_id, hot_op_plan)
            if hot.compiled_input_ready:
                plan = self._resolve_compiled_param_plan(
                    ctx,
                    packed,
                    program_id,
                    hot.param_shape_id,
                )
                self._compiled_validate_and_assemble(ctx, hot, plan)
            current_phase = ""
            for phase_name, invoke_kind, call, dep, is_async in compiled_steps:
                if phase_name != current_phase:
                    ctx.phase = phase_name
                    current_phase = phase_name
                    if getattr(ctx, "_raw_db", None) is not None:
                        from tigrbl_atoms.atoms.sys.phase_db import bind_phase_db

                        bind_phase_db(ctx)
                if invoke_kind == _DIRECT_INVOKE_RUN_WITH_DEP:
                    rv = call(dep, ctx)
                elif invoke_kind == _DIRECT_INVOKE_RUN_WITH_NONE:
                    rv = call(None, ctx)
                else:
                    rv = call(ctx)
                if is_async:
                    await rv
                elif rv is not None and callable(getattr(type(rv), "__await__", None)):
                    close = getattr(rv, "close", None)
                    if callable(close):
                        close()
                    raise RuntimeError(
                        f"sync compiled step returned awaitable in phase {phase_name!r}"
                    )

        self._program_runner_cache[cache_key] = _runner
        return _runner

    def _resolve_program_websocket_unary_text_runner(
        self,
        packed: PackedKernel,
        program_id: int,
        hot_op_plan: Any | None,
    ) -> Any:
        cache_key = (id(packed), program_id, _HOT_RUNNER_WS_UNARY_TEXT)
        cached = self._program_runner_cache.get(cache_key)
        if cached is not None:
            return cached

        endpoint = getattr(hot_op_plan, "websocket_direct_endpoint", None)
        if not callable(endpoint):
            runner = self._resolve_program_linear_direct_runner(
                packed, program_id, hot_op_plan
            )
            self._program_runner_cache[cache_key] = runner
            return runner
        endpoint_is_async = inspect.iscoroutinefunction(endpoint)

        async def _runner(ctx: _Ctx) -> None:
            temp = getattr(ctx, "temp", None)
            hot = dict.get(temp, "hot_ctx") if isinstance(temp, dict) else None
            if not isinstance(hot, HotCtx):
                raise RuntimeError("websocket fast runner requires hot websocket context")
            receive = hot.raw_receive
            send = hot.raw_send
            if not callable(send):
                raise RuntimeError("websocket fast runner requires send callable")
            first_message: Mapping[str, Any] | None = None
            if callable(receive):
                initial = await receive()
                if isinstance(initial, Mapping):
                    if initial.get("type") == "websocket.connect":
                        next_message = await receive() if callable(receive) else {"type": "websocket.disconnect", "code": 1000}
                        first_message = (
                            next_message
                            if isinstance(next_message, Mapping)
                            else {"type": "websocket.disconnect", "code": 1000}
                        )
                    else:
                        first_message = initial
            websocket = _DirectWebSocketUnary(
                receive=receive,
                send=send,
                path=hot.path,
                path_params=hot.route_path_params or hot.path_params,
                buffered_message=first_message,
            )
            ctx.phase = "HANDLER"
            await websocket.accept()
            if endpoint_is_async:
                result = await endpoint(websocket)
            else:
                result = endpoint(websocket)
            if result is not None:
                ctx.result = result
            if result is not None and not websocket.sent_payload and not websocket.closed:
                if isinstance(result, memoryview):
                    await websocket.send_bytes(result.tobytes())
                elif isinstance(result, (bytes, bytearray)):
                    await websocket.send_bytes(bytes(result))
                elif isinstance(result, str):
                    await websocket.send_text(result)
                else:
                    try:
                        payload_text = json.dumps(result, separators=(",", ":"))
                    except TypeError:
                        payload_text = json.dumps(
                            result, separators=(",", ":"), default=str
                        )
                    await websocket.send_text(payload_text)
            hot.egress_sent = websocket.sent_payload
            if not websocket.closed:
                await websocket.close(1000)

        self._program_runner_cache[cache_key] = _runner
        return _runner

    def _resolve_program_runner(
        self, packed: PackedKernel, program_id: int, hot_op_plan: Any | None
    ) -> Any:
        cache_key = (id(packed), program_id)
        cached = self._program_runner_cache.get(cache_key)
        if cached is not None:
            return cached
        program_hot_runner_id = self._resolve_program_hot_runner_id(
            packed, program_id, hot_op_plan
        )
        if program_hot_runner_id == _HOT_RUNNER_COMPILED_PARAM:
            runner = self._resolve_program_compiled_param_runner(
                packed, program_id, hot_op_plan
            )
            self._program_runner_cache[cache_key] = runner
            return runner
        if program_hot_runner_id == _HOT_RUNNER_WS_UNARY_TEXT:
            runner = self._resolve_program_websocket_unary_text_runner(
                packed, program_id, hot_op_plan
            )
            self._program_runner_cache[cache_key] = runner
            return runner
        if program_hot_runner_id == _HOT_RUNNER_LINEAR_DIRECT:
            runner = self._resolve_program_linear_direct_runner(
                packed, program_id, hot_op_plan
            )
            self._program_runner_cache[cache_key] = runner
            return runner
        runners = self._resolve_segment_runners(packed)
        if hot_op_plan is not None:
            ordered = tuple(getattr(hot_op_plan, "ordered_segment_ids", ()) or ())
            remaining = tuple(getattr(hot_op_plan, "remaining_segment_ids", ()) or ())
        else:
            ordered, remaining = self._resolve_segments_for_program(packed, program_id)
        phase_names = self._segment_phase_names(packed)
        all_segment_ids = (*ordered, *remaining)

        async def _runner(ctx: _Ctx) -> None:
            temp = getattr(ctx, "temp", None)
            skip_dispatch = bool(
                isinstance(temp, dict) and temp.get("_tigrbl_hot_exact_route")
            )
            fast_direct_create = bool(
                isinstance(temp, dict) and temp.get("_tigrbl_hot_direct_create")
            )
            for seg_id in all_segment_ids:
                phase_name = str(normalize_phase(phase_names[seg_id]))
                if skip_dispatch and phase_name in {
                    "INGRESS_BEGIN",
                    "INGRESS_DISPATCH",
                }:
                    continue
                if fast_direct_create and phase_name in {
                    "POST_COMMIT",
                    "EGRESS_SHAPE",
                    "EGRESS_FINALIZE",
                    "POST_RESPONSE",
                }:
                    continue
                ctx.phase = phase_name
                await runners[seg_id](ctx)

        self._program_runner_cache[cache_key] = _runner
        return _runner

    def _resolve_program_runner_for_mode(
        self,
        packed: PackedKernel,
        program_id: int,
        hot_op_plan: Any | None,
        *,
        skip_dispatch: bool = False,
        fast_direct_create: bool = False,
    ) -> Any:
        mode = (1 if skip_dispatch else 0) | (2 if fast_direct_create else 0)
        cache_key = (id(packed), program_id, mode)
        cached = self._program_runner_mode_cache.get(cache_key)
        if cached is not None:
            return cached

        base_runner = self._resolve_program_runner(packed, program_id, hot_op_plan)
        if not skip_dispatch and not fast_direct_create:
            self._program_runner_mode_cache[cache_key] = base_runner
            return base_runner

        runners = self._resolve_segment_runners(packed)
        if hot_op_plan is not None:
            ordered = tuple(getattr(hot_op_plan, "ordered_segment_ids", ()) or ())
            remaining = tuple(getattr(hot_op_plan, "remaining_segment_ids", ()) or ())
        else:
            ordered, remaining = self._resolve_segments_for_program(packed, program_id)
        phase_names = self._segment_phase_names(packed)
        all_segment_ids = (*ordered, *remaining)

        skip_phases = set()
        if skip_dispatch:
            skip_phases.update({"INGRESS_BEGIN", "INGRESS_DISPATCH"})
        if fast_direct_create:
            skip_phases.update(
                {"POST_COMMIT", "EGRESS_SHAPE", "EGRESS_FINALIZE", "POST_RESPONSE"}
            )

        async def _runner(ctx: _Ctx) -> None:
            for seg_id in all_segment_ids:
                phase_name = str(normalize_phase(phase_names[seg_id]))
                if phase_name in skip_phases:
                    continue
                ctx.phase = phase_name
                await runners[seg_id](ctx)

        self._program_runner_mode_cache[cache_key] = _runner
        return _runner

    def _resolve_db_acquire(
        self,
        plan: KernelPlan,
        program_id: int,
        hot_op_plan: Any | None,
    ) -> Any:
        cache_key = (id(plan), program_id)
        cached = self._db_acquire_cache.get(cache_key)
        if cached is not None:
            return cached
        model = getattr(hot_op_plan, "model", None)
        alias = getattr(hot_op_plan, "alias", None)
        hint = str(getattr(hot_op_plan, "db_acquire_hint", "resolver") or "resolver")

        if hint == "model_get_db" and callable(
            getattr(model, "__tigrbl_get_db__", None)
        ):
            _resolver = import_module("tigrbl_concrete._concrete").engine_resolver

            def _acquire(_ctx: _Ctx) -> tuple[Any, Any]:
                return _resolver.acquire(model=model)

            self._db_acquire_cache[cache_key] = _acquire
            return _acquire

        provider_cache: dict[str, Any] = {}
        app_resolver_cache: dict[str, Any] = {}

        def _runtime_owner(ctx: _Ctx) -> Any:
            return getattr(ctx, "router", None) or getattr(ctx, "app", None)

        def _resolve_from_owner(ctx: _Ctx) -> Any:
            owner = _runtime_owner(ctx)
            if owner is None:
                return None
            if "resolver" in app_resolver_cache:
                return app_resolver_cache["resolver"]
            resolver = getattr(owner, "_tigrbl_runtime_resolve_provider", None)
            if callable(resolver):
                app_resolver_cache["resolver"] = resolver
                return resolver
            return None

        def _acquire_via_owner(ctx: _Ctx) -> tuple[Any, Any] | None:
            owner = _runtime_owner(ctx)
            acquire = getattr(owner, "_tigrbl_runtime_acquire_db", None)
            if callable(acquire):
                return acquire(
                    router=getattr(ctx, "router", None) or getattr(ctx, "app", None),
                    model=model,
                    op_alias=alias if isinstance(alias, str) else None,
                )
            return None

        def _release(db: Any) -> None:
            close = getattr(db, "close", None)
            if not callable(close):
                return
            try:
                rv = close()
                if inspect.isawaitable(rv):
                    try:
                        loop = asyncio.get_running_loop()
                    except RuntimeError:
                        asyncio.run(rv)
                    else:
                        loop.create_task(rv)
            except Exception:
                return

        def _acquire_from_provider(provider: Any) -> tuple[Any, Any]:
            db = provider.session()
            return db, lambda: _release(db)

        def _acquire(ctx: _Ctx) -> tuple[Any, Any]:
            owner_session = _acquire_via_owner(ctx)
            if owner_session is not None:
                return owner_session
            provider = provider_cache.get("provider")
            if provider is not None:
                return _acquire_from_provider(provider)
            resolver = _resolve_from_owner(ctx)
            provider = None
            if callable(resolver):
                provider = resolver(
                    router=getattr(ctx, "router", None) or getattr(ctx, "app", None),
                    model=model,
                    op_alias=alias if isinstance(alias, str) else None,
                )
            if provider is not None:
                provider_cache["provider"] = provider
                return _acquire_from_provider(provider)
            owner_session = _acquire_via_owner(ctx)
            if owner_session is not None:
                return owner_session
            raise RuntimeError("No runtime database acquisition callback is configured")

        self._db_acquire_cache[cache_key] = _acquire
        return _acquire

    async def _run_segment(self, ctx: _Ctx, packed: PackedKernel, seg_id: int) -> None:
        ctx.phase = normalize_phase(self._segment_phase_names(packed)[seg_id])
        await self._resolve_segment_runners(packed)[seg_id](ctx)

    async def _run_error_segments(
        self,
        ctx: _Ctx,
        packed: PackedKernel,
        error_phase_segments: Mapping[str, tuple[int, ...]],
        *phase_names: str,
    ) -> None:
        seen: set[str] = set()
        for phase_name in phase_names:
            if phase_name in seen:
                continue
            seen.add(phase_name)
            for seg_id in error_phase_segments.get(phase_name, ()):
                try:
                    await self._run_segment(ctx, packed, seg_id)
                except Exception:
                    pass

    async def _run_rollback_edge(
        self,
        ctx: _Ctx,
        packed: PackedKernel,
        error_phase_segments: Mapping[str, tuple[int, ...]],
    ) -> None:
        rollback_segments = error_phase_segments.get("TX_ROLLBACK", ())
        if rollback_segments:
            await self._run_error_segments(
                ctx,
                packed,
                error_phase_segments,
                "TX_ROLLBACK",
            )
            return

        db = getattr(ctx, "db", None) or getattr(ctx, "_raw_db", None)
        rollback = getattr(db, "rollback", None)
        if not callable(rollback):
            return
        rv = rollback()
        if inspect.isawaitable(rv):
            await rv

    async def _prepare_error_edge(
        self,
        ctx: _Ctx,
        packed: PackedKernel,
        error_phase_segments: Mapping[str, tuple[int, ...]],
        exc: BaseException,
    ) -> str:
        failed_phase = str(normalize_phase(getattr(ctx, "phase", "") or ""))
        rollback_required = failed_phase in {
            "START_TX",
            "PRE_HANDLER",
            "HANDLER",
            "POST_HANDLER",
            "PRE_COMMIT",
            "TX_COMMIT",
        } and bool(getattr(ctx, "owns_tx", False))
        edge = select_error_edge(
            failed_phase,
            rollback_required=rollback_required,
        )
        build_error_ctx(
            ctx,
            exc,
            failed_phase=failed_phase,
            err_target=edge.target,
            rollback_required=edge.target.kind == "rollback",
        )
        if edge.target.kind == "rollback":
            await self._run_rollback_edge(ctx, packed, error_phase_segments)
        return error_phase_for(failed_phase)

    def _resolve_error_segments(
        self,
        packed: PackedKernel,
        program_id: int,
    ) -> Mapping[str, tuple[int, ...]]:
        cache_key = (id(packed), program_id)
        cached = self._program_error_segments_cache.get(cache_key)
        if cached is not None:
            return cached[1]

        profile_ids = self._hot_array(
            packed,
            "program_error_profile_ids",
            tuple(getattr(packed, "program_error_profile_ids", ()) or ()),
        )
        profile_offsets = self._hot_array(
            packed,
            "error_profile_offsets",
            tuple(getattr(packed, "error_profile_offsets", ()) or ()),
        )
        if profile_offsets and program_id < len(profile_ids):
            phase_names = tuple(getattr(packed, "phase_names", ()) or ())
            profile_lengths = self._hot_array(packed, "error_profile_lengths", tuple(getattr(packed, "error_profile_lengths", ()) or ()))
            phase_ids = self._hot_array(packed, "error_profile_phase_ids", tuple(getattr(packed, "error_profile_phase_ids", ()) or ()))
            seg_ref_offsets = self._hot_array(packed, "error_profile_segment_offsets", tuple(getattr(packed, "error_profile_segment_ref_offsets", ()) or ()))
            seg_ref_lengths = self._hot_array(packed, "error_profile_segment_lengths", tuple(getattr(packed, "error_profile_segment_ref_lengths", ()) or ()))
            seg_refs = self._hot_array(packed, "error_profile_segment_refs", tuple(getattr(packed, "error_profile_segment_refs", ()) or ()))
            profile_id = profile_ids[program_id]
            if 0 <= profile_id < len(profile_offsets):
                start = profile_offsets[profile_id]
                length = profile_lengths[profile_id] if profile_id < len(profile_lengths) else 0
                frozen = {}
                for idx in range(start, start + length):
                    phase_id = phase_ids[idx]
                    phase_name = (
                        phase_names[phase_id]
                        if 0 <= phase_id < len(phase_names)
                        else str(phase_id)
                    )
                    seg_start = seg_ref_offsets[idx]
                    seg_length = seg_ref_lengths[idx]
                    frozen[str(normalize_phase(phase_name))] = tuple(
                        int(seg_refs[j]) for j in range(seg_start, seg_start + seg_length)
                    )
                ordered_segments, remaining_segments = self._resolve_segments_for_program(
                    packed, program_id
                )
                self._program_error_segments_cache[cache_key] = (
                    (*ordered_segments, *remaining_segments),
                    frozen,
                )
                return frozen

        grouped: dict[str, list[int]] = {}
        segment_offsets = self._hot_array(
            packed,
            "program_segment_offsets",
            tuple(getattr(packed, "program_segment_ref_offsets", ()) or getattr(packed, "op_segment_offsets", ()) or ()),
        )
        segment_lengths = self._hot_array(
            packed,
            "program_segment_lengths",
            tuple(getattr(packed, "program_segment_ref_lengths", ()) or getattr(packed, "op_segment_lengths", ()) or ()),
        )
        segment_refs = self._hot_array(
            packed,
            "program_segment_refs",
            tuple(getattr(packed, "program_segment_refs", ()) or getattr(packed, "op_to_segment_ids", ()) or ()),
        )
        segment_phases = self._segment_phase_names(packed)
        seg_offset = segment_offsets[program_id]
        seg_length = segment_lengths[program_id]
        for i in range(seg_offset, seg_offset + seg_length):
            seg_id = segment_refs[i]
            phase_name = str(normalize_phase(segment_phases[seg_id]))
            if phase_name.startswith("ON_") or phase_name == "TX_ROLLBACK":
                grouped.setdefault(phase_name, []).append(seg_id)

        ordered_segments, remaining_segments = self._resolve_segments_for_program(
            packed, program_id
        )
        frozen = {phase: tuple(seg_ids) for phase, seg_ids in grouped.items()}
        self._program_error_segments_cache[cache_key] = (
            (*ordered_segments, *remaining_segments),
            frozen,
        )
        return frozen

    async def _execute_packed(
        self, env: Any, ctx: _Ctx, plan: KernelPlan, packed: PackedKernel
    ) -> None:
        _send_json, _send_transport_response = self._resolve_transport_senders()
        StatusDetailError, create_standardized_error = self._resolve_error_helpers()

        temp = getattr(ctx, "temp", None)
        if not isinstance(temp, dict):
            ctx.temp = {}
            temp = ctx.temp

        hot = self._ensure_hot_ctx(ctx, env)
        ctx.plan = plan
        ctx.kernel_plan = plan
        if hot.method and getattr(ctx, "method", None) in (None, ""):
            ctx.method = hot.method
        if hot.path and getattr(ctx, "path", None) in (None, ""):
            ctx.path = hot.path
        if (
            hot.scope_type == "http"
            and str(hot.method or "").upper() == "POST"
            and self._resolve_jsonrpc_endpoint_for_path(ctx, hot)
        ):
            request = self._ensure_hot_request(ctx, hot)
            body_bytes = await self._ensure_body_bytes(ctx, hot)
            if request is not None and body_bytes is not None and hasattr(request, "body"):
                request.body = body_bytes
            if not hot.parsed_json_loaded:
                parsed = None
                if body_bytes:
                    try:
                        parsed = json.loads(body_bytes)
                    except Exception:
                        parsed = None
                hot.parsed_json = parsed
                hot.parsed_json_loaded = True
            if isinstance(hot.parsed_json, Mapping) and hot.parsed_json.get("jsonrpc") == "2.0":
                params = hot.parsed_json.get("params", {})
                if isinstance(params, Mapping) and set(params) == {"params"}:
                    egress = temp.setdefault("egress", {})
                    if isinstance(egress, dict):
                        egress["transport_response"] = {
                            "status_code": 204,
                            "body": b"",
                        }
                    hot.route_short_circuit = True
                    hot.route_rpc_envelope = dict(hot.parsed_json)
                    hot.dispatch_rpc_envelope = dict(hot.parsed_json)
                    await _send_transport_response(env, ctx)
                    return
            if isinstance(hot.parsed_json, list):
                await _send_json(
                    env,
                    200,
                    await self._execute_jsonrpc_batch(ctx, hot, hot.parsed_json),
                )
                return

        program_id = self._require_program_id_from_ctx(ctx)
        if program_id < 0:
            program_id = self._prime_exact_route_program(ctx, env, packed)
        if program_id < 0:
            program_id = await self._prime_exact_jsonrpc_program(
                ctx, env, plan, packed
            )
        if program_id < 0:
            program_id = self._prime_exact_websocket_program(ctx, env, plan, packed)
        if program_id < 0:
            program_id = await self._probe_ingress_for_program(ctx, plan, packed)
        if program_id < 0:
            scope = getattr(env, "scope", {}) or {}
            transport = hot.egress_transport_response
            if isinstance(transport, dict):
                await _send_transport_response(env, ctx)
                return

            if hot.route_method_not_allowed:
                await _send_json(env, 405, {"detail": "Method Not Allowed"})
                return
            if str(scope.get("type") or "") == "websocket":
                send = getattr(env, "send", None)
                if callable(send):
                    await send({"type": "websocket.close", "code": 4404})
                return
            await _send_json(
                env, 404, {"detail": "No runtime operation matched request."}
            )
            return

        temp["program_id"] = program_id

        hot_op_plan = (
            packed.hot_op_plans[program_id]
            if program_id < len(getattr(packed, "hot_op_plans", ()))
            else None
        )
        program_hot_runner_id = self._resolve_program_hot_runner_id(
            packed, program_id, hot_op_plan
        )

        if program_id >= len(plan.opmeta):
            await _send_json(
                env, 404, {"detail": "No runtime operation matched request."}
            )
            return
        if hot_op_plan is not None:
            ctx.model = hot_op_plan.model
            ctx.op = hot_op_plan.alias
            ctx.target = hot_op_plan.target
        else:
            meta = plan.opmeta[program_id]
            ctx.model = getattr(meta, "model", None)
            ctx.op = getattr(meta, "alias", None)
            ctx.target = getattr(meta, "target", None)
        env_ref = ctx.get("env")
        if env_ref is None:
            ctx["env"] = SimpleNamespace(method=ctx.op)
        elif getattr(env_ref, "method", None) in (None, "", "unknown"):
            try:
                setattr(env_ref, "method", ctx.op)
            except Exception:
                ctx["env"] = SimpleNamespace(method=ctx.op)
        release_db = None
        if (
            program_hot_runner_id != _HOT_RUNNER_WS_UNARY_TEXT
            and getattr(ctx, "_raw_db", None) is None
        ):
            try:
                acquire_db = self._resolve_db_acquire(plan, program_id, hot_op_plan)
                db, release_db = acquire_db(ctx)
                ctx._raw_db = db
                if getattr(ctx, "db", None) is None:
                    ctx.db = db
                ctx.owns_tx = True
            except Exception:
                release_db = None
        if (
            program_hot_runner_id != _HOT_RUNNER_WS_UNARY_TEXT
            and hot_op_plan is not None
            and hot_op_plan.opview is not None
        ):
            ctx.opview = hot_op_plan.opview
        elif program_hot_runner_id != _HOT_RUNNER_WS_UNARY_TEXT:
            app = getattr(ctx, "app", None)
            if app is not None and ctx.model is not None and isinstance(ctx.op, str):
                opview_key = (id(plan), program_id)
                opview = self._opview_cache.get(opview_key)
                if opview is None:
                    opview = self.runtime.kernel.get_opview(app, ctx.model, ctx.op)
                    self._opview_cache[opview_key] = opview
                ctx.opview = opview

        try:
            if hot_op_plan is not None:
                error_phase_segments = hot_op_plan.error_segment_ids
            else:
                error_phase_segments = self._resolve_error_segments(
                    packed,
                    program_id,
                )

            try:
                if hot.transport_kind_id == _TRANSPORT_KIND_JSONRPC and isinstance(
                    hot.parsed_json, dict
                ):
                    opview = getattr(ctx, "opview", None)
                    schema_in = getattr(opview, "schema_in", None)
                    field_names = tuple(getattr(schema_in, "fields", ()) or ())
                    self._reject_jsonrpc_wrapper_keys(
                        hot.parsed_json.get("params", {}),
                        field_names=field_names,
                    )
                await self._resolve_program_runner(
                    packed,
                    program_id,
                    hot_op_plan,
                )(ctx)
            except StatusDetailError as exc:
                detail = (
                    exc.detail
                    if getattr(exc, "detail", None) not in (None, "")
                    else str(exc)
                )
                error_phase = await self._prepare_error_edge(
                    ctx,
                    packed,
                    error_phase_segments,
                    exc,
                )
                fallback_phase = "ON_ERROR"
                await self._run_error_segments(
                    ctx,
                    packed,
                    error_phase_segments,
                    error_phase,
                    fallback_phase,
                )
                status_code = int(getattr(exc, "status_code", 500) or 500)
                payload = self._jsonrpc_error_payload(ctx, status_code, detail)
                await _send_json(
                    env,
                    200 if payload is not None else status_code,
                    payload or {"detail": detail},
                    headers=getattr(exc, "headers", None),
                )
                return
            except Exception as exc:
                std = create_standardized_error(exc)
                detail = (
                    std.detail
                    if getattr(std, "detail", None) not in (None, "")
                    else str(std)
                )
                error_phase = await self._prepare_error_edge(
                    ctx,
                    packed,
                    error_phase_segments,
                    exc,
                )
                fallback_phase = "ON_ERROR"
                await self._run_error_segments(
                    ctx,
                    packed,
                    error_phase_segments,
                    error_phase,
                    fallback_phase,
                )
                status_code = int(getattr(std, "status_code", 500) or 500)
                persistence_error = self._is_persistence_exception(exc)
                if persistence_error:
                    status_code = 500
                    detail = "Internal error"
                payload = self._jsonrpc_error_payload(
                    ctx,
                    status_code,
                    detail,
                    sanitize_detail=persistence_error,
                )
                await _send_json(
                    env,
                    200 if payload is not None else status_code,
                    payload or {"detail": detail},
                    headers=getattr(std, "headers", None),
                )
                return

            if program_hot_runner_id == _HOT_RUNNER_WS_UNARY_TEXT:
                return
            if isinstance(temp, dict) and temp.get("_tigrbl_hot_direct_create") is True:
                status = int(getattr(ctx, "status_code", 201) or 201)
                payload = self._serialize_model_row(getattr(ctx, "result", None))
                await _send_json(env, status, payload)
                return
            if hot.route_short_circuit and hot.egress_transport_response:
                await _send_transport_response(env, ctx)
                return

            await _send_transport_response(env, ctx)
        finally:
            if callable(release_db):
                try:
                    release_db()
                except Exception:
                    pass

    def _build_python_packed_executor(self, packed: PackedKernel):
        async def _executor(kernel: Any, env: Any, ctx: _Ctx, plan: KernelPlan) -> None:
            del kernel
            await self._execute_packed(env, ctx, plan, packed)

        return _executor

    def _build_numba_packed_executor(self, packed: PackedKernel):
        if not packed.route_to_program:
            return None
        try:
            from numba import njit
        except Exception:
            return None

        route_to_program = packed.route_to_program

        @njit(cache=True)
        def _dispatch(proto_id: int, selector_id: int) -> int:
            if proto_id < 0 or selector_id < 0:
                return -1
            if proto_id >= len(route_to_program):
                return -1
            row = route_to_program[proto_id]
            if selector_id >= len(row):
                return -1
            return row[selector_id]

        def _executor(proto_id: int, selector_id: int) -> int:
            return int(_dispatch(int(proto_id), int(selector_id)))

        return _executor

    async def invoke(
        self,
        *,
        runtime: Any,
        env: Any,
        ctx: Any,
        plan: Any,
        packed_plan: Any | None = None,
    ) -> Any:
        if not isinstance(plan, KernelPlan):
            raise TypeError("PackedPlanExecutor requires a KernelPlan instance")
        if not isinstance(packed_plan, PackedKernel):
            raise TypeError("PackedPlanExecutor requires a PackedKernel instance")

        base_ctx = _Ctx.ensure(
            request=ctx.get("request") if isinstance(ctx, Mapping) else None,
            db=ctx.get("db") if isinstance(ctx, Mapping) else None,
            seed=ctx,
        )
        await self._execute_packed(env, base_ctx, plan, packed_plan)
        return base_ctx.get("result")


__all__ = ["PackedPlanExecutor"]
