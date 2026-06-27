from __future__ import annotations

from ._shared import *
from .batch import _PackedBatchMixin
from .hot_access import _PackedHotAccessMixin
from .input_extract import _PackedInputExtractMixin
from .input_compile import _PackedInputCompileMixin
from .hot_context import _PackedHotContextMixin
from .request_select import _PackedRequestSelectMixin
from .route_select import _PackedRouteSelectMixin
from .segments import _PackedSegmentsMixin
from .runner_resolve import _PackedRunnerResolveMixin
from .error_edges import _PackedErrorEdgesMixin
from .execute import _PackedExecuteMixin


class PackedPlanExecutor(
    _PackedBatchMixin,
    _PackedHotAccessMixin,
    _PackedInputExtractMixin,
    _PackedInputCompileMixin,
    _PackedHotContextMixin,
    _PackedRequestSelectMixin,
    _PackedRouteSelectMixin,
    _PackedSegmentsMixin,
    _PackedRunnerResolveMixin,
    _PackedErrorEdgesMixin,
    _PackedExecuteMixin,
    ExecutorBase,
):
    """Executes packed kernel plans via kernel-attached packed execution hooks."""

    name: ClassVar[str] = "packed"
    _resident_batch_scheduler: ClassVar[Any | None] = None
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

__all__ = ["PackedPlanExecutor"]
