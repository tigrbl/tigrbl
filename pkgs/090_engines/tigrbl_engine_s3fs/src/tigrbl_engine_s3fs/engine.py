from __future__ import annotations

from dataclasses import dataclass
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


@dataclass
class S3FSEngine(EngineBase):
    fs: Any
    bucket: str
    prefix: str = ""
    cas_enabled: bool = False
    cas_prefix: str = ".cas/sha256"
    verify_cas: bool = True
    spec: Any = None

    def __post_init__(self) -> None:
        self.bucket = _clean_fragment(self.bucket, name="bucket")
        self.prefix = _clean_fragment(self.prefix, name="prefix", allow_empty=True)
        self.cas_prefix = _clean_fragment(self.cas_prefix, name="cas_prefix")

    def object_path(self, key: str) -> str:
        clean = _clean_fragment(key, name="key")
        return "/".join(part for part in (self.bucket, self.prefix, clean) if part)

    def cas_path(self, address: str) -> str:
        self._require_cas()
        digest = _digest_from_address(address)
        return self.object_path(f"{self.cas_prefix}/{digest[:2]}/{digest[2:]}")

    def put_path(self, path: str, data: bytes) -> None:
        with self.fs.open(path, "wb") as stream:
            stream.write(data)

    def get_path(self, path: str) -> bytes:
        with self.fs.open(path, "rb") as stream:
            return bytes(stream.read())

    def delete_path(self, path: str) -> bool:
        if not self.fs.exists(path):
            return False
        self.fs.rm(path)
        return True

    def path_exists(self, path: str) -> bool:
        return bool(self.fs.exists(path))

    def head_path(self, path: str) -> dict[str, Any]:
        return dict(self.fs.info(path))

    def list_paths(self, logical_prefix: str = "") -> list[str]:
        base = "/".join(part for part in (self.bucket, self.prefix) if part)
        target = base
        if logical_prefix:
            target = self.object_path(logical_prefix)
        try:
            found = self.fs.find(target, detail=False)
        except FileNotFoundError:
            return []
        marker = f"{base}/"
        return sorted(
            path[len(marker) :]
            for path in found
            if isinstance(path, str) and path.startswith(marker)
        )

    def cas_address(self, data: bytes) -> str:
        self._require_cas()
        return _content_address(data)

    def to_provider(self) -> "S3FSEngine":
        return self

    async def _executeloop_impl(self, statements: Any) -> Any:
        del statements
        raise TypeError("s3fs object engines do not execute SQL statements")

    async def _executemany_impl(self, stmt: Any, parameter_sets: Any) -> Any:
        del stmt, parameter_sets
        raise TypeError("s3fs object engines do not execute SQL statements")

    def verify_cas_payload(self, address: str, data: bytes) -> None:
        if self.verify_cas and _content_address(data) != address.lower():
            raise ValueError(f"CAS integrity check failed for {address}")

    def _require_cas(self) -> None:
        if not self.cas_enabled:
            raise RuntimeError("content-addressed storage is not enabled")


def s3fs_engine(
    *, mapping: dict[str, Any] | None = None, spec: Any = None, **_: Any
) -> tuple[S3FSEngine, Callable[..., Any]]:
    config = dict(mapping or {})
    bucket = config.get("bucket")
    if not isinstance(bucket, str) or not bucket:
        raise TypeError("mapping['bucket'] must be a non-empty string")

    fs = config.get("fs")
    if fs is None:
        try:
            import s3fs
        except ImportError as exc:  # pragma: no cover - packaging guard
            raise RuntimeError(
                "s3fs is required; install the tigrbl_engine_s3fs package"
            ) from exc
        storage_options = dict(config.get("storage_options") or {})
        for source, target in (
            ("anon", "anon"),
            ("key", "key"),
            ("secret", "secret"),
            ("token", "token"),
            ("use_ssl", "use_ssl"),
        ):
            if source in config:
                storage_options[target] = config[source]
        client_kwargs = dict(storage_options.get("client_kwargs") or {})
        if config.get("endpoint_url") is not None:
            client_kwargs["endpoint_url"] = config["endpoint_url"]
        if config.get("region_name") is not None:
            client_kwargs["region_name"] = config["region_name"]
        if client_kwargs:
            storage_options["client_kwargs"] = client_kwargs
        fs = s3fs.S3FileSystem(**storage_options)

    engine = S3FSEngine(
        fs=fs,
        bucket=bucket,
        prefix=str(config.get("prefix") or ""),
        cas_enabled=bool(config.get("cas", False)),
        cas_prefix=str(config.get("cas_prefix") or ".cas/sha256"),
        verify_cas=bool(config.get("verify_cas", True)),
        spec=spec,
    )

    from .session import S3FSSession

    def session_factory(session_spec: Any = None) -> S3FSSession:
        return S3FSSession(engine, spec=session_spec)

    return engine, session_factory


def s3fs_capabilities() -> dict[str, object]:
    return {
        "engine": "s3fs",
        "object_storage": True,
        "s3_compatible": True,
        "filesystem_interface": True,
        "content_addressed_storage": "optional",
        "cas_algorithm": "sha256",
        "transactional": False,
        "staged_writes": True,
        "async_native": False,
        "read_only_enforced": True,
    }
