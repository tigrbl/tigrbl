from __future__ import annotations

from tigrbl import TigrblApp, TigrblRouter


app = TigrblApp(title="Phase 8 CLI App", version="8.0.0", mount_system=False)
router = TigrblRouter()


@router.get("/ping")
def ping() -> dict[str, bool]:
    return {"ok": True}


@router.websocket("/ws/echo")
async def echo_socket(ws) -> None:
    await ws.accept()
    await ws.close()


app.include_router(router)


def build_app() -> TigrblApp:
    return app

