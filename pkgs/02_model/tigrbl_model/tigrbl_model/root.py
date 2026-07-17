"""Root-value model support."""

from __future__ import annotations

from typing import Any, ClassVar

from .model import Model


class RootModel(Model):
    __root_model__: ClassVar[bool] = True
    root: Any

    def __init__(self, root: Any = None, **data: Any) -> None:
        if "root" in data:
            if root is not None:
                raise TypeError("RootModel accepts either positional root or root keyword, not both")
            root = data.pop("root")
        super().__init__(root=root, **data)

    @classmethod
    def model_validate(cls, obj: Any, **options: Any) -> "RootModel":
        if isinstance(obj, cls):
            return obj
        if isinstance(obj, dict) and set(obj) == {"root"}:
            return cls(root=obj["root"], **_engine_options(options))
        return cls(root=obj, **_engine_options(options))

    @classmethod
    def __class_getitem__(cls, item: Any) -> type["RootModel"]:
        item_name = getattr(item, "__name__", str(item).replace("typing.", ""))
        return type(
            f"RootModel[{item_name}]",
            (cls,),
            {"__annotations__": {"root": item}, "__module__": cls.__module__},
        )

    def model_dump(self, **options: Any) -> Any:
        from .serialization import serialize_value

        mode = options.pop("mode", "python")
        return serialize_value(self.root, mode=mode, **options)


def _engine_options(options: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    if options.get("strict") is not None:
        result["__tigrbl_strict__"] = bool(options["strict"])
    if options.get("extra") is not None:
        result["__tigrbl_extra__"] = options["extra"]
    return result


__all__ = ["RootModel"]
