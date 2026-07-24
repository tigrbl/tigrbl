from __future__ import annotations

import inspect
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from tigrbl import TigrblApp
from tigrbl.factories.app import deriveApp

from catalog import TigrblMcpTool, build_tool_catalog


ToolFactory = Callable[[TigrblApp], Callable[..., Any]]
SurfaceProvider = Callable[[FastMCP, TigrblApp], None]


@dataclass(frozen=True, slots=True)
class TigrblMCPDefinition:
    name: str
    instructions: str
    tables: tuple[type, ...]
    tools: Mapping[str, ToolFactory]
    surfaces: tuple[SurfaceProvider, ...]
    version: str
    stateless_http: bool
    json_response: bool


@dataclass(frozen=True, slots=True)
class TigrblMCP:
    definition: TigrblMCPDefinition
    tigrbl: TigrblApp
    mcp: FastMCP
    catalog: tuple[TigrblMcpTool, ...]

    @classmethod
    def define(
        cls,
        *,
        name: str,
        instructions: str,
        tables: Sequence[type],
        tools: Mapping[str, ToolFactory],
        surfaces: Sequence[SurfaceProvider] = (),
        version: str = "0.1.0",
        stateless_http: bool = True,
        json_response: bool = True,
    ) -> TigrblMCPDefinition:
        """Define an immutable MCP projection without creating runtime state."""
        normalized_tools = dict(tools)
        if not name.strip():
            raise ValueError("TigrblMCP name must not be empty")
        if not tables:
            raise ValueError("TigrblMCP requires at least one table")
        if not normalized_tools:
            raise ValueError("TigrblMCP requires at least one tool provider")
        return TigrblMCPDefinition(
            name=name,
            instructions=instructions,
            tables=tuple(tables),
            tools=normalized_tools,
            surfaces=tuple(surfaces),
            version=version,
            stateless_http=stateless_http,
            json_response=json_response,
        )

    @classmethod
    async def make(
        cls,
        definition: TigrblMCPDefinition,
        *,
        engine: Any,
        mount_system: bool = False,
    ) -> TigrblMCP:
        """Make an initialized Tigrbl app and derive its MCP projection."""
        App = deriveApp(
            title=definition.name,
            version=definition.version,
            engine=engine,
            tables=definition.tables,
        )
        app = App(mount_system=mount_system)
        initialized = app.initialize()
        if inspect.isawaitable(initialized):
            await initialized
        return cls.derive(definition, app)

    @classmethod
    def derive(
        cls,
        definition: TigrblMCPDefinition,
        app: TigrblApp,
    ) -> TigrblMCP:
        """Derive an MCP server from an already materialized Tigrbl app."""
        catalog = build_tool_catalog(app)
        catalog_by_name = {tool.name: tool for tool in catalog}
        declared_names = set(definition.tools)
        projected_names = set(catalog_by_name)
        if declared_names != projected_names:
            raise ValueError(
                "TigrblMCP tool providers must exactly match the exposed "
                f"OpSpec catalog; declared={sorted(declared_names)}, "
                f"projected={sorted(projected_names)}"
            )

        mcp = FastMCP(
            definition.name,
            instructions=definition.instructions,
            stateless_http=definition.stateless_http,
            json_response=definition.json_response,
        )
        service = cls(
            definition=definition,
            tigrbl=app,
            mcp=mcp,
            catalog=catalog,
        )
        service._provide_tools(catalog_by_name)
        for surface in definition.surfaces:
            surface(mcp, app)
        return service

    def provide(self) -> FastMCP:
        """Provide the configured official-SDK MCP protocol server."""
        return self.mcp

    def asgi_app(self, transport: str) -> Any | None:
        """Provide an ASGI app only for an HTTP-based MCP transport.

        Stdio is a process-stream transport, so no ASGI server creates a scope.
        Streamable HTTP receives ordinary ASGI ``http`` scopes at ``/mcp``.
        """
        if transport == "stdio":
            return None
        if transport == "streamable-http":
            return self.mcp.streamable_http_app()
        raise ValueError(f"unsupported MCP transport: {transport!r}")

    @staticmethod
    def _annotations(tool: TigrblMcpTool) -> ToolAnnotations:
        return ToolAnnotations(
            title=tool.title,
            readOnlyHint=tool.read_only,
            destructiveHint=tool.destructive,
            idempotentHint=tool.idempotent,
            openWorldHint=tool.open_world,
        )

    @classmethod
    def _tool_kwargs(cls, tool: TigrblMcpTool) -> dict[str, Any]:
        return {
            "name": tool.name,
            "title": tool.title,
            "description": tool.description,
            "annotations": cls._annotations(tool),
            "meta": {"com.tigrbl/op": tool.tigrbl_identity},
            "structured_output": True,
        }

    def _provide_tools(
        self,
        catalog_by_name: Mapping[str, TigrblMcpTool],
    ) -> None:
        for name, factory in self.definition.tools.items():
            tool = catalog_by_name[name]
            handler = factory(self.tigrbl)
            if not callable(handler):
                raise TypeError(f"tool provider {name!r} did not return a callable")
            self.mcp.add_tool(handler, **self._tool_kwargs(tool))
