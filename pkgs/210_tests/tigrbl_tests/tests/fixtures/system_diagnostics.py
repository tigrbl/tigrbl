from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any

from sqlalchemy import Column, String

from tigrbl import Request, TigrblApp
from tigrbl.factories.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import TableBase
from tigrbl.system.diagnostics import mount_diagnostics


class SystemDiagnosticsFixtureWidget(TableBase, GUIDPk):
    __tablename__ = "system_diagnostics_fixture_widgets"

    name = Column(String, nullable=False)


class UnavailableDiagnosticsDb:
    def execute(self, *_args: Any, **_kwargs: Any) -> None:
        raise RuntimeError("fixture database unavailable")


class AvailableDiagnosticsDb:
    def execute(self, *_args: Any, **_kwargs: Any) -> None:
        return None


@dataclass(frozen=True)
class SystemDiagnosticsFixture:
    app: TigrblApp
    healthz_path: str
    absent_default_path: str
    expected_healthz_payload: dict[str, bool]
    warning_vocabulary: frozenset[str]

    def request(
        self,
        path: str | None = None,
        *,
        db: Any | None = None,
        dbs: dict[str, Any] | None = None,
        query: dict[str, list[str]] | None = None,
    ) -> Request:
        state = SimpleNamespace()
        if db is not None:
            state.db = db
        if dbs is not None:
            state.dbs = dbs
        return Request(
            method="GET",
            path=path or self.healthz_path,
            headers={},
            query=query or {},
            path_params={},
            body=b"",
            state=state,
        )

    def available_db_request(self) -> Request:
        return self.request(db=AvailableDiagnosticsDb())

    def unavailable_db_request(self) -> Request:
        return self.request(db=UnavailableDiagnosticsDb())

    def multi_db_request(self, *, detail: str | None = None) -> Request:
        query = {"dbs": [detail]} if detail is not None else {}
        return self.request(
            dbs={
                "primary": AvailableDiagnosticsDb(),
                "analytics": AvailableDiagnosticsDb(),
                "archive": UnavailableDiagnosticsDb(),
            },
            query=query,
        )

    def no_db_warning_request(self) -> Request:
        return self.request(query={"warn_no_db": ["1"]})


def build_system_diagnostics_fixture(
    *,
    prefix: str = "/internal",
) -> SystemDiagnosticsFixture:
    app = TigrblApp(engine=mem(async_=False), mount_system=False)
    app.include_table(SystemDiagnosticsFixtureWidget)
    app.initialize()
    app.mount_jsonrpc()
    app.include_router(mount_diagnostics(app), prefix=prefix)

    return SystemDiagnosticsFixture(
        app=app,
        healthz_path=f"{prefix.rstrip('/')}/healthz",
        absent_default_path="/system/healthz",
        expected_healthz_payload={"ok": True},
        warning_vocabulary=frozenset({"db-not-configured", "db-unavailable"}),
    )
