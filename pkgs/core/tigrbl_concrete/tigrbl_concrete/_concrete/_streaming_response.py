"""Concrete streaming response primitive."""

from __future__ import annotations

from collections.abc import AsyncIterable, AsyncIterator, Iterable
from typing import Any

from ._response import Response


class StreamingResponse(Response):
    def __init__(
        self,
        content: Iterable[bytes] | AsyncIterable[bytes] | bytes,
        status_code: int = 200,
        media_type: str = "application/octet-stream",
        headers: dict[str, str] | list[tuple[str, str]] | None = None,
    ) -> None:
        super().__init__(
            status_code=status_code,
            headers=headers or [("content-type", media_type)],
            body=b"",
            media_type=media_type,
            kind="stream",
        )
        self._content = content

    @property
    def body_iterator(self) -> AsyncIterator[bytes]:
        async def _iter() -> AsyncIterator[bytes]:
            source: Any = self._content
            if isinstance(source, (bytes, bytearray, memoryview)):
                yield bytes(source)
                return
            if hasattr(source, "__aiter__"):
                async for chunk in source:  # type: ignore[union-attr]
                    yield bytes(chunk)
                return
            for chunk in source:  # type: ignore[union-attr]
                yield bytes(chunk)

        return _iter()


__all__ = ["StreamingResponse"]
