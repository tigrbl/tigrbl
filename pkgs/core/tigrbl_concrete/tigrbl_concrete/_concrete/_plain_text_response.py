"""Concrete plain-text response primitive."""

from __future__ import annotations

from collections.abc import Mapping

from ._response import Response


class PlainTextResponse(Response):
    def __init__(
        self,
        content: str,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        response_headers: list[tuple[str, str]] = [
            ("content-type", "text/plain; charset=utf-8")
        ]
        for key, value in (headers or {}).items():
            response_headers.append((key.lower(), value))
        super().__init__(
            status_code=status_code,
            headers=response_headers,
            body=content.encode("utf-8"),
            media_type="text/plain",
        )


__all__ = ["PlainTextResponse"]
