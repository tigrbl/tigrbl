from __future__ import annotations

import inspect
import json
import sys
from pathlib import Path

import httpx
import pytest
from mcp import ClientSession, StdioServerParameters, types
from mcp.server.lowlevel import Server
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamable_http_client
from mcp.shared.memory import create_connected_server_and_client_session
from pydantic import AnyUrl


EXAMPLE_DIR = Path(__file__).resolve().parents[1]
if str(EXAMPLE_DIR) not in sys.path:
    sys.path.insert(0, str(EXAMPLE_DIR))

import app as app_module  # noqa: E402
import server as server_module  # noqa: E402
from app import NOTE_MCP  # noqa: E402
from server import parse_args  # noqa: E402
from tigrbl.factories.app import deriveApp  # noqa: E402
from tigrbl.factories.engine import mem  # noqa: E402
from tigrbl_mcp import TigrblMCP, TigrblMCPDefinition  # noqa: E402


@pytest.mark.asyncio
async def test_catalog_projects_only_explicit_tigrbl_mcp_operations() -> None:
    assert isinstance(NOTE_MCP, TigrblMCPDefinition)
    service = await TigrblMCP.make(NOTE_MCP, engine=mem(async_=False))
    catalog = service.catalog

    assert [tool.name for tool in catalog] == [
        "create_note",
        "list_notes",
        "read_note",
    ]
    by_name = {tool.name: tool for tool in catalog}
    assert by_name["create_note"].tigrbl_identity == "Note.create"
    assert by_name["create_note"].input_schema["required"] == ["title", "body"]
    assert by_name["read_note"].input_schema["required"] == ["id"]
    assert by_name["list_notes"].input_schema["additionalProperties"] is False
    assert by_name["list_notes"].output_schema["type"] == "array"
    assert by_name["read_note"].read_only is True
    assert by_name["create_note"].read_only is False


def test_lowlevel_sdk_handlers_cover_declared_mcp_capabilities() -> None:
    service = TigrblMCP.derive(NOTE_MCP, _initialized_app_for_sync_test())
    handlers = service.provide().request_handlers

    assert isinstance(service.provide(), Server)
    assert {
        types.ListToolsRequest,
        types.CallToolRequest,
        types.ListResourcesRequest,
        types.ListResourceTemplatesRequest,
        types.ReadResourceRequest,
        types.ListPromptsRequest,
        types.GetPromptRequest,
    }.issubset(handlers)


def _initialized_app_for_sync_test():
    App = deriveApp(
        title=NOTE_MCP.name,
        version=NOTE_MCP.version,
        engine=mem(async_=False),
        tables=NOTE_MCP.tables,
    )
    app = App()
    app.initialize()
    return app


@pytest.mark.asyncio
async def test_official_sdk_client_lists_and_calls_all_tigrbl_tools() -> None:
    service = await TigrblMCP.make(NOTE_MCP, engine=mem(async_=False))

    async with create_connected_server_and_client_session(service.provide()) as client:
        listed = await client.list_tools()
        assert [tool.name for tool in listed.tools] == [
            "create_note",
            "read_note",
            "list_notes",
        ]
        listed_by_name = {tool.name: tool for tool in listed.tools}
        assert listed_by_name["create_note"].inputSchema["required"] == [
            "title",
            "body",
        ]
        assert listed_by_name["read_note"].annotations.readOnlyHint is True
        assert listed_by_name["create_note"].annotations.readOnlyHint is False

        created = await client.call_tool(
            "create_note",
            {"title": "MCP", "body": "Backed by Tigrbl."},
        )
        assert created.isError is False
        assert created.structuredContent is not None
        note_id = created.structuredContent["id"]

        read = await client.call_tool("read_note", {"id": note_id})
        assert read.isError is False
        assert read.structuredContent == created.structuredContent

        listed_notes = await client.call_tool("list_notes", {})
        assert listed_notes.isError is False
        assert listed_notes.structuredContent["result"] == [created.structuredContent]


@pytest.mark.asyncio
async def test_official_sdk_client_reads_resource_and_gets_prompt() -> None:
    service = await TigrblMCP.make(NOTE_MCP, engine=mem(async_=False))

    async with create_connected_server_and_client_session(service.provide()) as client:
        created = await client.call_tool(
            "create_note",
            {"title": "Resource", "body": "Context content."},
        )
        note_id = created.structuredContent["id"]

        templates = await client.list_resource_templates()
        assert len(templates.resourceTemplates) == 1
        assert str(templates.resourceTemplates[0].uriTemplate) == "note://{note_id}"

        resource = await client.read_resource(AnyUrl(f"note://{note_id}"))
        assert len(resource.contents) == 1
        payload = json.loads(resource.contents[0].text)
        assert payload == {
            "body": "Context content.",
            "id": note_id,
            "title": "Resource",
        }

        prompts = await client.list_prompts()
        assert [prompt.name for prompt in prompts.prompts] == ["summarize_note"]
        prompt = await client.get_prompt(
            "summarize_note",
            {"note_id": note_id},
        )
        assert len(prompt.messages) == 1
        assert f"note://{note_id}" in prompt.messages[0].content.text


