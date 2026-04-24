"""HTTP bearer security scheme."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from tigrbl_runtime.runtime.status.exceptions import HTTPException
from tigrbl_runtime.runtime.status.mappings import status
from tigrbl_base._base._security_base import OpenAPISecurityDependency


@dataclass(frozen=True)
class HTTPAuthorizationCredentials:
    scheme: str
    credentials: str


class HTTPBearer(OpenAPISecurityDependency):
    def __init__(
        self,
        auto_error: bool = True,
        *,
        scheme_name: str = "HTTPBearer",
        scheme: str = "bearer",
        bearer_format: str | None = None,
        description: str | None = None,
        scopes: Sequence[str] | None = None,
        realm: str | None = None,
    ) -> None:
        payload: dict[str, Any] = {"type": "http", "scheme": scheme}
        if bearer_format is not None:
            payload["bearerFormat"] = bearer_format
        if description is not None:
            payload["description"] = description
        super().__init__(
            scheme_name=scheme_name,
            scheme=payload,
            scopes=scopes,
            auto_error=auto_error,
        )
        self.http_scheme = scheme
        self.realm = realm

    def _challenge_value(
        self,
        *,
        error: str | None = None,
        error_description: str | None = None,
    ) -> str:
        parts = ["Bearer"]
        if self.realm:
            parts.append(f'realm="{self.realm}"')
        if error:
            parts.append(f'error="{error}"')
        if error_description:
            parts.append(f'error_description="{error_description}"')
        return ", ".join(parts) if len(parts) > 1 else parts[0]

    def _unauthorized(
        self,
        *,
        error: str | None = None,
        error_description: str | None = None,
        detail: str = "Unauthorized",
    ) -> None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={
                "WWW-Authenticate": self._challenge_value(
                    error=error,
                    error_description=error_description,
                )
            },
        )

    def __call__(self, request: Any) -> HTTPAuthorizationCredentials | None:
        header = request.headers.get("authorization")
        if not header:
            if self.auto_error:
                self._unauthorized(detail="Not authenticated")
            return None

        try:
            incoming_scheme, credentials = header.split(" ", 1)
        except ValueError:
            if self.auto_error:
                self._unauthorized(error="invalid_request")
            return None

        if incoming_scheme.lower() != self.http_scheme.lower():
            if self.auto_error:
                self._unauthorized(error="invalid_request")
            return None

        credentials = credentials.strip()
        if not credentials:
            if self.auto_error:
                self._unauthorized(error="invalid_token")
            return None

        return HTTPAuthorizationCredentials(
            scheme=incoming_scheme,
            credentials=credentials,
        )
