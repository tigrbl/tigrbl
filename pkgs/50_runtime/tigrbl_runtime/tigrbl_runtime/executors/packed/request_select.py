from __future__ import annotations

from ._shared import *


class _PackedRequestSelectMixin:
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
