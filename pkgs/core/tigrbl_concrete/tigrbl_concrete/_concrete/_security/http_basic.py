"""HTTP basic authentication security scheme."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Any, Sequence

from tigrbl_runtime.runtime.status.exceptions import HTTPException
from tigrbl_runtime.runtime.status.mappings import status
from tigrbl_base._base._security_base import OpenAPISecurityDependency


@dataclass(frozen=True)
class HTTPBasicCredentials:
    username: str
    password: str


class HTTPBasic(OpenAPISecurityDependency):
    def __init__(
        self,
        auto_error: bool = True,
        *,
        scheme_name: str = "HTTPBasic",
        realm: str | None = None,
        description: str | None = None,
        scopes: Sequence[str] | None = None,
    ) -> None:
        payload: dict[str, Any] = {"type": "http", "scheme": "basic"}
        if description is not None:
            payload["description"] = description
        super().__init__(
            scheme_name=scheme_name,
            scheme=payload,
            scopes=scopes,
            auto_error=auto_error,
        )
        self.realm = realm

    def _challenge_value(self) -> str:
        if self.realm:
            return f'Basic realm="{self.realm}"'
        return "Basic"

    def _unauthorized(self, detail: str = "Unauthorized") -> None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": self._challenge_value()},
        )

    def __call__(self, request: Any) -> HTTPBasicCredentials | None:
        header = request.headers.get("authorization")
        if not header:
            if self.auto_error:
                self._unauthorized()
            return None

        try:
            incoming_scheme, credentials = header.split(" ", 1)
        except ValueError:
            if self.auto_error:
                self._unauthorized()
            return None

        if incoming_scheme.lower() != "basic":
            if self.auto_error:
                self._unauthorized()
            return None

        try:
            decoded = base64.b64decode(credentials.strip(), validate=True).decode("utf-8")
            username, password = decoded.split(":", 1)
        except Exception:
            if self.auto_error:
                self._unauthorized()
            return None

        return HTTPBasicCredentials(username=username, password=password)
