"""Static monitor assets served by the collector."""

import mimetypes
from pathlib import Path

FAVICON_PATH = Path(__file__).with_name("assets") / "favicon.svg"


async def serve_frontend(frontend, path, method, send, reply, *, monitor=False):
    if method != "GET":
        return await reply(send, 405, {"error": "Method not supported."})
    is_page = not path.startswith("/assets/")
    relative = "index.html" if is_page else path[1:]
    asset = (frontend / relative).resolve()
    if not asset.is_relative_to(frontend) or not asset.is_file():
        return await reply(
            send, 404, {"error": "Frontend asset missing. Run pnpm build."}
        )
    content_type = mimetypes.guess_type(asset)[0] or "application/octet-stream"
    body = asset.read_bytes()
    if monitor and relative == "index.html":
        body = body.replace(b'<div id="root"', b'<div id="root" data-trace-monitor', 1)
    return await reply(send, 200, body, content_type)
