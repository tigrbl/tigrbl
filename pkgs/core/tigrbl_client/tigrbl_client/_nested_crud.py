# tigrbl_client/_nested_crud.py
from __future__ import annotations

from typing import Any, Iterable, TypeVar

T = TypeVar("T")


class NestedCRUDMixin:
    """Helpers for hierarchical REST resource paths."""

    def __init__(self) -> None:
        self._nested_crud_enabled = True

    @staticmethod
    def _normalize_segment(value: Any) -> str:
        raw = str(value).strip("/")
        if not raw:
            raise ValueError("Nested resource segments must be non-empty")
        return raw

    def nested_path(self, *segments: Any) -> str:
        """Build a normalized nested resource path.

        Examples:
            ``nested_path("users", 1, "posts", 2) -> "/users/1/posts/2"``
        """

        if not segments:
            raise ValueError("At least one nested segment is required")
        normalized = [self._normalize_segment(segment) for segment in segments]
        return "/" + "/".join(normalized)

    def nested_collection_path(
        self,
        *parents: Any,
        resource: str,
    ) -> str:
        """Build a nested collection path under one or more parent pairs."""

        parent_segments = tuple(parents)
        if len(parent_segments) % 2 != 0:
            raise ValueError("parents must be resource/id pairs")
        return self.nested_path(*parent_segments, resource)

    def nested_member_path(
        self,
        *parents: Any,
        resource: str,
        item_id: Any,
    ) -> str:
        """Build a nested member path under one or more parent pairs."""

        return self.nested_path(*parents, resource, item_id)

    def nested_get(self, *segments: Any, **kwargs: Any) -> Any:
        return self.get(self.nested_path(*segments), **kwargs)

    def nested_post(self, *segments: Any, **kwargs: Any) -> Any:
        return self.post(self.nested_path(*segments), **kwargs)

    def nested_put(self, *segments: Any, **kwargs: Any) -> Any:
        return self.put(self.nested_path(*segments), **kwargs)

    def nested_patch(self, *segments: Any, **kwargs: Any) -> Any:
        return self.patch(self.nested_path(*segments), **kwargs)

    def nested_delete(self, *segments: Any, **kwargs: Any) -> Any:
        return self.delete(self.nested_path(*segments), **kwargs)

    async def anested_get(self, *segments: Any, **kwargs: Any) -> Any:
        return await self.aget(self.nested_path(*segments), **kwargs)

    async def anested_post(self, *segments: Any, **kwargs: Any) -> Any:
        return await self.apost(self.nested_path(*segments), **kwargs)

    async def anested_put(self, *segments: Any, **kwargs: Any) -> Any:
        return await self.aput(self.nested_path(*segments), **kwargs)

    async def anested_patch(self, *segments: Any, **kwargs: Any) -> Any:
        return await self.apatch(self.nested_path(*segments), **kwargs)

    async def anested_delete(self, *segments: Any, **kwargs: Any) -> Any:
        return await self.adelete(self.nested_path(*segments), **kwargs)


__all__ = ["NestedCRUDMixin"]
