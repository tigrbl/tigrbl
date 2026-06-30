from __future__ import annotations

from types import SimpleNamespace

from tigrbl_kernel import Kernel


class FakeModel:
    hooks = SimpleNamespace(create=SimpleNamespace())
    ops = SimpleNamespace(
        by_alias={
            "create": [
                SimpleNamespace(
                    alias="create",
                    target="create",
                    persist="default",
                    secdeps=(),
                    deps=(),
                )
            ]
        }
    )


class WebTransportControlModel:
    hooks = SimpleNamespace(open_bidi_stream=SimpleNamespace())
    ops = SimpleNamespace(
        by_alias={
            "open_bidi_stream": [
                SimpleNamespace(
                    alias="open_bidi_stream",
                    target="open_bidi_stream",
                    persist="default",
                    secdeps=(),
                    deps=(),
                )
            ]
        }
    )


def test_build_op_prepends_phase_db_binding_to_each_phase() -> None:
    chains = Kernel()._build_op(FakeModel, "create")

    required = (
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

    for phase in required:
        steps = chains.get(phase, ())
        assert steps, f"{phase} missing phase-db binder"
        assert (
            getattr(steps[0], "__tigrbl_label", "")
            == "atom:sys:phase_db@SYS_PHASE_DB_BIND"
        )


def test_repeated_build_does_not_duplicate_phase_db_binding() -> None:
    kernel = Kernel()
    chains = kernel._build_op(FakeModel, "create")
    for phase, steps in chains.items():
        labels = [getattr(step, "__tigrbl_label", "") for step in steps]
        assert labels.count("atom:sys:phase_db@SYS_PHASE_DB_BIND") == 1, phase


def test_ingress_and_egress_chains_prepend_phase_db_binding() -> None:
    kernel = Kernel()
    ingress = kernel._build_ingress(app=None)
    egress = kernel._build_egress(app=None)

    for chains in (ingress, egress):
        for phase, steps in chains.items():
            assert steps, phase
            assert (
                getattr(steps[0], "__tigrbl_label", "")
                == "atom:sys:phase_db@SYS_PHASE_DB_BIND"
            )


def test_webtransport_control_op_selects_control_plane_handler_atom() -> None:
    chains = Kernel()._build_op(WebTransportControlModel, "open_bidi_stream")
    labels = [getattr(step, "__tigrbl_label", "") for step in chains["HANDLER"]]

    assert "atom:sys:handler_open_bidi_stream@sys.handler.persistence" in labels
    assert "atom:sys:handler_create@sys.handler.persistence" not in labels
