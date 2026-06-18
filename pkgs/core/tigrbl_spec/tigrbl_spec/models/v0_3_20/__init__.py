from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar
from typing_extensions import Self

from tigrbl_spec.schema import CURRENT_SCHEMA_VERSION, identity_fields, spec_kinds, validate_payload


@dataclass(slots=True)
class SpecDataclass:
    spec_kind: str
    spec_schema_version: str
    spec_type: str
    data: dict[str, Any] = field(default_factory=dict)

    KIND: ClassVar[str]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Self:
        validated = validate_payload(cls.KIND, payload, CURRENT_SCHEMA_VERSION)
        identity = identity_fields(cls.KIND, CURRENT_SCHEMA_VERSION)
        data = {key: value for key, value in validated.items() if key not in identity}
        return cls(data=data, **identity)

    def to_dict(self) -> dict[str, Any]:
        return {
            "spec_kind": self.spec_kind,
            "spec_schema_version": self.spec_schema_version,
            "spec_type": self.spec_type,
            **self.data,
        }


def _model_class(kind: str) -> type[SpecDataclass]:
    return dataclass(slots=True)(
        type(kind, (SpecDataclass,), {"KIND": kind, "__annotations__": {"KIND": ClassVar[str]}})
    )


for _kind in spec_kinds(CURRENT_SCHEMA_VERSION):
    globals()[_kind] = _model_class(_kind)


__all__ = ["SpecDataclass", *spec_kinds(CURRENT_SCHEMA_VERSION)]
