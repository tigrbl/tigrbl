"""Same-origin API and production frontend for the loopback demo."""

import asyncio
import logging
import time
from pathlib import Path
from uuid import uuid4

from trace_lab.gateway import FAVICON_PATH as FAVICON_PATH, serve_frontend
from trace_lab.http import utc_now


def build_gateway(app, capture, frontend: Path, run_scenario, reply, base_url):
    frontend = frontend.resolve()

    async def gateway(scope, receive, send):
        path = scope.get("path", "")
        method = scope.get("method")
        if scope["type"] != "http":
            return await app(scope, receive, send)
        if path == "/demo/trace":
            return (
                await reply(send, 200, capture.snapshot())
                if method == "GET"
                else await reply(send, 405, {"error": "Method not supported."})
            )
        if path == "/demo/run":
            if method != "POST":
                return await reply(send, 405, {"error": "Method not supported."})
            host = dict(scope["headers"]).get(b"host")
            origin = dict(scope["headers"]).get(b"origin")
            expected = base_url().encode()
            if host != expected.removeprefix(b"http://") or origin not in (
                None,
                expected,
            ):
                return await reply(
                    send, 403, {"error": "Use the displayed loopback URL."}
                )
            if capture.active_run is not None:
                return await reply(
                    send, 409, {"error": "A scenario is already running."}
                )
            run_id = uuid4().hex
            note_id = uuid4().hex
            started_at = utc_now()
            start_time = time.monotonic()
            start_revision = capture.timeline.revision
            capture.active_run = run_id
            results = {}
            try:
                results = await asyncio.wait_for(run_scenario(note_id), 25)
                status = "completed"
            except Exception:
                logging.getLogger(__name__).exception("Trace lab scenario failed")
                status = "failed"
            finally:
                summary = {
                    "run_id": run_id,
                    "status": "failed" if not results else status,
                    "started_at": started_at,
                    "completed_at": utc_now(),
                    "duration_ms": round((time.monotonic() - start_time) * 1000, 2),
                    "emitted_events": capture.timeline.revision - start_revision,
                    "note_id": note_id,
                    "transports": results,
                }
                capture.last_run = summary
                capture.active_run = None
            if status == "failed":
                return await reply(
                    send,
                    500,
                    {"error": "Scenario failed. Inspect the captured events."},
                )
            return await reply(send, 200, summary)

        if path in {"/", "/distributions"} or path.startswith("/assets/"):
            return await serve_frontend(frontend, path, method, send, reply)
        return await app(scope, receive, send)

    return gateway
