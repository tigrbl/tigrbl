from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Tuple

from . import commit_tx as _commit_tx
from . import handler_bulk_create as _handler_bulk_create
from . import handler_bulk_delete as _handler_bulk_delete
from . import handler_bulk_merge as _handler_bulk_merge
from . import handler_bulk_replace as _handler_bulk_replace
from . import handler_bulk_update as _handler_bulk_update
from . import handler_checkpoint as _handler_checkpoint
from . import handler_clear as _handler_clear
from . import handler_count as _handler_count
from . import handler_create as _handler_create
from . import handler_delete as _handler_delete
from . import handler_download as _handler_download
from . import handler_exists as _handler_exists
from . import handler_aggregate as _handler_aggregate
from . import handler_group_by as _handler_group_by
from . import handler_list as _handler_list
from . import handler_merge as _handler_merge
from . import handler_noop as _handler_noop
from . import handler_append_chunk as _handler_append_chunk
from . import handler_persistence as _handler_persistence
from . import handler_publish as _handler_publish
from . import handler_read as _handler_read
from . import handler_replace as _handler_replace
from . import handler_send_datagram as _handler_send_datagram
from . import handler_subscribe as _handler_subscribe
from . import handler_tail as _handler_tail
from . import handler_update as _handler_update
from . import handler_upload as _handler_upload
from . import start_tx as _start_tx

RunFn = Callable[[Optional[object], Any], Any]

_ORDERED: Tuple[Tuple[str, str, str, RunFn], ...] = (
    ("sys", "start_tx", _start_tx.ANCHOR, _start_tx.INSTANCE),
    (
        "sys",
        "handler_persistence",
        _handler_persistence.ANCHOR,
        _handler_persistence.INSTANCE,
    ),
    ("sys", "handler_create", _handler_create.ANCHOR, _handler_create.INSTANCE),
    ("sys", "handler_read", _handler_read.ANCHOR, _handler_read.INSTANCE),
    ("sys", "handler_update", _handler_update.ANCHOR, _handler_update.INSTANCE),
    ("sys", "handler_replace", _handler_replace.ANCHOR, _handler_replace.INSTANCE),
    ("sys", "handler_merge", _handler_merge.ANCHOR, _handler_merge.INSTANCE),
    ("sys", "handler_noop", _handler_noop.ANCHOR, _handler_noop.INSTANCE),
    ("sys", "handler_delete", _handler_delete.ANCHOR, _handler_delete.INSTANCE),
    ("sys", "handler_list", _handler_list.ANCHOR, _handler_list.INSTANCE),
    ("sys", "handler_clear", _handler_clear.ANCHOR, _handler_clear.INSTANCE),
    ("sys", "handler_count", _handler_count.ANCHOR, _handler_count.INSTANCE),
    ("sys", "handler_exists", _handler_exists.ANCHOR, _handler_exists.INSTANCE),
    (
        "sys",
        "handler_bulk_create",
        _handler_bulk_create.ANCHOR,
        _handler_bulk_create.INSTANCE,
    ),
    (
        "sys",
        "handler_bulk_update",
        _handler_bulk_update.ANCHOR,
        _handler_bulk_update.INSTANCE,
    ),
    (
        "sys",
        "handler_bulk_replace",
        _handler_bulk_replace.ANCHOR,
        _handler_bulk_replace.INSTANCE,
    ),
    (
        "sys",
        "handler_bulk_merge",
        _handler_bulk_merge.ANCHOR,
        _handler_bulk_merge.INSTANCE,
    ),
    (
        "sys",
        "handler_bulk_delete",
        _handler_bulk_delete.ANCHOR,
        _handler_bulk_delete.INSTANCE,
    ),
    (
        "sys",
        "handler_aggregate",
        _handler_aggregate.ANCHOR,
        _handler_aggregate.INSTANCE,
    ),
    ("sys", "handler_group_by", _handler_group_by.ANCHOR, _handler_group_by.INSTANCE),
    ("sys", "handler_publish", _handler_publish.ANCHOR, _handler_publish.INSTANCE),
    (
        "sys",
        "handler_subscribe",
        _handler_subscribe.ANCHOR,
        _handler_subscribe.INSTANCE,
    ),
    ("sys", "handler_tail", _handler_tail.ANCHOR, _handler_tail.INSTANCE),
    ("sys", "handler_upload", _handler_upload.ANCHOR, _handler_upload.INSTANCE),
    ("sys", "handler_download", _handler_download.ANCHOR, _handler_download.INSTANCE),
    (
        "sys",
        "handler_append_chunk",
        _handler_append_chunk.ANCHOR,
        _handler_append_chunk.INSTANCE,
    ),
    (
        "sys",
        "handler_send_datagram",
        _handler_send_datagram.ANCHOR,
        _handler_send_datagram.INSTANCE,
    ),
    (
        "sys",
        "handler_checkpoint",
        _handler_checkpoint.ANCHOR,
        _handler_checkpoint.INSTANCE,
    ),
    ("sys", "commit_tx", _commit_tx.ANCHOR, _commit_tx.INSTANCE),
)

REGISTRY: Dict[Tuple[str, str], Tuple[str, RunFn]] = {
    (domain, subject): (anchor, run) for domain, subject, anchor, run in _ORDERED
}

__all__ = ["REGISTRY", "RunFn"]
