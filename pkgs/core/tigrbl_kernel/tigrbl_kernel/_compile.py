from __future__ import annotations

from dataclasses import replace
from types import SimpleNamespace
from typing import Any, Mapping

from tigrbl_atoms import StepFn
from tigrbl_core._spec.binding_spec import (
    HttpJsonRpcProtocolBindingSpec,
    HttpRestBindingSpec,
    HttpRestProtocolBindingSpec,
    WebSocketProtocolBindingSpec,
    WebTransportProtocolBindingSpec,
    derive_websocket_subprotocol_for_framing,
    derive_session_metadata_for_framing,
    framing_spec_name,
)
from tigrbl_core.config.constants import __JSONRPC_DEFAULT_ENDPOINT__
from tigrbl_core._spec.op_spec import OpSpec
from tigrbl_core._spec.well_known_spec import well_known_op_alias

from . import events as _ev
from .models import KernelPlan, OpKey, OpMeta, OpView
from .opview_compiler import compile_opview_from_specs
from .types import DEFAULT_PHASE_ORDER as _DEFAULT_PHASE_ORDER
from .utils import (
    _canonicalize_app,
    _compile_path_pattern,
    _opspecs,
    _phase_info_map,
    _route_payload_template,
    _table_iter,
    deepmerge_phase_chains,
)


DEFAULT_PHASE_ORDER = tuple(getattr(_ev, "PHASES", ())) or _DEFAULT_PHASE_ORDER


def _route_metadata_for_binding(binding: Any) -> dict[str, Any]:
    framing = str(getattr(binding, "framing", "") or "")
    metadata: dict[str, Any] = {
        "framing": framing,
        "framing_kind": framing,
        "framing_spec": framing_spec_name(framing),
    }
    proto = str(getattr(binding, "proto", "") or "")
    if isinstance(binding, WebSocketProtocolBindingSpec):
        derived_subprotocol = derive_websocket_subprotocol_for_framing(framing)
        if derived_subprotocol is not None:
            metadata["websocket_subprotocol"] = derived_subprotocol
    elif proto in {"ws", "wss"}:
        metadata.update(
            derive_session_metadata_for_framing(
                binding_kind=proto,
                framing=framing,
                subprotocols=tuple(getattr(binding, "subprotocols", ()) or ()),
            )
        )
    if isinstance(binding, WebTransportProtocolBindingSpec):
        control = binding.control_stream
        metadata["control_stream"] = {
            "name": control.name,
            "kind": control.kind,
            "opens": control.opens,
            "purpose": control.purpose,
            "framing": control.framing,
        }
        metadata["streams"] = tuple(
            {
                "name": stream.name,
                "kind": stream.kind,
                "purpose": stream.purpose,
                "framing": stream.framing,
            }
            for stream in binding.streams
        )
        metadata["datagrams"] = tuple(
            {
                "name": datagram.name,
                "purpose": datagram.purpose,
                "framing": datagram.framing,
            }
            for datagram in binding.datagrams
        )
    elif proto == "webtransport":
        lane = getattr(binding, "lane", None) or getattr(binding, "profile", None)
        inner_framing = getattr(binding, "inner_framing", None)
        metadata["lane"] = lane
        metadata["inner_framing"] = inner_framing
        if inner_framing is not None:
            metadata["inner_framing_kind"] = str(inner_framing)
            metadata["inner_framing_spec"] = framing_spec_name(inner_framing)
    return metadata


