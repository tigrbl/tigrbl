from __future__ import annotations

import pytest

from tigrbl_atoms.fallback import rust_atoms_enabled
from tigrbl_atoms.rust import (
    register_rust_atom,
    register_rust_hook,
)


def test_rust_atom_and_hook_registrars_are_deprecated() -> None:
    with pytest.warns(DeprecationWarning):
        assert rust_atoms_enabled() is False

    with pytest.warns(DeprecationWarning):
        with pytest.raises(RuntimeError, match="Python-only"):
            register_rust_atom("demo.atom", lambda ctx: ctx)
    with pytest.warns(DeprecationWarning):
        with pytest.raises(RuntimeError, match="Python-only"):
            register_rust_hook("demo.hook", lambda ctx: ctx)
