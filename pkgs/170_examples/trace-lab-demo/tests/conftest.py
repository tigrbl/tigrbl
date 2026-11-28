from collections import deque

import pytest
from trace_lab_demo.capture import RETENTION


class Buffer:
    def __init__(self):
        self.rows = deque(maxlen=RETENTION)
        self.revision = 0

    def add(self, kind, transport, fields):
        self.revision += 1
        self.rows.append(
            {
                "sequence": self.revision,
                "kind": kind,
                "transport": transport,
                "at": "2026-11-23T12:00:00Z",
                **fields,
            }
        )

    def data(self):
        return {"revision": self.revision, "events": list(self.rows)}


@pytest.fixture
def buffer():
    return Buffer()
