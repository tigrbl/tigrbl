from tigrbl_canon import _warn_deprecated_import

_warn_deprecated_import(__name__)

"""Compatibility shim for relocated column MRO collector."""

from tigrbl_core._spec.column_spec import *  # noqa: F403
