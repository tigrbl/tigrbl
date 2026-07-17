from __future__ import annotations

from tigrbl import TableBase
from tigrbl.types import Column, String


class Thread(TableBase):
    __tablename__ = "websocket_realtime_thread"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    resource_name = "threads"


class Message(TableBase):
    __tablename__ = "websocket_realtime_message"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    thread_id = Column(String, nullable=False)
    body = Column(String, nullable=False)
    resource_name = "messages"
