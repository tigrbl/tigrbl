from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Tuple

from . import abort_group as _abort_group
from . import admit as _admit
from . import await_seal as _await_seal
from . import cleanup as _cleanup
from . import commit as _commit
from . import dedupe as _dedupe
from . import error_project as _error_project
from . import execute as _execute
from . import precommit_validate as _precommit_validate
from . import prepare_execute as _prepare_execute
from . import reject_admission as _reject_admission
from . import result_slots as _result_slots
from . import seal_check as _seal_check
from . import tx_begin as _tx_begin

RunFn = Callable[[Optional[object], Any], Any]

_ORDERED: Tuple[Tuple[str, str, str, RunFn], ...] = (
    ("batch", "admit", _admit.ANCHOR, _admit.INSTANCE),
    ("batch", "dedupe", _dedupe.ANCHOR, _dedupe.INSTANCE),
    ("batch", "seal_check", _seal_check.ANCHOR, _seal_check.INSTANCE),
    ("batch", "await_seal", _await_seal.ANCHOR, _await_seal.INSTANCE),
    ("batch", "tx_begin", _tx_begin.ANCHOR, _tx_begin.INSTANCE),
    (
        "batch",
        "prepare_execute",
        _prepare_execute.ANCHOR,
        _prepare_execute.INSTANCE,
    ),
    ("batch", "execute", _execute.ANCHOR, _execute.INSTANCE),
    ("batch", "result_slots", _result_slots.ANCHOR, _result_slots.INSTANCE),
    (
        "batch",
        "precommit_validate",
        _precommit_validate.ANCHOR,
        _precommit_validate.INSTANCE,
    ),
    ("batch", "commit", _commit.ANCHOR, _commit.INSTANCE),
    ("batch", "cleanup", _cleanup.ANCHOR, _cleanup.INSTANCE),
    (
        "batch",
        "reject_admission",
        _reject_admission.ANCHOR,
        _reject_admission.INSTANCE,
    ),
    ("batch", "abort_group", _abort_group.ANCHOR, _abort_group.INSTANCE),
    ("batch", "error_project", _error_project.ANCHOR, _error_project.INSTANCE),
)

REGISTRY: Dict[Tuple[str, str], Tuple[str, RunFn]] = {
    (domain, subject): (anchor, run) for domain, subject, anchor, run in _ORDERED
}

__all__ = ["REGISTRY", "RunFn"]
