from __future__ import annotations


def compile_lifespan_chain(*, event: str) -> dict[str, object]:
    if event not in {"startup", "shutdown"}:
        raise ValueError("lifespan event must be startup or shutdown")
    state_atom = "state.ready.set" if event == "startup" else "state.ready.clear"
    return {
        "owner": "kernelplan",
        "event": event,
        "subevent": f"lifespan.{event}",
        "atoms": (
            "lifespan.receive",
            "lifespan.run_handlers",
            state_atom,
            "lifespan.complete",
        ),
    }


__all__ = ["compile_lifespan_chain"]
