from tigrbl_canon import _warn_deprecated_import

_warn_deprecated_import(__name__)

from .core import infer
from .types import (
    Email,
    Phone,
    DataKind,
    PyTypeInfo,
    SATypePlan,
    JsonHint,
    Inferred,
    InferenceError,
    UnsupportedType,
)

__all__ = [
    "infer",
    "Email",
    "Phone",
    "DataKind",
    "PyTypeInfo",
    "SATypePlan",
    "JsonHint",
    "Inferred",
    "InferenceError",
    "UnsupportedType",
]
