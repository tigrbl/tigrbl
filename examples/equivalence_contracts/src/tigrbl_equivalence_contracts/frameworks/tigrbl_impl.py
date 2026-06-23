from __future__ import annotations

from tigrbl import (
    BulkCrudTable,
    EventStreamTable,
    JsonRpcOlapTable,
    JsonRpcOltpTable,
    JsonRpcTable,
    OlapTable,
    OltpTable,
    RestJsonRpcOlapTable,
    RestJsonRpcOltpTable,
    RestJsonRpcTable,
    RestOlapTable,
    RestOltpTable,
    RestTable,
    SseTable,
    StreamTable,
    TableBase,
    TigrblApp,
    WebSocketJsonRpcTable,
    WebSocketTable,
    WebTransportBidiTable,
    WebTransportClientStreamTable,
    WebTransportDatagramTable,
    WebTransportServerStreamTable,
    WebTransportTable,
)
from tigrbl.types import Column, String


class Widget(RestTable):
    __tablename__ = "widgets"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


class WidgetTableBase(TableBase):
    __tablename__ = "widgets_table_base"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


class WidgetRestTable(RestTable):
    __tablename__ = "widgets_rest_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


class WidgetJsonRpcTable(JsonRpcTable):
    __tablename__ = "widgets_json_rpc_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


class WidgetRestJsonRpcTable(RestJsonRpcTable):
    __tablename__ = "widgets_rest_json_rpc_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


class WidgetBulkCrudTable(BulkCrudTable):
    __tablename__ = "widgets_bulk_crud_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


class WidgetRestOltpTable(RestOltpTable):
    __tablename__ = "widgets_rest_oltp_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


class WidgetOltpTable(OltpTable):
    __tablename__ = "widgets_oltp_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


class WidgetJsonRpcOltpTable(JsonRpcOltpTable):
    __tablename__ = "widgets_json_rpc_oltp_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


class WidgetRestJsonRpcOltpTable(RestJsonRpcOltpTable):
    __tablename__ = "widgets_rest_json_rpc_oltp_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


class WidgetRestOlapTable(RestOlapTable):
    __tablename__ = "widgets_rest_olap_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


class WidgetOlapTable(OlapTable):
    __tablename__ = "widgets_olap_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


class WidgetJsonRpcOlapTable(JsonRpcOlapTable):
    __tablename__ = "widgets_json_rpc_olap_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


class WidgetRestJsonRpcOlapTable(RestJsonRpcOlapTable):
    __tablename__ = "widgets_rest_json_rpc_olap_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


class WidgetStreamTable(StreamTable):
    __tablename__ = "widgets_stream_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


class WidgetSseTable(SseTable):
    __tablename__ = "widgets_sse_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


class WidgetEventStreamTable(EventStreamTable):
    __tablename__ = "widgets_event_stream_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


class WidgetWebSocketTable(WebSocketTable):
    __tablename__ = "widgets_web_socket_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


class WidgetWebSocketJsonRpcTable(WebSocketJsonRpcTable):
    __tablename__ = "widgets_web_socket_json_rpc_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


class WidgetWebTransportTable(WebTransportTable):
    __tablename__ = "widgets_web_transport_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


class WidgetWebTransportBidiTable(WebTransportBidiTable):
    __tablename__ = "widgets_web_transport_bidi_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


class WidgetWebTransportClientStreamTable(WebTransportClientStreamTable):
    __tablename__ = "widgets_web_transport_client_stream_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


class WidgetWebTransportServerStreamTable(WebTransportServerStreamTable):
    __tablename__ = "widgets_web_transport_server_stream_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


class WidgetWebTransportDatagramTable(WebTransportDatagramTable):
    __tablename__ = "widgets_web_transport_datagram_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


app = TigrblApp(engine={"kind": "sqlite", "mode": "memory", "async": False})
app.include_table(Widget)
app.include_table(WidgetTableBase)
app.include_table(WidgetRestTable)
app.include_table(WidgetJsonRpcTable)
app.include_table(WidgetRestJsonRpcTable)
app.include_table(WidgetBulkCrudTable)
app.include_table(WidgetRestOltpTable)
app.include_table(WidgetOltpTable)
app.include_table(WidgetJsonRpcOltpTable)
app.include_table(WidgetRestJsonRpcOltpTable)
app.include_table(WidgetRestOlapTable)
app.include_table(WidgetOlapTable)
app.include_table(WidgetJsonRpcOlapTable)
app.include_table(WidgetRestJsonRpcOlapTable)
app.include_table(WidgetStreamTable)
app.include_table(WidgetSseTable)
app.include_table(WidgetEventStreamTable)
app.include_table(WidgetWebSocketTable)
app.include_table(WidgetWebSocketJsonRpcTable)
app.include_table(WidgetWebTransportTable)
app.include_table(WidgetWebTransportBidiTable)
app.include_table(WidgetWebTransportClientStreamTable)
app.include_table(WidgetWebTransportServerStreamTable)
app.include_table(WidgetWebTransportDatagramTable)
app.initialize()
