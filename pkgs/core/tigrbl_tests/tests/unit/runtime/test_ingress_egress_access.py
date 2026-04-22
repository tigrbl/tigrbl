import pytest

from tigrbl.decorators.hook import hook_ctx
from tigrbl.hook.exceptions import InvalidHookPhaseError
from tigrbl_kernel.atoms import _inject_atoms


_ATOM_ONLY_ANCHORS = (
    "INGRESS_BEGIN",
    "INGRESS_PARSE",
    "INGRESS_DISPATCH",
    "EGRESS_SHAPE",
    "EGRESS_FINALIZE",
)


def _mk_atom(module: str, label: str):
    def run(obj, ctx):
        return None

    run.__module__ = module
    run.__tigrbl_label = label
    return run


@pytest.mark.parametrize("anchor", _ATOM_ONLY_ANCHORS)
def test_atom_injection_accepts_ingress_and_egress_anchors(anchor: str) -> None:
    chains = {}
    atoms = [
        (
            anchor,
            _mk_atom(
                "tigrbl.runtime.atoms.response.custom",
                f"atom:response:custom@{anchor}",
            ),
        )
    ]

    _inject_atoms(chains, atoms, persistent=True)

    assert anchor in chains
    assert len(chains[anchor]) == 1


@pytest.mark.parametrize("anchor", _ATOM_ONLY_ANCHORS)
def test_hook_ctx_rejects_ingress_and_egress_hook_anchors(anchor: str) -> None:
    with pytest.raises(InvalidHookPhaseError):

        class Model:
            @hook_ctx(ops="create", phase=anchor)
            def bad_anchor_hook(cls, ctx):
                return None
