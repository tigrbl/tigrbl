from __future__ import annotations

from ._shared import *


class _PackedWebSocketRouteSelectMixin:
    def _resolve_hot_exact_websocket_routes(
        self,
        plan: KernelPlan,
        packed: PackedKernel,
    ) -> Mapping[tuple[str, str], int]:
        return _kernel_resolve_hot_exact_websocket_routes(
            plan,
            packed,
            self._hot_exact_websocket_route_cache,
        )


    def _resolve_program_id_from_exact_websocket(
        self,
        plan: KernelPlan,
        packed: PackedKernel,
        protocol: str,
        path: str,
    ) -> int:
        return _kernel_resolve_program_id_from_exact_websocket(
            plan,
            packed,
            protocol,
            path,
            self._hot_exact_websocket_route_cache,
        )


