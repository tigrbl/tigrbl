import pytest

from tigrbl import TigrblApp
from tigrbl_concrete._concrete import _app as concrete_app_module


@pytest.mark.unit
def test_add_event_handler_registers_startup_handler() -> None:
    app = TigrblApp()

    def handler() -> None:
        return None

    app.add_event_handler("startup", handler)

    assert app.event_handlers["startup"] == [handler]


@pytest.mark.unit
def test_on_event_decorator_registers_shutdown_handler() -> None:
    app = TigrblApp()

    @app.on_event("shutdown")
    def handler() -> None:
        return None

    assert app.event_handlers["shutdown"] == [handler]


@pytest.mark.asyncio
async def test_run_event_handlers_executes_sync_and_async_handlers() -> None:
    app = TigrblApp()
    calls: list[str] = []

    def sync_handler() -> None:
        calls.append("sync")

    async def async_handler() -> None:
        calls.append("async")

    app.add_event_handler("startup", sync_handler)
    app.add_event_handler("startup", async_handler)

    await app.run_event_handlers("startup")

    assert calls == ["sync", "async"]


@pytest.mark.unit
def test_add_event_handler_rejects_unsupported_event_type() -> None:
    app = TigrblApp()

    with pytest.raises(ValueError, match="Unsupported event type"):
        app.add_event_handler("deploy", lambda: None)


@pytest.mark.asyncio
async def test_lifespan_startup_runs_boot_warmup_after_startup_handlers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = TigrblApp()
    warmup_calls: list[bool] = []
    sent: list[str] = []
    messages = iter(
        (
            {"type": "lifespan.startup"},
            {"type": "lifespan.shutdown"},
        )
    )

    def _warmup() -> None:
        warmup_calls.append(True)

    async def _receive() -> dict[str, str]:
        return next(messages)

    async def _send(message: dict[str, str]) -> None:
        sent.append(message["type"])

    @app.on_event("startup")
    def _startup_handler() -> None:
        app.add_route("/boot-warmup", lambda: {"ok": True}, methods=["GET"])

    monkeypatch.setattr(concrete_app_module._resolver, "warmup", _warmup)

    await app._handle_lifespan({"type": "lifespan"}, _receive, _send)

    cache_key, _plan, _packed_plan = app._runtime_compile_cache
    assert cache_key[1] == app._runtime_plan_revision
    assert app._runtime_plan_revision > 0
    assert app._runtime_boot_warm_revision == app._runtime_plan_revision
    assert warmup_calls == [True]
    assert sent == [
        "lifespan.startup.complete",
        "lifespan.shutdown.complete",
    ]
