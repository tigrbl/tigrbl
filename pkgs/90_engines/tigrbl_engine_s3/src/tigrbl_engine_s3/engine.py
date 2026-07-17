from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from pathlib import PurePosixPath
from typing import Any, Callable

from tigrbl_base._base import EngineBase


def _clean_fragment(value: str, *, name: str, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")
    if value.startswith("/") or "//" in value:
        raise ValueError(f"{name} must be relative and contain no empty segments")
    candidate = value.strip("/")
    if not candidate:
        if allow_empty:
            return ""
        raise ValueError(f"{name} must not be empty")
    if "\\" in candidate:
        raise ValueError(f"{name} must use POSIX separators")
    parts = PurePosixPath(candidate).parts
    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError(f"{name} must not contain empty or traversal segments")
    return "/".join(parts)


def _content_address(data: bytes) -> str:
    return f"sha256:{sha256(data).hexdigest()}"


def _digest_from_address(address: str) -> str:
    if not isinstance(address, str) or not address.startswith("sha256:"):
        raise ValueError("CAS address must use the sha256:<hex> form")
    digest = address.removeprefix("sha256:").lower()
    if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
        raise ValueError("CAS address must contain a 64-character SHA-256 digest")
    return digest


def _is_missing(exc: Exception) -> bool:
    response = getattr(exc, "response", None)
    if isinstance(response, dict):
        code = str(response.get("Error", {}).get("Code", ""))
        return code in {"404", "NoSuchKey", "NotFound"}
    return isinstance(exc, (FileNotFoundError, KeyError))


@dataclass
class S3Engine(EngineBase):
    client: Any
    bucket: str
    prefix: str = ""
    cas_enabled: bool = False
    cas_prefix: str = ".cas/sha256"
    verify_cas: bool = True
    put_options: dict[str, Any] = field(default_factory=dict)
    spec: Any = None

    def __post_init__(self) -> None:
        self.bucket = _clean_fragment(self.bucket, name="bucket")
        self.prefix = _clean_fragment(self.prefix, name="prefix", allow_empty=True)
        self.cas_prefix = _clean_fragment(self.cas_prefix, name="cas_prefix")

    def object_key(self, key: str) -> str:
        clean = _clean_fragment(key, name="key")
        return "/".join(part for part in (self.prefix, clean) if part)

    def cas_key(self, address: str) -> str:
        self._require_cas()
        digest = _digest_from_address(address)
        return self.object_key(f"{self.cas_prefix}/{digest[:2]}/{digest[2:]}")

    def put_key(self, key: str, data: bytes) -> None:
        self.client.put_object(
            Bucket=self.bucket, Key=key, Body=data, **self.put_options
        )

    def get_key(self, key: str) -> bytes:
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
        except Exception as exc:
            if _is_missing(exc):
                raise FileNotFoundError(key) from exc
            raise
        body = response["Body"]
        return bytes(body.read() if hasattr(body, "read") else body)

    def delete_key(self, key: str) -> bool:
        self.client.delete_object(Bucket=self.bucket, Key=key)
        return True

    def key_exists(self, key: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except Exception as exc:
            if _is_missing(exc):
                return False
            raise

    def head_key(self, key: str) -> dict[str, Any]:
        try:
            return dict(self.client.head_object(Bucket=self.bucket, Key=key))
        except Exception as exc:
            if _is_missing(exc):
                raise FileNotFoundError(key) from exc
            raise

    def list_keys(self, logical_prefix: str = "") -> list[str]:
        request_prefix = f"{self.prefix}/" if self.prefix else ""
        if logical_prefix:
            request_prefix = self.object_key(logical_prefix)
        kwargs: dict[str, Any] = {"Bucket": self.bucket, "Prefix": request_prefix}
        found: list[str] = []
        while True:
            response = self.client.list_objects_v2(**kwargs)
            found.extend(
                str(row["Key"]) for row in response.get("Contents", []) if "Key" in row
            )
            token = response.get("NextContinuationToken")
            if not response.get("IsTruncated") or not token:
                break
            kwargs["ContinuationToken"] = token
        marker = f"{self.prefix}/" if self.prefix else ""
        return sorted(
            key[len(marker) :] if marker and key.startswith(marker) else key
            for key in found
        )

    def cas_address(self, data: bytes) -> str:
        self._require_cas()
        return _content_address(data)

    def to_provider(self) -> "S3Engine":
        return self

    async def _executeloop_impl(self, statements: Any) -> Any:
        del statements
        raise TypeError("S3 object engines do not execute SQL statements")

    async def _executemany_impl(self, stmt: Any, parameter_sets: Any) -> Any:
        del stmt, parameter_sets
        raise TypeError("S3 object engines do not execute SQL statements")

    def verify_cas_payload(self, address: str, data: bytes) -> None:
        if self.verify_cas and _content_address(data) != address.lower():
            raise ValueError(f"CAS integrity check failed for {address}")

    def _require_cas(self) -> None:
        if not self.cas_enabled:
            raise RuntimeError("content-addressed storage is not enabled")


def s3_engine(
    *, mapping: dict[str, Any] | None = None, spec: Any = None, **_: Any
) -> tuple[S3Engine, Callable[..., Any]]:
    config = dict(mapping or {})
    bucket = config.get("bucket")
    if not isinstance(bucket, str) or not bucket:
        raise TypeError("mapping['bucket'] must be a non-empty string")

    client = config.get("client")
    if client is None:
        try:
            import boto3
        except ImportError as exc:  # pragma: no cover - packaging guard
            raise RuntimeError(
                "boto3 is required; install the tigrbl_engine_s3 package"
            ) from exc
        session_kwargs: dict[str, Any] = {}
        if config.get("profile_name") is not None:
            session_kwargs["profile_name"] = config["profile_name"]
        session = boto3.Session(**session_kwargs)
        client_kwargs: dict[str, Any] = {}
        for source, target in (
            ("region_name", "region_name"),
            ("endpoint_url", "endpoint_url"),
            ("use_ssl", "use_ssl"),
            ("verify", "verify"),
            ("access_key", "aws_access_key_id"),
            ("secret_key", "aws_secret_access_key"),
            ("session_token", "aws_session_token"),
        ):
            if source in config:
                client_kwargs[target] = config[source]
        client = session.client("s3", **client_kwargs)

    engine = S3Engine(
        client=client,
        bucket=bucket,
        prefix=str(config.get("prefix") or ""),
        cas_enabled=bool(config.get("cas", False)),
        cas_prefix=str(config.get("cas_prefix") or ".cas/sha256"),
        verify_cas=bool(config.get("verify_cas", True)),
        put_options=dict(config.get("put_options") or {}),
        spec=spec,
    )

    from .session import S3Session

    def session_factory(session_spec: Any = None) -> S3Session:
        return S3Session(engine, spec=session_spec)

    return engine, session_factory


def s3_capabilities() -> dict[str, object]:
    return {
        "engine": "s3",
        "object_storage": True,
        "s3_compatible": True,
        "direct_s3_api": True,
        "content_addressed_storage": "optional",
        "cas_algorithm": "sha256",
        "transactional": False,
        "staged_writes": True,
        "async_native": False,
        "read_only_enforced": True,
    }
