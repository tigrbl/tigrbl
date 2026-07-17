from __future__ import annotations

from typing import Any

from tigrbl.engine.registry import register_engine

from .engine import ROMEngine
from .session import ROMSession


def capabilities(*, spec: Any = None, mapping: Any = None) -> dict[str, Any]:
    return {
        "engine": "rom",
        "transactional": False,
        "async_native": True,
        "isolation_levels": set(),
        "read_only_enforced": True,
        "persistence": "process",
        "storage": "immutable-memory",
        "read_consistency": "immutable-snapshot",
        "binding_scopes": {"table"},
    }


def build_rom(*, mapping=None, spec=None, dsn=None, **_: Any) -> tuple[object, object]:
    if dsn:
        raise ValueError("ROM engine accepts embedded mapping data, not a DSN")
    config = dict(mapping or {})
    engine = ROMEngine(
        rows=config.get("rows"),
        primary_key=str(config.get("primary_key", "id")),
        namespace=str(config.get("namespace", "default")),
        spec=spec,
    )

    def sessionmaker(session_spec=None) -> ROMSession:
        return ROMSession(engine, spec=session_spec)

    return engine, sessionmaker


class _Registration:
    def build(self, *, mapping, spec, dsn):
        return build_rom(mapping=mapping, spec=spec, dsn=dsn)

    def capabilities(self, *, spec, mapping=None):
        return capabilities(spec=spec, mapping=mapping)


def register() -> None:
    register_engine("rom", _Registration())


__all__ = ["build_rom", "capabilities", "register"]
