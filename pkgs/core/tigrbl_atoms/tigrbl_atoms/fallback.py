from __future__ import annotations

import warnings


def rust_atoms_enabled() -> bool:
    warnings.warn(
        "tigrbl_atoms Rust registration is deprecated; atoms are Python-only.",
        DeprecationWarning,
        stacklevel=2,
    )
    return False
