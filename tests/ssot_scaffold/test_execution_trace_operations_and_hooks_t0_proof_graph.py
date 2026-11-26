import asyncio
import inspect

import httpx
import pytest
from tigrbl import Column, HTTPException, TableBase, TigrblApp, Timeline, hook_ctx
from tigrbl.factories.engine import sqlitef
from tigrbl_core._spec import AppSpec, HttpRestBindingSpec, OpSpec
from tigrbl_engine_sqlite.plugin import register


@pytest.mark.asyncio
async def test_named_operation_and_hook_timings_include_failure_and_rollback(tmp_path):
    class TracedNote(TableBase):
        __tablename__ = "traced_notes"

        id = Column(
            storage=Column.S(primary_key=True, nullable=False),
            field=Column.F(py_type=str, required_in=("create",)),
            io=Column.IO(in_verbs=("create",), out_verbs=("create", "read")),
        )
        __tigrbl_ops__ = (
            OpSpec(
                alias="create",
                target="create",
                tx_scope="read_write",
                bindings=(
                    HttpRestBindingSpec(
                        proto="http.rest", methods=("POST",), path="/notes"
                    ),
                ),
            ),
            OpSpec(
                alias="read",
                target="read",
                tx_scope="read_only",
                bindings=(
                    HttpRestBindingSpec(
                        proto="http.rest", methods=("GET",), path="/notes/{id}"
                    ),
                ),
            ),
        )

        @hook_ctx(ops="create", phase="PRE_HANDLER")
        def before_write(cls, ctx):
            assert ctx["op"] == "create"

        @hook_ctx(ops="create", phase="POST_HANDLER")
        async def flush_note(cls, ctx):
            await ctx["db"].flush()

        @hook_ctx(ops="create", phase="PRE_COMMIT")
        async def inspect_note(cls, ctx):
            await asyncio.sleep(0.01)
            if ctx["payload"]["id"] == "reject":
                raise HTTPException(422, "Note rejected")

    register()
    timeline = Timeline()
    app = TigrblApp.from_spec(
        AppSpec(engine=sqlitef(str(tmp_path / "trace.sqlite3"))),
        trace_sink=timeline.add,
        trace_atoms=True,
    )
    app.include_table(TracedNote)
    initialized = app.initialize()
    if inspect.isawaitable(initialized):
        await initialized

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://trace.test"
    ) as client:
        for note_id, code, outcome, transaction_outcome in (
            ("accept", 201, "ok", "committed"),
            ("reject", 422, "failed", "rolled_back"),
        ):
            response = await client.post("/notes", json={"id": note_id})
            assert response.status_code == code, response.text
            correlation = response.headers["x-correlation-id"]
            records = [
                row
                for row in timeline.data()["events"]
                if row.get("correlation_id") == correlation
            ]
            (operation,) = [row for row in records if row["kind"] == "Invocation"]
            (exchange,) = [row for row in records if row["kind"] == "Response"]
            hooks = [row for row in records if row["kind"] == "Hook"]
            atoms = [row for row in records if row["kind"] == "Atom"]
            assert atoms
            assert any(
                row["atom_phase"] == ("TX_COMMIT" if code == 201 else "TX_ROLLBACK")
                for row in atoms
            )
            assert [row["atom_ordinal"] for row in atoms] == list(
                range(1, len(atoms) + 1)
            )
            assert all(
                row["atom_label"]
                and row["atom_phase"]
                and row["invocation_id"] == operation["invocation_id"]
                and row["timing_boundary"] == "atom_monotonic"
                and row["measured_duration_ms"] >= 0
                for row in atoms
            )
            assert (operation["op_model"], operation["op_alias"]) == (
                "TracedNote",
                "create",
            )
            assert operation["outcome"] == outcome
            assert operation["timing_boundary"] == "invocation_monotonic"
            assert [
                (hook["hook_name"], hook["hook_phase"], hook["outcome"])
                for hook in hooks
            ] == [
                ("before_write", "PRE_HANDLER", "ok"),
                ("flush_note", "POST_HANDLER", "ok"),
                ("inspect_note", "PRE_COMMIT", outcome),
            ]
            assert (
                operation["measured_duration_ms"]
                >= hooks[-1]["measured_duration_ms"]
                >= 5
            )
            for hook in hooks:
                assert hook["timing_boundary"] == "hook_monotonic"
                assert hook["clock_domain"] == "server_monotonic"
                assert hook["invocation_id"] == operation["invocation_id"]
                assert operation["source_started_at"] <= hook["source_started_at"]
                assert hook["source_ended_at"] <= operation["source_ended_at"]
            (transaction,) = [
                row
                for row in records
                if row["kind"] == "Transaction"
                and row["outcome"] == transaction_outcome
            ]
            (begin,) = [
                row
                for row in records
                if row["kind"] == "Transaction" and row["outcome"] == "begin"
            ]
            assert begin["transaction_id"] == transaction["transaction_id"]
            (start_tx,) = [
                row
                for row in atoms
                if row["atom_phase"] == "START_TX"
                and row["atom_label"].startswith("atom:sys:start_tx@")
            ]
            assert (
                start_tx["source_started_at"]
                <= begin["source_started_at"]
                <= start_tx["source_ended_at"]
                <= hooks[0]["source_started_at"]
            )
            preludes = [row for row in atoms if row["atom_label"].startswith("fused:")]
            assert [(row["atom_label"], row["atom_phase"]) for row in preludes] == [
                ("fused:compiled_context_setup", "INGRESS_BEGIN"),
                ("fused:compiled_input_prepare", "INGRESS_PARSE"),
                ("fused:compiled_validate_and_assemble", "PRE_HANDLER"),
            ]
            ingress = [row for row in atoms if row["atom_phase"] == "INGRESS_BEGIN"]
            pre_handler = [row for row in atoms if row["atom_phase"] == "PRE_HANDLER"]
            assert ingress and pre_handler
            assert ingress[-1]["atom_ordinal"] < preludes[1]["atom_ordinal"]
            assert ingress[-1]["atom_ordinal"] < start_tx["atom_ordinal"]
            assert start_tx["atom_ordinal"] < pre_handler[0]["atom_ordinal"]
            assert hooks[-1]["transaction_id"] == transaction["transaction_id"]
            assert hooks[-1]["engine_session_id"] == transaction["engine_session_id"]
            assert begin["source_started_at"] == transaction["source_started_at"]
            assert transaction["source_started_at"] <= transaction["source_ended_at"]
            assert transaction["clock_domain"] == "engine_monotonic"
            assert transaction["timing_boundary"] == (
                "db_tx_begin_to_commit" if code == 201 else "db_tx_begin_to_rollback"
            )
            assert (
                transaction["measured_duration_ms"] >= hooks[-1]["measured_duration_ms"]
            )
            assert exchange["status"] == code
            assert exchange["clock_domain"] == "server_monotonic"
            assert exchange["timing_boundary"] == "ingress_to_egress_monotonic"
            assert exchange["measured_duration_ms"] >= hooks[-1]["measured_duration_ms"]
            assert exchange["source_started_at"] <= operation["source_started_at"]
            assert hooks[-1]["source_ended_at"] <= exchange["source_ended_at"]
            flushes = [row for row in records if row["kind"] == "Flush"]
            assert len(flushes) == (2 if code == 201 else 1)
            assert len({row["flush_id"] for row in flushes}) == len(flushes)
            for flush in flushes:
                assert flush["outcome"] == "ok"
                assert flush["invocation_id"] == operation["invocation_id"]
                assert flush["transaction_id"] == transaction["transaction_id"]
                assert flush["timing_boundary"] == "db_flush_monotonic"
                assert flush["clock_domain"] == "engine_monotonic"
                assert flush["measured_duration_ms"] > 0
            assert hooks[1]["source_started_at"] <= flushes[0]["source_started_at"]
            assert flushes[0]["source_ended_at"] <= hooks[1]["source_ended_at"]
        assert (await client.get("/notes/accept")).status_code == 200
        assert (await client.get("/notes/reject")).status_code == 404

        invalid = await client.post("/notes", json={})
        assert invalid.status_code == 422
        invalid_rows = [
            row
            for row in timeline.data()["events"]
            if row.get("correlation_id") == invalid.headers["x-correlation-id"]
        ]
        assert any(
            row.get("atom_label") == "fused:compiled_validate_and_assemble"
            and row.get("atom_phase") == "PRE_HANDLER"
            and row.get("outcome") == "failed"
            for row in invalid_rows
        )
        assert not any(row.get("atom_phase") == "HANDLER" for row in invalid_rows)
        assert any(
            row["kind"] == "Transaction" and row.get("outcome") == "rolled_back"
            for row in invalid_rows
        )

        duplicate = await client.post("/notes", json={"id": "accept"})
        assert duplicate.status_code >= 400
        failed_flushes = [
            row
            for row in timeline.data()["events"]
            if row.get("correlation_id") == duplicate.headers["x-correlation-id"]
            and row["kind"] == "Flush"
        ]
        (failed_flush,) = failed_flushes
        assert failed_flush["outcome"] == "failed"
        assert failed_flush["engine_session_id"]
        assert failed_flush["invocation_id"]
        assert failed_flush["measured_duration_ms"] > 0
