"""Static monitor assets served by the collector."""

from html import escape
from importlib.metadata import PackageNotFoundError, version
import mimetypes
from pathlib import Path

FAVICON_PATH = Path(__file__).with_name("assets") / "favicon.svg"
IMAGE_VERSION_FILE = ".trace-lab-image-version"


def _monitor_attributes(frontend: Path) -> bytes:
    attributes = ["data-trace-monitor"]
    try:
        backend_version = version("tigrbl-transport-trace-lab")
    except PackageNotFoundError:
        pass
    else:
        attributes.append(f'data-trace-backend-version="{escape(backend_version)}"')

    try:
        image_version = (
            (frontend / IMAGE_VERSION_FILE).read_text(encoding="utf-8").strip()
        )
    except FileNotFoundError:
        image_version = ""
    if image_version:
        attributes.append(f'data-trace-image-version="{escape(image_version)}"')
    return (" " + " ".join(attributes)).encode()


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
        root = b'<div id="root"'
        body = body.replace(root, root + _monitor_attributes(frontend), 1)
    return await reply(send, 200, body, content_type)
