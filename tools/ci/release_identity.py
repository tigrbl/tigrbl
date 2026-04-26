from __future__ import annotations

import json
import re
from pathlib import Path

from common import repo_root

ROOT = repo_root()
CURRENT_TARGET = ROOT / "docs" / "conformance" / "CURRENT_TARGET.md"
REGISTRY = ROOT / ".ssot" / "registry.json"

_PROMOTION_SOURCE_RE = re.compile(r"promotion-source dev build:\s*`docs/conformance/dev/([^`/]+)/`")
_STABLE_RELEASE_RE = re.compile(r"promoted stable release:\s*`docs/conformance/releases/([^`/]+)/`")
_ACTIVE_DEV_RE = re.compile(r"active next-line dev bundle:\s*`docs/conformance/dev/([^`/]+)/`")
_SEMVER_RE = re.compile(r"^([0-9]+)\.([0-9]+)\.([0-9]+)(?:\.dev([0-9]+))?$")


def _current_target_text() -> str:
    return CURRENT_TARGET.read_text(encoding="utf-8")


def _registry_version() -> str:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    return str(registry.get("repo", {}).get("version", ""))


def _capture(pattern: re.Pattern[str], text: str, *, label: str) -> str:
    match = pattern.search(text)
    if match is None:
        raise ValueError(f"unable to derive {label} from docs/conformance/CURRENT_TARGET.md")
    return match.group(1)


def parse_semver(version: str, *, require_dev: bool = False) -> tuple[int, int, int, int, int]:
    match = _SEMVER_RE.fullmatch(version)
    if match is None:
        raise ValueError(f"{version!r} is not a semver-like version")
    major, minor, patch, dev = match.groups()
    if require_dev and dev is None:
        raise ValueError(f"{version!r} is not a dev checkpoint version")
    return int(major), int(minor), int(patch), 0 if dev is None else 1, int(dev or 0)


def promotion_source_dev_version() -> str:
    return _capture(_PROMOTION_SOURCE_RE, _current_target_text(), label="promotion-source dev build")


def current_stable_release_version() -> str:
    return _capture(_STABLE_RELEASE_RE, _current_target_text(), label="current stable release")


def active_governed_dev_version() -> str:
    text = _current_target_text()
    match = _ACTIVE_DEV_RE.search(text)
    if match is not None:
        return match.group(1)
    return _registry_version()


def current_stable_release_root() -> Path:
    return ROOT / "docs" / "conformance" / "releases" / current_stable_release_version()


def promotion_source_dev_root() -> Path:
    return ROOT / "docs" / "conformance" / "dev" / promotion_source_dev_version()


def previous_stable_version(version: str) -> str:
    major, minor, patch, *_ = parse_semver(version, require_dev=True)
    return f"{major}.{minor}.{max(patch - 1, 0)}"
