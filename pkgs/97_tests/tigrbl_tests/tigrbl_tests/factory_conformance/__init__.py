"""Factory surface inventory and conformance assertions."""

from .aliases import assert_alias_parity
from .discovery import FactoryCandidate, discover_factory_candidates
from .manifest import FactoryAlias, FactoryManifest, FactorySurface, load_manifest
from .ownership import assert_owner
from .resolution import resolve_symbol
from .semantics import assert_surface_shape

__all__ = [
    "FactoryAlias",
    "FactoryCandidate",
    "FactoryManifest",
    "FactorySurface",
    "assert_alias_parity",
    "assert_owner",
    "assert_surface_shape",
    "discover_factory_candidates",
    "load_manifest",
    "resolve_symbol",
]
