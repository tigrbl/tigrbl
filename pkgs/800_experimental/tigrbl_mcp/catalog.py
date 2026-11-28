from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from tigrbl import TigrblApp


JsonSchema = dict[str, Any]


@dataclass(frozen=True, slots=True)
class TigrblMcpTool:
    name: str
    title: str
    description: str
    table_name: str
    op_alias: str
    input_schema: JsonSchema
    output_schema: JsonSchema
    read_only: bool
    destructive: bool
    idempotent: bool
    open_world: bool

    @property
    def tigrbl_identity(self) -> str:
        return f"{self.table_name}.{self.op_alias}"


def _model_json_schema(model: Any) -> JsonSchema:
    if model is None:
        return {"type": "object", "properties": {}}
    exporter = getattr(model, "model_json_schema", None)
    if not callable(exporter):
        raise TypeError(f"{model!r} does not expose model_json_schema()")
    return dict(exporter())


def _policy(op: Any) -> Mapping[str, Any] | None:
    extra = getattr(op, "extra", None)
    if not isinstance(extra, Mapping):
        return None
    policy = extra.get("mcp")
    if not isinstance(policy, Mapping) or policy.get("expose") is not True:
        return None
    return policy


def build_tool_catalog(app: TigrblApp) -> tuple[TigrblMcpTool, ...]:
    projected: list[TigrblMcpTool] = []
    seen_names: set[str] = set()

    for table_name, table in sorted(app.tables.items()):
        for op in sorted(tuple(table.ops.all), key=lambda item: item.alias):
            policy = _policy(op)
            if policy is None:
                continue

            name = str(policy.get("name") or f"{table_name}_{op.alias}").lower()
            if name in seen_names:
                raise ValueError(f"duplicate MCP tool name: {name}")
            seen_names.add(name)

            schema_ns = getattr(getattr(table, "schemas", None), op.alias, None)
            projected.append(
                TigrblMcpTool(
                    name=name,
                    title=str(policy.get("title") or name.replace("_", " ").title()),
                    description=str(policy.get("description") or ""),
                    table_name=table_name,
                    op_alias=op.alias,
                    input_schema=_model_json_schema(getattr(schema_ns, "in_", None)),
                    output_schema=_model_json_schema(getattr(schema_ns, "out", None)),
                    read_only=bool(policy.get("read_only", False)),
                    destructive=bool(policy.get("destructive", False)),
                    idempotent=bool(policy.get("idempotent", False)),
                    open_world=bool(policy.get("open_world", True)),
                )
            )

    return tuple(sorted(projected, key=lambda item: item.name))


def catalog_by_name(app: TigrblApp) -> dict[str, TigrblMcpTool]:
    return {tool.name: tool for tool in build_tool_catalog(app)}