def _pathspec_iter(app: Any) -> tuple[Any, ...]:
    collected: list[Any] = []
    collected.extend(tuple(getattr(app, "_tigrbl_path_specs", ()) or ()))
    routers = getattr(app, "routers", None)
    if isinstance(routers, Mapping):
        router_values = tuple(routers.values())
    elif isinstance(routers, (list, tuple)):
        router_values = tuple(routers)
    else:
        router_values = ()
    for router in router_values:
        collected.extend(tuple(getattr(router, "_tigrbl_path_specs", ()) or ()))

    seen: set[tuple[str, str, str]] = set()
    deduped: list[Any] = []
    for path in collected:
        resource = getattr(path, "well_known", None)
        key = (
            str(getattr(path, "kind", "")),
            str(getattr(path, "path", "")),
            str(getattr(resource, "name", "")),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(path)
    return tuple(deduped)


def _well_known_path_model(app: Any) -> type | None:
    pathspecs = tuple(
        path
        for path in _pathspec_iter(app)
        if getattr(path, "kind", None) == "well-known"
        and getattr(path, "well_known", None) is not None
    )
    if not pathspecs:
        return None

    ops: list[Any] = []
    resources: dict[str, dict[str, Any]] = {}
    for path in pathspecs:
        resource = path.well_known
        alias = well_known_op_alias(resource.name)
        resources[alias] = {
            "name": resource.name,
            "payload": resource.payload,
            "media_type": resource.media_type,
            "status_code": resource.status_code,
            "headers": dict(resource.headers or {}),
        }
        ops.append(
            OpSpec(
                alias=alias,
                target="well_known",
                arity="collection",
                persist="skip",
                expose_routes=False,
                expose_rpc=False,
                bindings=(
                    HttpRestBindingSpec(
                        proto="http.rest",
                        path=str(path.path),
                        methods=("GET",),
                    ),
                ),
                status_code=resource.status_code,
                exchange="request_response",
                tx_scope="none",
            )
        )

    ops_tuple = tuple(ops)
    model = type("TigrblWellKnownPathOps", (), {})
    model.resource_name = "well_known"
    model.__tigrbl_well_known_resources__ = resources
    model.__tigrbl_ops__ = ops_tuple
    model.ops = SimpleNamespace(
        all=ops_tuple,
        by_alias={op.alias: (op,) for op in ops_tuple},
        by_key={(op.alias, op.target): op for op in ops_tuple},
    )
    model.opspecs = model.ops
    setattr(app, "_tigrbl_kernel_well_known_model", model)
    return model


def _compile_models(app: Any) -> tuple[Any, ...]:
    models = list(_table_iter(app))
    well_known_model = _well_known_path_model(app)
    if well_known_model is not None:
        models.append(well_known_model)
    return tuple(models)


def _compile_opview_from_specs(self: Any, specs: Mapping[str, Any], sp: Any) -> OpView:
    return compile_opview_from_specs(specs, sp)


def _compile_plan(self: Any, app: Any) -> KernelPlan:
    app = _canonicalize_app(app)

    from tigrbl_core._spec.binding_spec import (
        HttpJsonRpcBindingSpec,
        HttpRestBindingSpec,
        HttpJsonRpcProtocolBindingSpec,
        HttpRestProtocolBindingSpec,
        HttpStreamBindingSpec,
        SseBindingSpec,
        WebSocketProtocolBindingSpec,
        WebTransportBindingSpec,
        WebTransportProtocolBindingSpec,
        WsBindingSpec,
    )

    route_data: dict[str, Any] = _route_payload_template()
    opmeta: list[OpMeta] = []
    opkey_to_meta: dict[OpKey, int] = {}
    phase_chains: dict[int, Mapping[str, list[StepFn]]] = {}
    opviews: list[OpView | None] = []
    rest_exact_route_to_program: dict[tuple[str, str], int] = {}
    ingress_chain = self._build_ingress(app)
    egress_chain = self._build_egress(app)
    phases, mainline_phases, error_phases = _phase_info_map(DEFAULT_PHASE_ORDER)

    for model in _compile_models(app):
        for sp in _opspecs(model):
            meta_index = len(opmeta)
            target = (getattr(sp, "target", sp.alias) or sp.alias).lower()
            opmeta.append(OpMeta(model=model, alias=sp.alias, target=target))
            try:
                opviews.append(
                    self._compile_opview_from_specs(self.get_specs(model), sp)
                )
            except Exception:
                opviews.append(None)
            phase_chains[meta_index] = deepmerge_phase_chains(
                ingress_chain,
                self._build_op(model, sp.alias),
                egress_chain,
            )

            for binding in getattr(sp, "bindings", ()) or ():
                if isinstance(
                    binding,
                    (
                        HttpRestBindingSpec,
                        HttpRestProtocolBindingSpec,
                        HttpStreamBindingSpec,
                        SseBindingSpec,
                    ),
                ):
                    bucket = route_data.setdefault(
                        binding.proto, {"exact": {}, "templated": []}
                    )
                    for method in binding.methods:
                        selector = f"{method.upper()} {binding.path}"
                        opkey_to_meta[OpKey(proto=binding.proto, selector=selector)] = (
                            meta_index
                        )
                        if "{" in binding.path and "}" in binding.path:
                            pattern, names = _compile_path_pattern(binding.path)
                            bucket["templated"].append(
                                {
                                    "method": method.upper(),
                                    "path": binding.path,
                                    "pattern": pattern,
                                    "names": names,
                                    "meta_index": meta_index,
                                    "selector": selector,
                                }
                            )
                        else:
                            bucket["exact"][selector] = meta_index
                            method, _, path = selector.partition(" ")
                            if path:
                                rest_exact_route_to_program[(method.upper(), path)] = (
                                    meta_index
                                )

                elif isinstance(binding, (HttpJsonRpcBindingSpec, HttpJsonRpcProtocolBindingSpec)):
                    rpc_path = str(
                        getattr(
                            binding,
                            "path",
                            getattr(binding, "endpoint", __JSONRPC_DEFAULT_ENDPOINT__),
                        )
                        or __JSONRPC_DEFAULT_ENDPOINT__
                    )
                    rpc_method = getattr(
                        binding,
                        "method",
                        getattr(binding, "rpc_method", None),
                    )
                    selector = f"{rpc_path}:{rpc_method}"
                    opkey_to_meta[OpKey(proto=binding.proto, selector=selector)] = (
                        meta_index
                    )
                    proto_bucket = route_data.setdefault(
                        binding.proto, {"paths": {}, "endpoints": {}}
                    )
                    path_bucket = proto_bucket.setdefault("paths", {}).setdefault(rpc_path, {})
                    endpoint_bucket = proto_bucket.setdefault("endpoints", {}).setdefault(rpc_path, {})
                    proto_bucket[rpc_method] = meta_index
                    row = {
                        "meta_index": meta_index,
                        "selector": selector,
                        "method": rpc_method,
                        "path": rpc_path,
                    }
                    path_bucket[rpc_method] = row
                    endpoint_bucket[rpc_method] = row

                elif isinstance(
                    binding,
                    (
                        WsBindingSpec,
                        WebSocketProtocolBindingSpec,
                        WebTransportBindingSpec,
                        WebTransportProtocolBindingSpec,
                    ),
                ):
                    bucket = route_data.setdefault(
                        binding.proto, {"exact": {}, "templated": []}
                    )
                    selector = binding.path
                    route_metadata = _route_metadata_for_binding(binding)
                    opkey_to_meta[OpKey(proto=binding.proto, selector=selector)] = (
                        meta_index
                    )

                    if "{" in binding.path and "}" in binding.path:
                        pattern, names = _compile_path_pattern(binding.path)
                        bucket["templated"].append(
                            {
                                "path": binding.path,
                                "pattern": pattern,
                                "names": names,
                                "meta_index": meta_index,
                                "selector": selector,
                                **route_metadata,
                            }
                        )
                    else:
                        bucket["exact"][selector] = meta_index
                        bucket.setdefault("exact_metadata", {})[selector] = {
                            "path": binding.path,
                            "meta_index": meta_index,
                            "selector": selector,
                            **route_metadata,
                        }

    semantic = KernelPlan(
        proto_indices=route_data,
        opmeta=tuple(opmeta),
        opkey_to_meta=opkey_to_meta,
        ingress_chain=ingress_chain,
        phase_chains=phase_chains,
        egress_chain=egress_chain,
        phases=phases,
        mainline_phases=mainline_phases,
        error_phases=error_phases,
    )
    try:
        packed = self._pack_kernel_plan(
            semantic,
            opviews=tuple(opviews),
            rest_exact_route_to_program=rest_exact_route_to_program,
        )
    except TypeError:
        packed = self._pack_kernel_plan(semantic)

    phase_trees = {}
    has_phase_tree_metadata = all(
        hasattr(packed, attr)
        for attr in (
            "program_phase_tree_offsets",
            "program_phase_tree_lengths",
            "phase_tree_nodes",
        )
    )
    if packed is not None and has_phase_tree_metadata:
        for program_id in range(len(opmeta)):
            offset = (
                packed.program_phase_tree_offsets[program_id]
                if program_id < len(packed.program_phase_tree_offsets)
                else 0
            )
            length = (
                packed.program_phase_tree_lengths[program_id]
                if program_id < len(packed.program_phase_tree_lengths)
                else 0
            )
            phase_trees[program_id] = tuple(
                packed.phase_tree_nodes[offset : offset + length]
            )
    return replace(semantic, packed=packed, phase_trees=phase_trees)
