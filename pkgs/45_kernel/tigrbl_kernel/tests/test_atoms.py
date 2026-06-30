from __future__ import annotations

from tigrbl_kernel.atoms import _wrap_atom
from tigrbl_atoms.atoms.ingress.transport_extract import (
    ANCHOR as TRANSPORT_ANCHOR,
    INSTANCE as TRANSPORT_INSTANCE,
)
from tigrbl_atoms.atoms.sys.handler_create import ANCHOR, INSTANCE, _run


def test_wrap_atom_prefers_module_run_for_direct_execution_metadata() -> None:
    step = _wrap_atom(INSTANCE, anchor=ANCHOR)

    assert getattr(step, "__tigrbl_direct_run") is _run
    assert getattr(step, "__tigrbl_use_two_args") is True


def test_wrap_atom_marks_compiled_param_skip_policy_for_transport_extract() -> None:
    step = _wrap_atom(TRANSPORT_INSTANCE, anchor=TRANSPORT_ANCHOR)

    assert getattr(step, "__tigrbl_atom_name__") == "ingress.transport_extract"
    assert getattr(step, "__tigrbl_skip_in_compiled_param") is True
    assert getattr(step, "__tigrbl_requires_phase_db") is False
