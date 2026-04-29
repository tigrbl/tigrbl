from __future__ import annotations

from pathlib import PurePosixPath
from typing import Any, Callable


def run_static_file_chain(
    *,
    request: dict[str, Any],
    mount: dict[str, Any],
    file_exists: Callable[[str], bool],
    read_file: Callable[[str], bytes] | None = None,
    stat_file: Callable[[str], dict[str, Any]] | None = None,
    read_file_range: Callable[[str, int, int], bytes] | None = None,
    capture_errors: bool = False,
) -> dict[str, object]:
    rel = _relative_path(str(request.get("path", "")), str(mount.get("path", "")))
    if rel is None or _is_unsafe(rel):
        return {
            "status_code": 404,
            "completed": True,
            "error_ctx": {"subevent": "static_file.security.reject"},
        }
    file_path = str(PurePosixPath(str(mount["directory"])) / rel)
    if not file_exists(file_path):
        return {"status_code": 404, "subevent": "static_file.not_found", "completed": True}

    headers: dict[str, str] = {}
    request_headers = dict(request.get("headers") or {})
    range_header = request_headers.get("range")
    if range_header and stat_file and read_file_range:
        start, end = _parse_range(range_header)
        stat = stat_file(file_path)
        body = read_file_range(file_path, start, end)
        headers["content-range"] = f"bytes {start}-{end}/{stat['size']}"
        if stat.get("etag"):
            headers["etag"] = str(stat["etag"])
        return {
            "status_code": 206,
            "file_path": file_path,
            "body": body,
            "headers": headers,
            "completed_subevent": "static_file.emit_complete",
        }

    body = read_file(file_path) if read_file else b""
    return {
        "status_code": 200,
        "file_path": file_path,
        "body": body,
        "headers": headers,
        "completed_subevent": "static_file.emit_complete",
    }


def _relative_path(path: str, mount_path: str) -> str | None:
    if not path.startswith(mount_path):
        return None
    rel = path[len(mount_path) :].lstrip("/")
    return rel or "index.html"


def _is_unsafe(rel: str) -> bool:
    parts = PurePosixPath(rel).parts
    return any(part in {"..", ""} for part in parts)


def _parse_range(value: str) -> tuple[int, int]:
    if not value.startswith("bytes="):
        raise ValueError("range header must use bytes unit")
    start, end = value.removeprefix("bytes=").split("-", 1)
    return int(start), int(end)


__all__ = ["run_static_file_chain"]
