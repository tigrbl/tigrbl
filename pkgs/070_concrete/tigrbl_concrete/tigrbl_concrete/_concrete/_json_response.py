"""Concrete JSON response primitive."""

from __future__ import annotations

import json as json_module
from typing import Any
from collections.abc import Mapping

from ._response import Response


class JSONResponse(Response):
    def __init__(
        self,
        content: Any,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        payload = json_module.dumps(
            content, ensure_ascii=False, separators=(",", ":"), default=str
        ).encode("utf-8")
        response_headers: list[tuple[str, str]] = [
            ("content-type", "application/json; charset=utf-8")
        ]
        for key, value in (headers or {}).items():
            response_headers.append((key.lower(), value))
        super().__init__(
            status_code=status_code,
            headers=response_headers,
            body=payload,
            media_type="application/json",
        )


__all__ = ["JSONResponse"]
