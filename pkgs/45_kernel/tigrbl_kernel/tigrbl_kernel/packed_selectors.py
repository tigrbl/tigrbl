from __future__ import annotations

from collections.abc import Mapping, MutableMapping

from .models import KernelPlan, PackedKernel
from .packed_access import (
    hot_array,
    hot_section,
    http_method_id,
    stable_name_hash64,
)

ExactRouteCache = MutableMapping[int, Mapping[int, tuple[int, int]]]
ExactRouteVerifyCache = MutableMapping[
    int, Mapping[int, Mapping[int, tuple[tuple[str, int], ...]]]
]
ExactWebSocketCache = MutableMapping[int, Mapping[tuple[str, str], int]]
ExactJsonRpcCache = MutableMapping[int, Mapping[str, Mapping[str, tuple[int, str, str]]]]


def resolve_hot_exact_route_slices(
    packed: PackedKernel,
    cache: ExactRouteCache,
) -> Mapping[int, tuple[int, int]]:
    packed_id = id(packed)
    cached = cache.get(packed_id)
    if cached is not None:
        return cached
    method_ids = hot_section(packed, "exact_method_ids")
    path_hashes = hot_section(packed, "exact_path_hashes")
    program_ids = hot_section(packed, "exact_program_ids")
    if method_ids is None or path_hashes is None or program_ids is None:
        cache[packed_id] = {}
        return {}
    if not (
        int(method_ids.count) == int(path_hashes.count) == int(program_ids.count)
    ):
        cache[packed_id] = {}
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
    frozen = {
        int(method_id): (int(start), int(count))
        for method_id, (start, count) in directory.items()
    }
    cache[packed_id] = frozen
    return frozen


def resolve_hot_exact_route_verify(
    packed: PackedKernel,
    cache: ExactRouteVerifyCache,
) -> Mapping[int, Mapping[int, tuple[tuple[str, int], ...]]]:
    packed_id = id(packed)
    cached = cache.get(packed_id)
    if cached is not None:
        return cached

    route = getattr(packed, "rest_exact_route_to_program", None)
    if not isinstance(route, Mapping):
        cache[packed_id] = {}
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
        method_id = http_method_id(method_name)
        path_hash = stable_name_hash64(exact_path)
        method_bucket = verify.setdefault(method_id, {})
        method_bucket.setdefault(path_hash, []).append((exact_path, program_id))

    frozen = {
        int(method_id): {
            int(path_hash): tuple(entries)
            for path_hash, entries in method_bucket.items()
        }
        for method_id, method_bucket in verify.items()
    }
    cache[packed_id] = frozen
    return frozen


def resolve_program_id_from_exact_route(
    packed: PackedKernel,
    method: str,
    path: str,
    route_cache: ExactRouteCache,
    verify_cache: ExactRouteVerifyCache,
) -> int:
    method_id = http_method_id(method)
    path_hash = stable_name_hash64(path)
    path_hashes = hot_section(packed, "exact_path_hashes")
    program_ids = hot_section(packed, "exact_program_ids")
    method_slices = resolve_hot_exact_route_slices(packed, route_cache)
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
            verify = resolve_hot_exact_route_verify(packed, verify_cache)
            method_verify = verify.get(method_id, {})
            candidates = method_verify.get(path_hash, ())
            if candidates:
                for candidate_path, candidate_program_id in candidates:
                    if candidate_path == path:
                        return int(candidate_program_id)
                return -1
            return program_id
    method_ids = hot_array(packed, "exact_method_ids", tuple())
    path_hash_array = hot_array(packed, "exact_path_hashes", tuple())
    program_id_array = hot_array(packed, "exact_program_ids", tuple())
    for candidate_method_id, candidate_hash, program_id in zip(
        method_ids, path_hash_array, program_id_array
    ):
        if int(candidate_method_id) == int(method_id) and int(candidate_hash) == int(
            path_hash
        ):
            return int(program_id)
    route = getattr(packed, "rest_exact_route_to_program", None)
    if not isinstance(route, Mapping):
        return -1
    maybe = route.get((method.upper(), path))
    return maybe if isinstance(maybe, int) else -1


def resolve_hot_exact_websocket_routes(
    plan: KernelPlan,
    packed: PackedKernel,
    cache: ExactWebSocketCache,
) -> Mapping[tuple[str, str], int]:
    packed_id = id(packed)
    cached = cache.get(packed_id)
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
    cache[packed_id] = exact
    return exact


def resolve_program_id_from_exact_websocket(
    plan: KernelPlan,
    packed: PackedKernel,
    protocol: str,
    path: str,
    cache: ExactWebSocketCache,
) -> int:
    exact = resolve_hot_exact_websocket_routes(plan, packed, cache)
    maybe = exact.get((protocol, path))
    return maybe if isinstance(maybe, int) else -1


def resolve_hot_exact_jsonrpc_routes(
    plan: KernelPlan,
    cache: ExactJsonRpcCache,
) -> Mapping[str, Mapping[str, tuple[int, str, str]]]:
    plan_id = id(plan)
    cached = cache.get(plan_id)
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
                    selector = str(entry.get("selector") or f"{endpoint}:{rpc_method}")
                    method_map[rpc_method] = (meta_index, str(proto), selector)

    frozen = {endpoint: dict(method_map) for endpoint, method_map in exact_routes.items()}
    cache[plan_id] = frozen
    return frozen


def normalize_jsonrpc_mount_path(path: str) -> str:
    normalized = str(path or "").rstrip("/")
    return normalized or "/"
