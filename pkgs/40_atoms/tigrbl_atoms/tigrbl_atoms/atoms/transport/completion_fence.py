from __future__ import annotations

from collections.abc import Awaitable, Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
import logging
from typing import Any

from .asgi_channel import complete_channel_state


ACK_VALUES = {"ack", "sent", "complete", "completed"}


def _completion_name(subevent: str) -> str:
    return subevent if subevent.endswith("_complete") else f"{subevent}_complete"


async def emit_with_fence(
    event: dict[str, Any],
    *,
    send: Callable[[dict[str, Any]], Awaitable[Any]],
    trace: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    subevent = str(event.get("subevent", "message.emit"))
    completed_subevent = _completion_name(subevent)
    result: dict[str, Any] = {
        "completion_fence": "POST_EMIT",
        "completed": False,
        "completed_subevent": completed_subevent,
    }
    try:
        send_result = await send(event)
    except Exception as exc:
        result["error_ctx"] = {"subevent": subevent, "message": str(exc)}
        return result

    values = send_result if isinstance(send_result, tuple) else (send_result,)
    if any(value in ACK_VALUES for value in values):
        if trace is not None:
            trace(completed_subevent)
        result["completed"] = True
    return result


_HTTP_ACTIONS = "_tigrbl_after_http_emit"
_LOG = logging.getLogger(__name__)


@dataclass
class HttpCompletion:
    """Observation of the original response at the ASGI send boundary."""

    status: int | None = None
    expects_trailers: bool = False
    body_sent: bool = False
    emitted: bool = False
    failed: bool = False

    def observe(self, message: dict[str, Any]) -> None:
        if self.failed or self.emitted:
            return
        match_type = message.get("type")
        if match_type == "http.response.start":
            self.status = message["status"]
            self.expects_trailers = bool(message.get("trailers"))
        elif self.status is not None and match_type == "http.response.body":
            if not message.get("more_body", False):
                self.body_sent = True
                self.emitted = not self.expects_trailers
        elif (
            match_type == "http.response.trailers"
            and self.expects_trailers
            and self.body_sent
        ):
            self.emitted = not message.get("more_trailers", False)


@contextmanager
def observe_http_completion(env: Any) -> Iterator[HttpCompletion | None]:
    """Observe accepted ASGI sends for one HTTP invocation."""
    scope = getattr(env, "scope", None)
    if not isinstance(scope, dict) or scope.get("type") != "http":
        yield None
        return

    state = scope.setdefault("state", {})
    send = getattr(env, "send", None)
    if state.get("_tigrbl_rpc_batch_item") is not None or not callable(send):
        # Batch item responses are captured in memory. The outer response owns the fence.
        yield None
        return
    state.setdefault(_HTTP_ACTIONS, [])
    completion = HttpCompletion()

    async def observed_send(message: dict[str, Any]) -> None:
        try:
            await send(message)
        except BaseException:
            if not completion.emitted:
                completion.failed = True
            raise
        completion.observe(message)

    env.send = observed_send
    try:
        yield completion
    finally:
        env.send = send


def defer_http_completion(
    scope: dict[str, Any], action: Callable[[HttpCompletion], Awaitable[Any]]
) -> None:
    if scope.get("type") != "http":
        raise ValueError("Callback after_emit requires an HTTP response")
    scope.setdefault("state", {}).setdefault(_HTTP_ACTIONS, []).append(action)


async def finish_http_completion(
    scope: dict[str, Any], ctx: Any, completion: HttpCompletion
) -> None:
    ctx["transport_completed"] = completion.emitted
    if completion.emitted:
        ctx["current_phase"] = "POST_EMIT"
        channel = ctx.get("channel")
        if isinstance(getattr(channel, "state", None), dict):
            complete_channel_state(channel.state)
    for action in scope.get("state", {}).pop(_HTTP_ACTIONS, ()):
        try:
            await action(completion)
        except Exception as exc:
            _LOG.error("HTTP completion action failed: %s", type(exc).__name__)


__all__ = [
    "ACK_VALUES",
    "HttpCompletion",
    "defer_http_completion",
    "emit_with_fence",
    "finish_http_completion",
    "observe_http_completion",
]
