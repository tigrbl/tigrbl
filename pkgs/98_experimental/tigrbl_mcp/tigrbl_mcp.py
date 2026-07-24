from __future__ import annotations

import inspect
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from mcp import types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from pydantic import BaseModel
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.types import Receive, Scope, Send
from tigrbl import TigrblApp
from tigrbl.factories.app import deriveApp

from catalog import TigrblMcpTool, build_tool_catalog


ToolFactory = Callable[[TigrblApp], Callable[..., Any]]
SurfaceProvider = Callable[[Server[Any, Any], TigrblApp], None]


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


class _StreamableHTTPApp:
    def __init__(self, manager: StreamableHTTPSessionManager) -> None:
        self.manager = manager

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self.manager.handle_request(scope, receive, send)


@dataclass(frozen=True, slots=True)
class TigrblMCP:
    definition: TigrblMCPDefinition
    tigrbl: TigrblApp
    mcp: Server[Any, Any]
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
        """Define immutable Tigrbl-to-MCP configuration without runtime state."""
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
        """Make an initialized Tigrbl app, then derive its MCP service."""
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
        """Derive a low-level MCP SDK server from an initialized Tigrbl app."""
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

        mcp: Server[Any, Any] = Server(
            definition.name,
            version=definition.version,
            instructions=definition.instructions,
        )
        service = cls(
            definition=definition,
            tigrbl=app,
            mcp=mcp,
            catalog=catalog,
        )
        service._register_tool_handlers(catalog_by_name)
        for surface in definition.surfaces:
            surface(mcp, app)
        return service

    def provide(self) -> Server[Any, Any]:
        """Provide the derived low-level SDK server; this is not a constructor."""
        return self.mcp

    async def run_stdio(self) -> None:
        """Run the low-level SDK server over MCP's stdio transport."""
        async with stdio_server() as (read_stream, write_stream):
            await self.mcp.run(
                read_stream,
                write_stream,
                self.mcp.create_initialization_options(),
                stateless=self.definition.stateless_http,
            )

    def asgi_app(self, transport: str) -> Starlette | None:
        """Provide ASGI only for Streamable HTTP; stdio has no ASGI scope."""
        if transport == "stdio":
            return None
        if transport != "streamable-http":
            raise ValueError(f"unsupported MCP transport: {transport!r}")

        manager = StreamableHTTPSessionManager(
            app=self.mcp,
            json_response=self.definition.json_response,
            stateless=self.definition.stateless_http,
        )
        return Starlette(
            routes=[Route("/mcp", endpoint=_StreamableHTTPApp(manager))],
            lifespan=lambda _: manager.run(),
        )

    @staticmethod
    def _annotations(tool: TigrblMcpTool) -> types.ToolAnnotations:
        return types.ToolAnnotations(
            title=tool.title,
            readOnlyHint=tool.read_only,
            destructiveHint=tool.destructive,
            idempotentHint=tool.idempotent,
            openWorldHint=tool.open_world,
        )

    @staticmethod
    def _mcp_output_schema(schema: dict[str, Any]) -> dict[str, Any]:
        if schema.get("type") == "object":
            return schema
        result_schema = dict(schema)
        definitions = result_schema.pop("$defs", None)
        wrapped = {
            "type": "object",
            "properties": {"result": result_schema},
            "required": ["result"],
            "additionalProperties": False,
        }
        if definitions is not None:
            wrapped["$defs"] = definitions
        return wrapped

    @staticmethod
    def _json_value(value: Any) -> Any:
        if isinstance(value, BaseModel):
            return value.model_dump(mode="json")
        if isinstance(value, list):
            return [TigrblMCP._json_value(item) for item in value]
        if isinstance(value, tuple):
            return [TigrblMCP._json_value(item) for item in value]
        if isinstance(value, dict):
            return {key: TigrblMCP._json_value(item) for key, item in value.items()}
        return value

    def _register_tool_handlers(
        self,
        catalog_by_name: Mapping[str, TigrblMcpTool],
    ) -> None:
        sdk_tools = {
            name: types.Tool(
                name=tool.name,
                title=tool.title,
                description=tool.description,
                inputSchema=tool.input_schema,
                outputSchema=self._mcp_output_schema(tool.output_schema),
                annotations=self._annotations(tool),
                meta={"com.tigrbl/op": tool.tigrbl_identity},
            )
            for name, tool in catalog_by_name.items()
        }
        handlers = {
            name: factory(self.tigrbl)
            for name, factory in self.definition.tools.items()
        }
        for name, handler in handlers.items():
            if not callable(handler):
                raise TypeError(f"tool provider {name!r} did not return a callable")

        @self.mcp.list_tools()
        async def list_tools() -> list[types.Tool]:
            return [sdk_tools[name] for name in self.definition.tools]

        @self.mcp.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
            if name not in handlers:
                raise ValueError(f"unknown MCP tool: {name}")
            result = handlers[name](**arguments)
            if inspect.isawaitable(result):
                result = await result
            serialized = self._json_value(result)
            if isinstance(serialized, dict):
                return serialized
            return {"result": serialized}
