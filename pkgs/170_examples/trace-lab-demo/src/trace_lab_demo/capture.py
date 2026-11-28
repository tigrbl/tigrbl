"""Compose a Trace Lab snapshot and attach demo scenario metadata."""

from collections import deque
from threading import RLock
from uuid import uuid4

from tigrbl_trace import project_event, projection_context, summarize

from trace_lab.http import utc_now

RETENTION = 750


class Capture:
    def __init__(self, timeline):
        self.timeline = timeline
        self.id = uuid4().hex
        self.active_run = None
        self.last_run = None
        self._run_labels = deque(maxlen=RETENTION)
        self._lock = RLock()

    def add(self, kind, transport, fields):
        with self._lock:
            self.timeline.add(kind, transport, fields)
            if self.active_run is not None:
                self._run_labels.append((self.timeline.revision, self.active_run))

    def snapshot(self):
        with self._lock:
            native = self.timeline.data()
            labels = dict(self._run_labels)
            active = self.active_run
            last = self.last_run
        rows = native["events"]
        origins = projection_context(rows)
        events = []
        for row in rows:
            event = project_event(row, origins)
            if event is None:
                continue
            event["capture_id"] = self.id
            if run := labels.get(event["sequence"]):
                event["scenario_run_id"] = run
            events.append(event)
        revision = native["revision"]
        return {
            "revision": revision,
            "capture_id": self.id,
            "captured_at": utc_now(),
            "retention_limit": RETENTION,
            "running": active is not None,
            "active_run_id": active,
            "last_run_summary": last,
            "retained_range": {
                "min_sequence": rows[0]["sequence"] if rows else 0,
                "max_sequence": revision,
                "total_emitted": revision,
                "evicted_count": revision - len(rows),
            },
            "events": events,
            "rollup": summarize(events),
        }
