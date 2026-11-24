from __future__ import annotations

from tigrbl_atoms.atoms.ingress.identity import invocation_identity

from ._shared import *
from ...channel._asgi_jsonrpc import _jsonrpc_error_payload


class _PackedBatchMixin:
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
        self._seed_batch_policy_from_hot_plan(ctx, hot_op_plan)
        self._seed_batch_scheduler(ctx, hot_op_plan, env)
        return True

    @classmethod
    def _batch_policy_mapping(cls, hot_op_plan: Any | None) -> dict[str, Any]:
        if hot_op_plan is None:
            return {}
        batch = getattr(hot_op_plan, "batch", None)
        if isinstance(batch, Mapping):
            return dict(batch)
        if is_dataclass(batch):
            return {field.name: getattr(batch, field.name) for field in fields(batch)}
        return {}

    @classmethod
    def _seed_batch_policy_from_hot_plan(
        cls, ctx: Any, hot_op_plan: Any | None
    ) -> None:
        batch_policy = cls._batch_policy_mapping(hot_op_plan)
        if not batch_policy:
            return
        try:
            setattr(ctx, "batch_policy", batch_policy)
        except Exception:
            pass
        temp = getattr(ctx, "temp", None)
        if isinstance(temp, dict):
            temp["batch_policy"] = batch_policy
            return
        if isinstance(ctx, Mapping):
            existing = ctx.get("temp")
            if isinstance(existing, dict):
                existing["batch_policy"] = batch_policy
                return
            try:
                ctx["temp"] = {"batch_policy": batch_policy}
            except Exception:
                pass

    @classmethod
    def _seed_batch_scheduler(
        cls, ctx: Any, hot_op_plan: Any | None, env: Any | None = None
    ) -> None:
        batch_policy = cls._batch_policy_mapping(hot_op_plan)
        if not bool(batch_policy.get("enabled", False)):
            return
        try:
            from tigrbl_atoms.atoms.batch.scheduler import ResidentBatchScheduler
        except Exception:
            return

        owner = getattr(env, "app", None) if env is not None else None
        scope = getattr(env, "scope", None) if env is not None else None
        if owner is None and isinstance(scope, Mapping):
            owner = scope.get("app")

        scheduler = None
        if owner is not None:
            scheduler = getattr(owner, "_tigrbl_batch_scheduler", None)
            if not isinstance(scheduler, ResidentBatchScheduler):
                scheduler = ResidentBatchScheduler()
                try:
                    setattr(owner, "_tigrbl_batch_scheduler", scheduler)
                except Exception:
                    pass
        if scheduler is None:
            if not isinstance(cls._resident_batch_scheduler, ResidentBatchScheduler):
                cls._resident_batch_scheduler = ResidentBatchScheduler()
            scheduler = cls._resident_batch_scheduler

        try:
            setattr(ctx, "batch_scheduler", scheduler)
        except Exception:
            pass
        temp = getattr(ctx, "temp", None)
        if isinstance(temp, dict):
            temp["batch_scheduler"] = scheduler
            return
        if isinstance(ctx, Mapping):
            existing = ctx.get("temp")
            if isinstance(existing, dict):
                existing["batch_scheduler"] = scheduler
                return
            try:
                ctx["temp"] = {"batch_scheduler": scheduler}
            except Exception:
                pass

    @classmethod
    def _resolve_error_helpers(cls):
        from tigrbl_typing.status import (
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
        return _jsonrpc_error_payload(rpc_code, ERROR_MESSAGES.get(rpc_code, 'Internal error'), rpc_id, data=data)

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

        parent_identity = invocation_identity(ctx.temp.get("identity", {}))
        ctx.temp["identity"] = parent_identity
        for item_index, item in enumerate(batch_payload):
            if not isinstance(item, Mapping):
                responses.append(
                    _jsonrpc_error_payload(-32600, 'Invalid Request', None)
                )
                continue

            rpc_id = item.get("id")
            method = item.get("method")
            if not isinstance(method, str):
                responses.append(
                    _jsonrpc_error_payload(-32601, 'Method not found', rpc_id)
                )
                continue

            if not callable(router_or_app) or not scope:
                responses.append(
                    _jsonrpc_error_payload(-32603, 'Internal error', rpc_id, data={'detail': 'RPC invoker unavailable.'})
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

                child_scope = dict(scope)
                child_state = dict(scope.get("state") or {})
                child_scope["state"] = child_state
                item_identity = {
                    key: value for key, value in parent_identity.items() if key != "attempt_id"
                }
                item_identity["rpc_item_index"] = item_index
                if "id" in item:
                    item_identity["rpc_id"] = rpc_id
                child_state["_tigrbl_rpc_batch_item"] = item_identity
                await router_or_app(child_scope, _receive, _send)
            except Exception as exc:
                responses.append(
                    _jsonrpc_error_payload(-32603, 'Internal error', rpc_id, data={'detail': str(exc)})
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
                decoded = _jsonrpc_error_payload(-32603, 'Internal error', rpc_id, data={'detail': response_body.decode('utf-8', errors='replace')})
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
