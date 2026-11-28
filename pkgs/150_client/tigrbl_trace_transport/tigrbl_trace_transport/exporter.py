"""Export Tigrbl identity events without waiting on the trace collector."""

import asyncio
import logging
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from queue import Empty, Full, Queue
from threading import Lock
from uuid import uuid4

import httpx

from tigrbl_trace.wire import BATCH_SIZE, WIRE_VERSION, BatchSource, select_fields

LOG = logging.getLogger(__name__)


@dataclass
class _AtomBatch:
    sequence: int
    transport: str
    context: dict
    anchor: datetime
    samples: list
    format_sample: Callable
    cursor: int = 0

    def next_event(self) -> dict:
        fields = self.format_sample(
            self.anchor, self.cursor + 1, self.samples[self.cursor]
        )
        event = {
            "sequence": self.sequence + self.cursor,
            "captured_at": fields["source_ended_at"],
            "kind": "Atom",
            "transport": self.transport,
            "fields": select_fields({**self.context, **fields}),
        }
        self.cursor += 1
        return event


class TraceExporter:
    def __init__(self, collector_url: str, token: str, service: str, environment: str):
        url = httpx.URL(collector_url)
        if url.scheme != "https" and not (
            url.scheme == "http" and url.host in {"localhost", "127.0.0.1", "::1"}
        ):
            raise ValueError("The trace collector requires HTTPS or loopback HTTP")
        self.endpoint = url.copy_with(path="/internal/trace/batches", query=None)
        self.headers = {"Authorization": f"Bearer {token}"}
        self.source = BatchSource(
            service=service,
            environment=environment,
            worker_boot_id=uuid4().hex,
        ).model_dump()
        self._queue = Queue(maxsize=2048)
        self._lock = Lock()
        self._sequence = 0
        self._atom_count = 0
        self._pending_atoms: _AtomBatch | None = None
        self._task = None
        self.dropped = 0
        self.send_failures = 0

    def capture(self, kind: str, transport: str, fields: Mapping) -> None:
        with self._lock:
            self._sequence += 1
            try:
                self._queue.put_nowait(
                    {
                        "sequence": self._sequence,
                        "captured_at": datetime.now(timezone.utc).isoformat(),
                        "kind": kind[:100],
                        "transport": transport[:32],
                        "fields": select_fields(fields),
                    }
                )
            except Full:
                self.dropped += 1

    def capture_atoms(self, transport, context, anchor, samples, format_sample) -> None:
        count = len(samples)
        if not count:
            return
        with self._lock:
            batch = _AtomBatch(
                self._sequence + 1,
                transport[:32],
                context,
                anchor,
                samples,
                format_sample,
            )
            self._sequence += count
            if self._atom_count + count > 4096:
                self.dropped += count
                return
            try:
                self._queue.put_nowait(batch)
            except Full:
                self.dropped += count
            else:
                self._atom_count += count

    def start(self) -> None:
        if self._task is None:
            self._task = asyncio.create_task(self._send())

    async def close(self) -> None:
        if self._task is None:
            return
        try:
            await asyncio.wait_for(self._queue_drained(), timeout=3)
        except TimeoutError:
            LOG.warning("Trace exporter stopped with undelivered events")
        finally:
            self._task.cancel()
            await asyncio.gather(self._task, return_exceptions=True)
            self._task = None

    async def _queue_drained(self) -> None:
        while self._queue.unfinished_tasks:
            await asyncio.sleep(0.05)

    def _batch(self):
        batch = []
        finished_items = 0
        finished_atoms = 0
        for _ in range(BATCH_SIZE):
            item = self._pending_atoms
            if item is None:
                try:
                    item = self._queue.get_nowait()
                except Empty:
                    break
            if isinstance(item, _AtomBatch):
                batch.append(item.next_event())
                if item.cursor == len(item.samples):
                    finished_atoms += len(item.samples)
                    finished_items += 1
                    self._pending_atoms = None
                else:
                    self._pending_atoms = item
            else:
                batch.append(item)
                finished_items += 1
        return batch, finished_items, finished_atoms

    async def _send(self) -> None:
        async with httpx.AsyncClient(timeout=2, trust_env=False) as client:
            while True:
                batch, finished_items, finished_atoms = self._batch()
                if not batch:
                    await asyncio.sleep(0.1)
                    continue
                delay = 0.25
                while True:
                    try:
                        response = await client.post(
                            self.endpoint,
                            headers=self.headers,
                            json={
                                "version": WIRE_VERSION,
                                **self.source,
                                "events": batch,
                            },
                        )
                        response.raise_for_status()
                    except httpx.HTTPError as error:
                        self.send_failures += 1
                        if self.send_failures == 1 or self.send_failures % 10 == 0:
                            LOG.warning(
                                "Trace export failed (%d failures, %d dropped)",
                                self.send_failures,
                                self.dropped,
                            )
                        if isinstance(error, httpx.HTTPStatusError) and (
                            400 <= error.response.status_code < 500
                            and error.response.status_code not in {408, 429}
                        ):
                            with self._lock:
                                self.dropped += len(batch)
                            break
                        await asyncio.sleep(delay)
                        delay = min(delay * 2, 5)
                    else:
                        break
                with self._lock:
                    self._atom_count -= finished_atoms
                for _ in range(finished_items):
                    self._queue.task_done()
