"""Run the Tigrbl trace collector and serve its built frontend bundle."""

import argparse
import asyncio
import os
from pathlib import Path


async def serve_collector(args):
    from tigrcorn.config.load import build_config
    from tigrcorn.server.runner import TigrCornServer

    from .collector import build_collector, collector_gateway

    dsn = os.environ["TRACE_DATABASE_URL"]
    if not dsn.startswith("postgresql+psycopg://"):
        raise ValueError("TRACE_DATABASE_URL must use postgresql+psycopg://")
    from tigrbl_engine_postgres.plugin import register

    register()
    app = await build_collector({"kind": "postgres", "dsn": dsn, "async": False})
    gateway = collector_gateway(
        app,
        args.frontend,
        os.environ["TRACE_INGEST_TOKEN"],
        os.environ["TRACE_OPERATOR_USER"],
        os.environ["TRACE_OPERATOR_PASSWORD"],
    )
    server = TigrCornServer(
        gateway,
        build_config(
            host=args.host,
            port=args.port,
            lifespan="off",
            http_versions=["1.1"],
            protocols=["http1"],
        ),
    )
    await server.start()
    try:
        print(
            f"Tigrbl Trace Collector listening on {args.host}:{args.port}", flush=True
        )
        await asyncio.Event().wait()
    finally:
        await server.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frontend", type=Path, required=True)
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()
    for name in (
        "TRACE_DATABASE_URL",
        "TRACE_INGEST_TOKEN",
        "TRACE_OPERATOR_USER",
        "TRACE_OPERATOR_PASSWORD",
    ):
        if not os.environ.get(name):
            parser.error(f"{name} is required")
    if ":" in os.environ["TRACE_OPERATOR_USER"]:
        parser.error("TRACE_OPERATOR_USER cannot contain a colon")
    if not (args.frontend / "index.html").is_file():
        parser.error("Build the frontend and supply its bundle with --frontend.")
    try:
        asyncio.run(serve_collector(args))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
