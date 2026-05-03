"""Concrete file response primitive."""

from __future__ import annotations

import mimetypes
from collections.abc import AsyncIterator
from collections.abc import Mapping
from pathlib import Path

from ._response import Response


class FileResponse(Response):
    def __init__(
        self,
        path: str,
        media_type: str | None = None,
        *,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
        filename: str | None = None,
        download: bool = False,
    ) -> None:
        resolved_path = Path(path)
        content_type = (
            media_type or mimetypes.guess_type(path)[0] or "application/octet-stream"
        )
        response_headers: list[tuple[str, str]] = [("content-type", content_type)]
        for key, value in (headers or {}).items():
            response_headers.append((key.lower(), value))
        if download or filename:
            resolved_filename = filename or resolved_path.name
            response_headers.append(
                ("content-disposition", f'attachment; filename="{resolved_filename}"')
            )
        super().__init__(
            status_code=status_code,
            headers=response_headers,
            body=resolved_path.read_bytes(),
            media_type=content_type,
            filename=filename,
            download=download,
        )
        self.path = str(resolved_path)

    @property
    def body_iterator(self) -> AsyncIterator[bytes]:
        async def _iter() -> AsyncIterator[bytes]:
            with Path(self.path).open("rb") as handle:
                while True:
                    chunk = handle.read(64 * 1024)
                    if not chunk:
                        break
                    yield chunk

        return _iter()


__all__ = ["FileResponse"]
