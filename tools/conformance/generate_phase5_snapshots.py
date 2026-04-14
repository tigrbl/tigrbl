from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for rel in [
    'pkgs/core/tigrbl',
    'pkgs/core/tigrbl_atoms',
    'pkgs/core/tigrbl_base',
    'pkgs/core/tigrbl_canon',
    'pkgs/core/tigrbl_client',
    'pkgs/core/tigrbl_concrete',
    'pkgs/core/tigrbl_core',
    'pkgs/core/tigrbl_kernel',
    'pkgs/core/tigrbl_ops_olap',
    'pkgs/core/tigrbl_ops_oltp',
    'pkgs/core/tigrbl_orm',
    'pkgs/core/tigrbl_runtime',
    'pkgs/core/tigrbl_spec',
    'pkgs/core/tigrbl_typing',
]:
    sys.path.insert(0, str(ROOT / rel))

from httpx import ASGITransport, AsyncClient  # noqa: E402
from pydantic import BaseModel  # noqa: E402
from sqlalchemy import Column, String  # noqa: E402

from tigrbl import (  # noqa: E402
    APIKey,
    HTTPBasic,
    HTTPBearer,
    MutualTLS,
    OAuth2,
    OpenIdConnect,
    TigrblApp,
    TigrblRouter,
)
from tigrbl._spec import OpSpec  # noqa: E402
from tigrbl.orm.mixins import GUIDPk  # noqa: E402
from tigrbl.orm.tables import TableBase  # noqa: E402
from tigrbl.security import Security  # noqa: E402
from tigrbl.shortcuts.engine import mem  # noqa: E402

SNAPSHOT_DIR = (
    ROOT
    / 'docs'
    / 'conformance'
    / 'audit'
    / '2026'
    / 'phase5-oas-jsonschema-jsonrpc-openrpc-closure'
    / 'snapshots'
)


def _basic_dep(cred=Security(HTTPBasic(scheme_name='BasicAuth'))):
    return cred


def _bearer_dep(cred=Security(HTTPBearer(scheme_name='BearerAuth'))):
    return cred


def _api_key_dep(cred=Security(APIKey(scheme_name='ApiKeyAuth', name='X-API-Key'))):
    return cred


def _oauth2_dep(
    cred=Security(
        OAuth2(
            scheme_name='OAuth2Auth',
            flows={'clientCredentials': {'tokenUrl': 'https://issuer.example/token'}},
        )
    ),
):
    return cred


def _openid_dep(
    cred=Security(
        OpenIdConnect(
            scheme_name='OpenIdAuth',
            openid_connect_url='https://issuer.example/.well-known/openid-configuration',
        )
    ),
):
    return cred


def _mtls_dep(cred=Security(MutualTLS(scheme_name='MutualTLSAuth'))):
    return cred


class Phase5CreateWidget(BaseModel):
    name: str


class Phase5WidgetOut(BaseModel):
    id: str
    name: str


class Phase5BasicDocsTable(TableBase, GUIDPk):
    __tablename__ = 'phase5_basic_docs_table'
    name = Column(String, nullable=False)
    __tigrbl_ops__ = (OpSpec(alias='read', target='read', secdeps=(_basic_dep,)),)


class Phase5BearerDocsTable(TableBase, GUIDPk):
    __tablename__ = 'phase5_bearer_docs_table'
    name = Column(String, nullable=False)
    __tigrbl_ops__ = (OpSpec(alias='read', target='read', secdeps=(_bearer_dep,)),)


class Phase5RouterDocsTable(TableBase, GUIDPk):
    __tablename__ = 'phase5_router_docs_table'
    name = Column(String, nullable=False)
    __tigrbl_ops__ = (OpSpec(alias='read', target='read', secdeps=(_api_key_dep,)),)


class Phase5TableDocsTable(TableBase, GUIDPk):
    __tablename__ = 'phase5_table_docs_table'
    name = Column(String, nullable=False)
    __tigrbl_ops__ = (
        OpSpec(
            alias='read',
            target='read',
            secdeps=(_oauth2_dep, _openid_dep, _mtls_dep),
        ),
    )


def build_snapshot_app() -> TigrblApp:
    router = TigrblRouter(title='Phase 5 Router', version='5.0.0', engine=mem(async_=False))

    @router.post(
        '/widgets/{widget_id}',
        tags=['widgets'],
        summary='Create widget',
        description='Create or update a widget',
        request_model=Phase5CreateWidget,
        response_model=Phase5WidgetOut,
        path_param_schemas={'widget_id': {'type': 'string'}},
        query_param_schemas={'verbose': {'type': 'boolean', 'required': False}},
    )
    def create(widget_id: str):
        return {'id': widget_id, 'name': widget_id}

    router.include_table(Phase5BasicDocsTable)
    router.include_table(Phase5RouterDocsTable)
    router.include_table(Phase5TableDocsTable)

    app = TigrblApp(title='Phase 5 API', version='5.0.0', engine=mem(async_=False))
    app.include_table(Phase5BearerDocsTable)
    app.include_router(router)
    app.initialize()
    app.mount_jsonrpc()
    app.mount_openrpc()
    return app


async def main() -> None:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    app = build_snapshot_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as client:
        openapi_doc = (await client.get('/openapi.json')).json()
        openrpc_doc = (await client.get('/openrpc.json')).json()
        swagger_html = (await client.get('/docs')).text
        lens_html = (await client.get('/lens')).text

    (SNAPSHOT_DIR / 'openapi_snapshot.json').write_text(
        json.dumps(openapi_doc, indent=2, sort_keys=True) + '\n',
        encoding='utf-8',
    )
    (SNAPSHOT_DIR / 'openrpc_snapshot.json').write_text(
        json.dumps(openrpc_doc, indent=2, sort_keys=True) + '\n',
        encoding='utf-8',
    )
    (SNAPSHOT_DIR / 'swagger_snapshot.html').write_text(swagger_html, encoding='utf-8')
    (SNAPSHOT_DIR / 'lens_snapshot.html').write_text(lens_html, encoding='utf-8')
    print(f'Wrote Phase 5 snapshots to {SNAPSHOT_DIR.relative_to(ROOT)}')


if __name__ == '__main__':
    asyncio.run(main())
