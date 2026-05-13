import pytest

from tigrbl_core._spec.path_spec import PathSpec


def test_pathspec_engine_rejection_contract() -> None:
    with pytest.raises(ValueError, match="PathSpec does not own engines"):
        PathSpec.from_dict({"path": "/items", "kind": "resource", "engine_name": "primary"})
