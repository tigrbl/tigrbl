from __future__ import annotations

from tigrbl.engine.registry import register_engine

from .rate import RateLimiter
from .session import RateSession, AsyncRateSession


def register() -> None:
    register_engine(kind="memrate", build=build_memrate, capabilities=capabilities)


def capabilities() -> dict:
    return {
        "engine": "memrate",
        "transactional": False,
        "async_native": True,
        "persistence": "process",
        "features": {"token_bucket", "reserve"},
    }


def build_memrate(*, mapping=None, spec=None, dsn=None, **_) -> tuple[object, object]:
    mapping = dict(mapping or {})
    async_ = bool(getattr(spec, "async_", False))

    rate_per_s = float(mapping.get("rate_per_s", 10.0))
    burst = float(mapping.get("burst", max(1.0, rate_per_s)))
    shards = int(mapping.get("shards", 64))
    namespace = str(mapping.get("namespace", "default"))

    engine = RateLimiter(
        rate_per_s=rate_per_s,
        burst=burst,
        shards=shards,
        namespace=namespace,
    )

    if async_:
        def sessionmaker():
            return AsyncRateSession(engine)
    else:
        def sessionmaker():
            return RateSession(engine)

    return engine, sessionmaker
