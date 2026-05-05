import pytest

from tigrbl_base._base._session_abc import SessionABC


def test_session_abc_is_abstract() -> None:
    with pytest.raises(TypeError):
        SessionABC()


def test_session_abc_declares_batch_execution_methods() -> None:
    assert "executeloop" in SessionABC.__abstractmethods__
    assert "executemany" in SessionABC.__abstractmethods__
