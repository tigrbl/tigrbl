"""Security compatibility namespace."""

from .dependencies import Dependency, Depends, Security
from .._concrete._security import APIKey, HTTPBasic, HTTPBearer, MutualTLS, OAuth2, OpenIdConnect

__all__ = [
    "Depends",
    "Security",
    "Dependency",
    "APIKey",
    "HTTPBasic",
    "HTTPBearer",
    "OAuth2",
    "OpenIdConnect",
    "MutualTLS",
]
