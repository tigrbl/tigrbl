from __future__ import annotations

from tigrbl_kernel.atoms import _wrap_atom
from tigrbl_atoms.atoms.sys.handler_create import ANCHOR, INSTANCE, _run


def test_wrap_atom_prefers_module_run_for_direct_execution_metadata() -> None:
    step = _wrap_atom(INSTANCE, anchor=ANCHOR)

    assert getattr(step, "__tigrbl_direct_run") is _run
    assert getattr(step, "__tigrbl_use_two_args") is True
