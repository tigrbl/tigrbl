from datetime import UTC, datetime

from tigrbl_trace.wire import BATCH_SIZE
from tigrbl_trace_transport import TraceExporter


def test_atom_records_are_formatted_on_dequeue_and_keep_sequence_across_batches():
    exporter = TraceExporter("http://127.0.0.1:8766", "test", "pilot", "test")
    anchor = datetime(2026, 11, 25, tzinfo=UTC)
    formatted = []

    def format_sample(at, ordinal, sample):
        assert at == anchor
        formatted.append(ordinal)
        return {
            "source_ended_at": at.isoformat(),
            "atom_ordinal": ordinal,
            "atom_label": sample,
        }

    exporter.capture("Invocation", "REST", {})
    samples = ["atom:sys:commit_tx"] * (BATCH_SIZE + 2)
    exporter.capture_atoms(
        "REST", {"invocation_id": "inv"}, anchor, samples, format_sample
    )
    exporter.capture("Transaction", "REST", {})
    assert not formatted
    first, first_items, first_atoms = exporter._batch()
    last, last_items, last_atoms = exporter._batch()
    rows = first + last
    assert (first_items, first_atoms) == (1, 0)
    assert (last_items, last_atoms) == (2, len(samples))
    assert [row["sequence"] for row in rows] == list(range(1, len(samples) + 3))
    assert [row["fields"]["atom_ordinal"] for row in rows[1:-1]] == formatted
    assert all(row["fields"]["invocation_id"] == "inv" for row in rows[1:-1])