@pytest.mark.asyncio
async def test_stdio_has_no_asgi_application_or_scope() -> None:
    service = await TigrblMCP.make(NOTE_MCP, engine=mem(async_=False))

    assert service.asgi_app("stdio") is None
    assert service.provide() is service.mcp
    assert parse_args([]).transport == "stdio"


@pytest.mark.asyncio
async def test_streamable_http_exposes_mcp_asgi_scope() -> None:
    service = await TigrblMCP.make(NOTE_MCP, engine=mem(async_=False))
    app = service.asgi_app("streamable-http")

    assert app is not None
    mcp_route = next(route for route in app.routes if route.path == "/mcp")
    assert mcp_route.path == "/mcp"
    assert (
        mcp_route.matches(
            {
                "type": "http",
                "http_version": "1.1",
                "method": "POST",
                "scheme": "http",
                "path": "/mcp",
                "raw_path": b"/mcp",
                "query_string": b"",
                "root_path": "",
                "headers": [],
                "client": ("127.0.0.1", 12345),
                "server": ("testserver", 80),
            }
        )[0].name
        == "FULL"
    )
    assert parse_args(["--transport", "streamable-http"]).transport == (
        "streamable-http"
    )


@pytest.mark.asyncio
async def test_official_sdk_client_connects_over_streamable_http_asgi() -> None:
    service = await TigrblMCP.make(NOTE_MCP, engine=mem(async_=False))
    app = service.asgi_app("streamable-http")
    assert app is not None

    transport = httpx.ASGITransport(app=app)
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as http_client:
            async with streamable_http_client(
                "http://testserver/mcp",
                http_client=http_client,
            ) as streams:
                async with ClientSession(streams[0], streams[1]) as client:
                    await client.initialize()
                    tools = await client.list_tools()
                    prompts = await client.list_prompts()
                    templates = await client.list_resource_templates()

    assert [tool.name for tool in tools.tools] == [
        "create_note",
        "read_note",
        "list_notes",
    ]
    assert [prompt.name for prompt in prompts.prompts] == ["summarize_note"]
    assert str(templates.resourceTemplates[0].uriTemplate) == "note://{note_id}"


@pytest.mark.asyncio
async def test_derive_preserves_transport_provisioning_contract() -> None:
    service = await TigrblMCP.make(NOTE_MCP, engine=mem(async_=False))
    derived = TigrblMCP.derive(NOTE_MCP, service.tigrbl)

    assert derived.provide() is derived.mcp
    assert derived.asgi_app("stdio") is None
    assert derived.asgi_app("streamable-http") is not None
    with pytest.raises(ValueError, match="unsupported MCP transport"):
        derived.asgi_app("sse")


def test_factory_surface_replaces_build_helpers() -> None:
    assert not hasattr(app_module, "build_tigrbl_app")
    assert not hasattr(server_module, "build_server")
    assert all(
        callable(getattr(TigrblMCP, method))
        for method in ("make", "define", "derive", "provide")
    )


def test_factory_descriptors_and_provide_accessor_are_explicit() -> None:
    assert isinstance(TigrblMCP.__dict__["define"], classmethod)
    assert isinstance(TigrblMCP.__dict__["make"], classmethod)
    assert isinstance(TigrblMCP.__dict__["derive"], classmethod)
    assert not isinstance(TigrblMCP.__dict__["provide"], classmethod)
    assert not inspect.iscoroutinefunction(TigrblMCP.define)
    assert inspect.iscoroutinefunction(TigrblMCP.make)
    assert not inspect.iscoroutinefunction(TigrblMCP.derive)
    assert not inspect.iscoroutinefunction(TigrblMCP.provide)
    assert "definition" in inspect.signature(TigrblMCP.make).parameters
    assert "app" in inspect.signature(TigrblMCP.derive).parameters
    assert tuple(inspect.signature(TigrblMCP.provide).parameters) == ("self",)
    assert TigrblMCP.provide.__doc__ is not None
    assert "not a constructor" in TigrblMCP.provide.__doc__


def test_python_sources_use_only_lowlevel_sdk() -> None:
    sources = [*EXAMPLE_DIR.glob("*.py"), *EXAMPLE_DIR.joinpath("tests").glob("*.py")]
    forbidden = "fast" + "mcp"
    for source in sources:
        assert forbidden not in source.read_text(encoding="utf-8").lower(), source


@pytest.mark.asyncio
async def test_official_sdk_client_connects_over_real_stdio() -> None:
    params = StdioServerParameters(
        command=sys.executable,
        args=[str(EXAMPLE_DIR / "server.py"), "--transport", "stdio"],
        cwd=str(EXAMPLE_DIR),
    )

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as client:
            await client.initialize()
            tools = await client.list_tools()

    assert [tool.name for tool in tools.tools] == [
        "create_note",
        "read_note",
        "list_notes",
    ]
