from __future__ import annotations

from pathlib import Path
from typing import Any

from tigrbl_concrete._concrete._file_response import FileResponse
from tigrbl_concrete._concrete._response import Response


def _safe_join(base: Path, relative: str) -> Path | None:
    target = (base / relative.lstrip('/')).resolve()
    try:
        target.relative_to(base.resolve())
    except ValueError:
        return None
    return target


def _mount_static(router: Any, *, directory: str | Path, path: str = "/static") -> Any:
    mount_path_raw = str(path or "")
    if not mount_path_raw.startswith("/"):
        raise ValueError("static mount path must be absolute.")
    mount_path = mount_path_raw.rstrip("/") or "/"
    if mount_path in {"/rpc", "/system", "/docs", "/openapi.json", "/openrpc.json"}:
        raise ValueError(f"static mount path {mount_path!r} is reserved.")
    directory_path = Path(directory).resolve()
    if not directory_path.exists() or not directory_path.is_dir():
        raise ValueError("static mount directory must exist and be a directory.")
    mounts = list(getattr(router, '_static_mounts', []) or [])
    mounts.append({'path': mount_path, 'directory': str(directory_path)})
    router._static_mounts = mounts
    return router


def _serve_static(router: Any, request: Any) -> Response | None:
    request_path = str(getattr(request, 'path', '') or '')
    for mount in list(getattr(router, '_static_mounts', []) or []):
        mount_path = str(mount.get('path') or '/').rstrip('/') or '/'
        if request_path == mount_path or request_path.startswith(mount_path + '/'):
            suffix = request_path[len(mount_path):].lstrip('/')
            candidate = _safe_join(Path(mount['directory']), suffix)
            if candidate is None or not candidate.exists() or not candidate.is_file():
                return Response.text('Not Found', status_code=404)
            return FileResponse(str(candidate))
    return None


__all__ = ['_mount_static', '_serve_static']
