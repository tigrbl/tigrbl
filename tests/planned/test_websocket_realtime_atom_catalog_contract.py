import pytest


pytestmark = pytest.mark.xfail(
    reason="planned WebSocket realtime atom catalog contract; implementation scope not frozen",
    strict=False,
)


def test_websocket_realtime_required_atoms_contract() -> None:
    assert False


def test_websocket_realtime_atom_phase_placement_contract() -> None:
    assert False
