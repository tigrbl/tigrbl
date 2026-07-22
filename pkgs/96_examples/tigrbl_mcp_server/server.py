from __future__ import annotations

import argparse
import asyncio

from tigrbl.factories.engine import mem

from app import NOTE_MCP
from tigrbl_mcp import TigrblMCP


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--transport",
        choices=("stdio", "streamable-http"),
        default="stdio",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    service = asyncio.run(TigrblMCP.make(NOTE_MCP, engine=mem(async_=False)))
    service.provide().run(transport=args.transport)


if __name__ == "__main__":
    main()
