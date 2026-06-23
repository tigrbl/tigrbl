from __future__ import annotations

import threading

from tigrbl import RestTable, TigrblApp
from tigrbl_equivalence_contracts.runtime import (
    RunningHttpServer,
    free_http_port,
    wait_for_http_server,
)
from tigrbl.types import Column, String
import uvicorn


class Widget(RestTable):
    __tablename__ = "widgets"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


app = TigrblApp(engine={"kind": "sqlite", "mode": "memory", "async": False})
app.include_table(Widget)
app.initialize()


def start_server() -> RunningHttpServer:
    """Start the Tigrbl ASGI app as a real local HTTP server."""

    port = free_http_port()
    server = uvicorn.Server(
        uvicorn.Config(
            app,
            host="127.0.0.1",
            port=port,
            lifespan="off",
            log_level="warning",
        )
    )
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{port}"
    wait_for_http_server(base_url)

    def stop() -> None:
        server.should_exit = True
        thread.join(timeout=10)

    return RunningHttpServer(base_url=base_url, stop=stop)
