"""Contract row for the WebSocketJsonRpcTable table-class equivalence."""

from __future__ import annotations

from tigrbl_equivalence_contracts.contracts import CertifiableEquivalence, _impl, _lazy_attr

from .runtime import assert_equivalence


CONTRACT = CertifiableEquivalence(
    id="table-class.web-socket-json-rpc-table",
    category="table-class",
    intent="Author a Widget resource with Tigrbl WebSocketJsonRpcTable and compare its projected route surface to FastAPI and Flask.",
    status="analogous",
    claim="Tigrbl WebSocketJsonRpcTable, FastAPI routes, and Flask routes can expose the same Widget route surface for the table class.",
    source_documents=("docs/developer/AUTHORING_EQUIVALENCE.md", "docs/developer/ROUTER_TABLE_EQUIVALENCE.md"),
    implementations=(
        _impl("tigrbl", "src/tigrbl_equivalence_contracts/equivalences/web_socket_json_rpc_table/tigrbl_impl.py", _lazy_attr("equivalences.web_socket_json_rpc_table.tigrbl_impl", "app"), "asgi", assert_equivalence, (), lambda result: result),
        _impl("fastapi", "src/tigrbl_equivalence_contracts/equivalences/web_socket_json_rpc_table/fastapi_impl.py", _lazy_attr("equivalences.web_socket_json_rpc_table.fastapi_impl", "app"), "asgi", assert_equivalence, (), lambda result: result),
        _impl("flask", "src/tigrbl_equivalence_contracts/equivalences/web_socket_json_rpc_table/flask_impl.py", _lazy_attr("equivalences.web_socket_json_rpc_table.flask_impl", "app"), "wsgi", assert_equivalence, (), lambda result: result),
    ),
)
