from .app import defineAppSpec, deriveApp
from .table import defineTableSpec, deriveTable, deriveTableSpec
from .webhook import DefineWebhook

__all__ = [
    "DefineWebhook",
    "defineAppSpec",
    "defineTableSpec",
    "deriveApp",
    "deriveTable",
    "deriveTableSpec",
]
