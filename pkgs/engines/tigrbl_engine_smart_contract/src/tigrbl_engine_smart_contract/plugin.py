from __future__ import annotations

from tigrbl.engine.registry import register_engine

from .engine import smart_contract_capabilities, smart_contract_engine


def register() -> None:
    register_engine(
        kind="smart_contract",
        build=smart_contract_engine,
        capabilities=smart_contract_capabilities,
    )
