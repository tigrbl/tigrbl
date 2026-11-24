"""Transport-independent authorization declaration for a bound operation."""

from dataclasses import dataclass
import re
from typing import Literal

from .serde import SerdeMixin


@dataclass(frozen=True)
class OperationSecurity(SerdeMixin):
    action_id: str
    resource_type: str
    access: Literal["protected", "public"] = "protected"

    def __post_init__(self) -> None:
        if not re.fullmatch(r"[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*){2,}", self.action_id):
            raise ValueError("action_id must be namespaced: application.resource.operation")
        if not self.resource_type or self.resource_type != self.resource_type.strip():
            raise ValueError("resource_type is required")
        if self.access not in ("protected", "public"):
            raise ValueError("operation access must be protected or public")
