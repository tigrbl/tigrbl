from tigrbl_canon import _warn_deprecated_import

_warn_deprecated_import(__name__)

from tigrbl_core._spec.op_spec import resolve

__all__ = ["resolve"]
