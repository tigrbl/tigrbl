from tigrbl.runtime import events as _ev
from tigrbl_kernel import events as _kernel_events


def test_order_events_returns_canonical_runtime_sequence() -> None:
    anchors = [_ev.OUT_DUMP, _ev.DEP_SECURITY, _ev.OUT_BUILD]

    assert _ev.order_events(anchors) == [_ev.DEP_SECURITY, _ev.OUT_BUILD, _ev.OUT_DUMP]


def test_prune_events_for_persist_keeps_non_persist_tied_only() -> None:
    anchors = [_ev.RESOLVE_VALUES, _ev.SCHEMA_COLLECT_IN, _ev.OUT_DUMP]

    assert _ev.prune_events_for_persist(anchors, persist=False) == [
        _ev.SCHEMA_COLLECT_IN,
        _ev.OUT_DUMP,
    ]


def test_stages_follow_expected_kernel_execution_order() -> None:
    assert _ev.PHASES == _kernel_events.PHASES
    assert _ev.PHASES[:3] == (
        "INGRESS_BEGIN",
        "INGRESS_PARSE",
        "INGRESS_DISPATCH",
    )
