from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
import re
import warnings

_REMOVAL_VERSION = (0, 13, 0)


def _dist_version_tuple() -> tuple[int, int, int] | None:
    try:
        raw = version("tigrbl")
    except PackageNotFoundError:
        return None
    parts = re.split(r"[.+-]", raw, maxsplit=1)[0].split(".")
    numbers = []
    for item in parts[:3]:
        try:
            numbers.append(int(item))
        except ValueError:
            numbers.append(0)
    while len(numbers) < 3:
        numbers.append(0)
    return tuple(numbers)  # type: ignore[return-value]


def warn_legacy_engine_session_name(old: str, new: str) -> None:
    installed = _dist_version_tuple()
    if installed is not None and installed > _REMOVAL_VERSION:
        raise RuntimeError(
            f"{old} was removed after tigrbl 0.13.0; use {new} instead."
        )
    warnings.warn(
        f"{old} is deprecated and will fail after tigrbl 0.13.0; use {new} instead.",
        DeprecationWarning,
        stacklevel=3,
    )


__all__ = ["warn_legacy_engine_session_name"]
