"""Independent notes pilot with a Tigrbl trace exporter."""

import asyncio
import inspect
import os
from pathlib import Path

from tigrbl import Column, HTMLResponse, HTTPException, TableBase, TigrblApp, hook_ctx
from sqlalchemy import select
from tigrbl.factories.engine import sqlitef
from tigrbl_core._spec import AppSpec, HttpRestBindingSpec, OpSpec
from tigrbl_engine_sqlite.plugin import register
from tigrcorn.config.load import build_config
from tigrcorn.server.runner import TigrCornServer
from tigrbl_trace_transport import TraceExporter


class PilotNote(TableBase):
    __tablename__ = "pilot_notes"

    id = Column(
        storage=Column.S(primary_key=True, nullable=False),
        field=Column.F(py_type=str, required_in=("create",)),
        io=Column.IO(in_verbs=("create",), out_verbs=("create",)),
    )
    text = Column(
        storage=Column.S(nullable=False),
        field=Column.F(py_type=str, required_in=("create",)),
        io=Column.IO(in_verbs=("create",), out_verbs=("create",)),
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
    )

    @hook_ctx(ops="create", phase="POST_HANDLER")
    async def verify_note_visible(cls, ctx):
        await asyncio.sleep(0.025)
        note_id = ctx["payload"]["id"]
        result = await ctx["db"].execute(select(cls.id).where(cls.id == note_id))
        result.scalar_one()

    @hook_ctx(ops="*", phase="PRE_COMMIT")
    async def wait_before_validation(cls, ctx):
        await asyncio.sleep(0.035)

    @hook_ctx(ops="*", phase="PRE_COMMIT")
    async def validate_note(cls, ctx):
        await asyncio.sleep(0.055)
        if ctx["op"] == "create" and ctx["payload"]["text"] == "reject":
            raise HTTPException(422, "Note rejected")


PAGE = """<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Notes Pilot</title>
<style>
body{font:16px/1.55 system-ui,sans-serif;margin:0;background:#f4f6f9;color:#15233c}
main{max-width:36rem;margin:12vh auto;padding:2rem;background:white;border:1px solid #d9e1ed;border-radius:12px}
h1{margin-top:0} label{display:block;font-weight:600}input{box-sizing:border-box;width:100%;font:inherit;padding:.6rem;margin:.35rem 0 .8rem;border:1px solid #8292aa;border-radius:4px}
button{font:inherit;background:#143f7b;color:white;padding:.55rem 1rem;border:0;border-radius:4px}
output{display:block;margin-top:1rem}a{color:#164f9d}code{overflow-wrap:anywhere}
</style>
<main>
  <h1>Notes Pilot</h1>
  <p>Save a note and open its trace to see two timed hooks on the <code>PRE_COMMIT</code> lane. Enter <code>reject</code> to make the second hook fail and roll back the write.</p>
  <form>
    <label for="text">Note</label>
    <input id="text" name="text" maxlength="250" value="My first traced note" required>
    <button type="submit">Save note</button>
  </form>
  <output aria-live="polite"></output>
</main>
<script type="module">
const form = document.querySelector('form');
const output = document.querySelector('output');
form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const button = form.querySelector('button');
  button.disabled = true;
  output.textContent = 'Saving…';
  try {
    const response = await fetch('/notes', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({id: crypto.randomUUID(), text: new FormData(form).get('text')}),
    });
    const correlation = response.headers.get('x-correlation-id');
    if (!correlation) throw new Error('No trace ID returned (HTTP ' + response.status + ')');
    const trace = new URL('http://127.0.0.1:8766/');
    trace.searchParams.set('correlation_id', correlation);
    const link = document.createElement('a');
    link.href = trace.href;
    link.textContent = 'Open this request in Trace Lab';
    const id = document.createElement('code');
    id.textContent = correlation;
    const status = response.ok ? 'Note saved. ' : 'Note rejected (HTTP ' + response.status + '). ';
    output.replaceChildren(status, link, document.createElement('br'), id);
  } catch (error) {
    output.textContent = error.message;
  } finally {
    button.disabled = false;
  }
});
</script>
"""


async def main():
    register()
    exporter = TraceExporter(
        os.environ.get("TRACE_COLLECTOR_URL", "http://127.0.0.1:8766"),
        os.environ["TRACE_INGEST_TOKEN"],
        "notes-pilot",
        "local-demo",
    )
    engine = sqlitef(str(Path(os.environ.get("TRACE_NOTES_DATABASE", "notes.sqlite3"))))
    spec = AppSpec(title="Notes Pilot", engine=engine)
    app = TigrblApp.from_spec(
        spec,
        trace_sink=exporter.capture,
        trace_atoms=os.environ.get("TRACE_PILOT_ATOMS", "1") == "1",
    )
    app.include_table(PilotNote)

    @app.get("/")
    async def home():
        return HTMLResponse(PAGE)

    initialized = app.initialize()
    if inspect.isawaitable(initialized):
        await initialized

    server = TigrCornServer(
        app,
        build_config(
            host="127.0.0.1",
            port=int(os.environ.get("TRACE_NOTES_PORT", "8767")),
            lifespan="off",
            http_versions=["1.1"],
            protocols=["http1"],
        ),
    )
    exporter.start()
    try:
        await server.start()
        print(
            f"Notes Pilot http://127.0.0.1:{os.environ.get('TRACE_NOTES_PORT', '8767')}/",
            flush=True,
        )
        await asyncio.Event().wait()
    finally:
        await server.close()
        await exporter.close()


if __name__ == "__main__":
    asyncio.run(main())


def cli():
    asyncio.run(main())
