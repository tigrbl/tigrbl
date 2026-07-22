from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, RootModel
from tigrbl import TableBase, TigrblApp
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String
from tigrbl_core._spec import OpSpec

from tigrbl_mcp import TigrblMCP


class NoteCreateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    body: str


class NoteIdInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID


class EmptyInput(BaseModel):
    model_config = ConfigDict(extra="forbid")


class NoteOutput(BaseModel):
    title: str
    body: str
    id: UUID


class NoteListOutput(RootModel[list[NoteOutput]]):
    pass


class Note(TableBase, GUIDPk):
    __tablename__ = "mcp_demo_note"
    __allow_unmapped__ = True

    title = Column(String, nullable=False)
    body = Column(String, nullable=False)


def _mcp_policy(
    *,
    name: str,
    title: str,
    description: str,
    read_only: bool,
    destructive: bool = False,
    idempotent: bool = False,
) -> dict[str, Any]:
    return {
        "mcp": {
            "expose": True,
            "name": name,
            "title": title,
            "description": description,
            "read_only": read_only,
            "destructive": destructive,
            "idempotent": idempotent,
            "open_world": False,
        }
    }


# MCP exposure is deliberately opt-in. The remaining canonical CRUD operations
# are still available to Tigrbl but do not appear in the MCP tool catalog.
Note.__tigrbl_ops__ = (
    OpSpec(
        alias="create",
        target="create",
        table=Note,
        request_model=NoteCreateInput,
        response_model=NoteOutput,
        extra=_mcp_policy(
            name="create_note",
            title="Create note",
            description="Create a note with a title and body.",
            read_only=False,
        ),
    ),
    OpSpec(
        alias="read",
        target="read",
        table=Note,
        request_model=NoteIdInput,
        response_model=NoteOutput,
        extra=_mcp_policy(
            name="read_note",
            title="Read note",
            description="Read one note by its identifier.",
            read_only=True,
            idempotent=True,
        ),
    ),
    OpSpec(
        alias="list",
        target="list",
        table=Note,
        request_model=EmptyInput,
        response_model=NoteListOutput,
        extra=_mcp_policy(
            name="list_notes",
            title="List notes",
            description="List all notes in the current server process.",
            read_only=True,
            idempotent=True,
        ),
    ),
)


def _create_note_tool(app: TigrblApp):
    async def create_note(title: str, body: str) -> NoteOutput:
        """Create a note with a title and body."""
        result = await app.rpc_call(
            "Note",
            "create",
            {"title": title, "body": body},
        )
        return NoteOutput.model_validate(result)

    return create_note


def _read_note_tool(app: TigrblApp):
    async def read_note(id: UUID) -> NoteOutput:
        """Read one note by its identifier."""
        result = await app.rpc_call("Note", "read", {"id": str(id)})
        return NoteOutput.model_validate(result)

    return read_note


def _list_notes_tool(app: TigrblApp):
    async def list_notes() -> list[NoteOutput]:
        """List all notes in the current server process."""
        result = await app.rpc_call("Note", "list", {})
        return [NoteOutput.model_validate(note) for note in result]

    return list_notes


def _provide_note_surfaces(mcp: FastMCP, app: TigrblApp) -> None:
    @mcp.resource(
        "note://{note_id}",
        name="note",
        title="Note",
        description="Read a Tigrbl note as JSON context.",
        mime_type="application/json",
    )
    async def note_resource(note_id: str) -> str:
        result = await app.rpc_call("Note", "read", {"id": note_id})
        return json.dumps(result, sort_keys=True)

    @mcp.prompt(
        name="summarize_note",
        title="Summarize note",
        description="Prepare a concise summary of one note resource.",
    )
    def summarize_note(note_id: str) -> str:
        return (
            f"Read note://{note_id}. Summarize its decisions and list any "
            "unresolved actions. Do not invent details absent from the note."
        )


NOTE_MCP = TigrblMCP.define(
    name="tigrbl-notes",
    version="0.1.0",
    instructions=(
        "Create and read notes. Read operations are safe; creation changes "
        "state and should reflect the user's explicit intent."
    ),
    tables=(Note,),
    tools={
        "create_note": _create_note_tool,
        "read_note": _read_note_tool,
        "list_notes": _list_notes_tool,
    },
    surfaces=(_provide_note_surfaces,),
)
