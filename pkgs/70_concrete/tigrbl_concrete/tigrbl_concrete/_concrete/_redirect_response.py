"""Concrete redirect response primitive."""

from __future__ import annotations

from collections.abc import Mapping

from ._response import Response


class RedirectResponse(Response):
    def __init__(
        self,
        url: str,
        status_code: int = 307,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        response_headers: list[tuple[str, str]] = [("location", url)]
        for key, value in (headers or {}).items():
            response_headers.append((key.lower(), value))
        super().__init__(
            status_code=status_code,
            headers=response_headers,
            body=b"",
            media_type=None,
        )
        self.url = url


__all__ = ["RedirectResponse"]
