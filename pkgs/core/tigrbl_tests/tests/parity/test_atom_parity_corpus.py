from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]


def test_atom_parity_corpus_covers_every_generated_feature() -> None:
    inventory = json.loads((ROOT / ".ssot/reports/python-rust-atom-parity-inventory.json").read_text(encoding="utf-8"))
    results = json.loads((ROOT / ".ssot/reports/python-rust-atom-parity-results.json").read_text(encoding="utf-8"))

    by_atom = {item["atom_id"]: item for item in results["results"]}
    assert results["status"] == "passed"
    assert set(by_atom) == {item["id"] for item in inventory["units"]}
    assert all(item["checks"]["inventory_tracked"] for item in by_atom.values())
    assert all(item["checks"]["feature_mapped"] for item in by_atom.values())
    assert all(item["checks"]["runtime_lanes_declared"] for item in by_atom.values())


def test_matched_atoms_are_marked_for_semantic_pair_checks() -> None:
    inventory = json.loads((ROOT / ".ssot/reports/python-rust-atom-parity-inventory.json").read_text(encoding="utf-8"))
    results = json.loads((ROOT / ".ssot/reports/python-rust-atom-parity-results.json").read_text(encoding="utf-8"))

    matched = {item["id"] for item in inventory["units"] if item["state"] == "matched"}
    checked = {item["atom_id"] for item in results["results"] if item["checks"]["semantic_pair_required"]}
    assert matched
    assert checked == matched
