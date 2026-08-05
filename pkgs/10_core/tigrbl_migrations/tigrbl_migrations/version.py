"""Manifest protocol version loading and strict semantic-version validation."""

from __future__ import annotations

import re
from importlib.resources import files
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10
    import tomli as tomllib

from .errors import ManifestError

_SEMVER = re.compile(
    r"^(?P<major>0|[1-9]\d*)\."
    r"(?P<minor>0|[1-9]\d*)\."
    r"(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+(?P<build>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)


def require_semver(value: str, *, field: str) -> str:
    if not isinstance(value, str) or _SEMVER.fullmatch(value) is None:
        raise ManifestError(f"{field} must be a semantic version: {value!r}")
    return value


def _load_manifest_version() -> str:
    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    try:
        if pyproject.is_file():
            data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
            value = data["tool"]["tigrbl"]["manifest"]["version"]
        else:
            resource = files("tigrbl_migrations").joinpath("manifest_protocol.toml")
            value = tomllib.loads(resource.read_text(encoding="utf-8"))["version"]
    except (OSError, KeyError, TypeError, tomllib.TOMLDecodeError) as exc:
        raise ManifestError("unable to load [tool.tigrbl.manifest].version") from exc
    return require_semver(value, field="manifest version")


MANIFEST_VERSION = _load_manifest_version()


def manifest_major(value: str) -> int:
    require_semver(value, field="manifest version")
    return int(value.split(".", 1)[0])


def require_supported_manifest_version(value: str) -> str:
    require_semver(value, field="manifest version")
    if manifest_major(value) != manifest_major(MANIFEST_VERSION):
        raise ManifestError(
            f"unsupported manifest version {value}; runtime supports {MANIFEST_VERSION}"
        )
    return value
