from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

_BOUNDARY_EVENTS: list[dict[str, Any]] = []
_SEQ = 0


def _record(event: str, **payload: Any) -> dict[str, Any]:
    global _SEQ
    item = {"seq": _SEQ, "event": event, **payload}
    _BOUNDARY_EVENTS.append(item)
    _SEQ += 1
    return item


def ffi_boundary_events() -> list[dict[str, Any]]:
    return [dict(item) for item in _BOUNDARY_EVENTS]


def clear_ffi_boundary_events() -> None:
    _BOUNDARY_EVENTS.clear()


def native_available() -> bool:
    return True


def compiled_extension_available() -> bool:
    return False


def normalize_spec(spec_json: str) -> str:
    trimmed = str(spec_json or "").strip()
    if not trimmed:
        raise RuntimeError("empty spec payload")
    _record("normalize_spec", size=len(trimmed))
    return trimmed


def compile_spec(spec_json: str) -> str:
    normalized = normalize_spec(spec_json)
    _record("compile_spec", size=len(normalized))
    return f"compiled-spec:{len(normalized)}"


@dataclass(slots=True)
class RuntimeHandle:
    spec_json: str
    description_text: str = field(init=False)

    def __post_init__(self) -> None:
        normalized = normalize_spec(self.spec_json)
        self.description_text = (
            f"runtime handle for normalized spec of {len(normalized)} byte(s)"
        )
        _record("create_runtime_handle", size=len(normalized))

    def describe(self) -> str:
        return self.description_text

    def begin_request(self, transport: str = "rest") -> None:
        _record("request_entry", transport=transport)

    def callback_fence(self, kind: str, name: str) -> None:
        _record("callback_fence_enter", kind=kind, name=name)
        _record("callback_fence_exit", kind=kind, name=name)

    def finish_response(self, transport: str = "rest") -> None:
        _record("response_exit", transport=transport)

    def ffi_events(self) -> list[dict[str, Any]]:
        return ffi_boundary_events()


def create_runtime_handle(spec_json: str) -> RuntimeHandle:
    return RuntimeHandle(spec_json)


def _descriptor(kind: str, name: str) -> str:
    return f"{kind}:{name}"


def register_python_callback(name: str) -> str:
    _record("register_python_callback", name=name)
    return _descriptor("python-callback", name)


def register_python_atom(name: str) -> str:
    _record("register_python_atom", name=name)
    return _descriptor("python-atom", name)


def register_python_hook(name: str) -> str:
    _record("register_python_hook", name=name)
    return _descriptor("python-hook", name)


def register_python_handler(name: str) -> str:
    _record("register_python_handler", name=name)
    return _descriptor("python-handler", name)


def register_python_engine(name: str) -> str:
    _record("register_python_engine", name=name)
    return _descriptor("python-engine", name)
