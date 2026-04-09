from __future__ import annotations

from dataclasses import dataclass

from tigrbl_core._spec import DataTypeSpec, EngineDatatypeBridge, EngineRegistry, StorageTypeRef


@dataclass
class SQLiteStringLowerer:
    engine_kind: str = "sqlite"

    def lower(self, datatype: DataTypeSpec) -> StorageTypeRef:
        if datatype.logical_name == "string":
            return StorageTypeRef(engine_kind="sqlite", physical_name="TEXT")
        return StorageTypeRef(engine_kind="sqlite", physical_name=datatype.logical_name.upper())


def test_engine_bridge_lowering_uses_registered_lowerer() -> None:
    registry = EngineRegistry()
    registry.register(SQLiteStringLowerer())
    bridge = EngineDatatypeBridge(registry)

    lowered = bridge.lower("sqlite", DataTypeSpec(logical_name="string"))
    assert lowered.physical_name == "TEXT"
