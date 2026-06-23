from __future__ import annotations

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / "examples" / "equivalence_contracts"


def _add(path: Path) -> None:
    text = str(path)
    if text not in sys.path:
        sys.path.insert(0, text)


_add(PROJECT / "src")

for base in (ROOT / "pkgs" / "core", ROOT / "pkgs" / "engines", ROOT / "pkgs" / "apps"):
    if not base.is_dir():
        continue
    for child in sorted(base.iterdir()):
        if not child.is_dir():
            continue
        _add(child)
        src = child / "src"
        if src.is_dir():
            _add(src)

from tigrbl_equivalence_contracts import (
    CERTIFIABLE_EQUIVALENCES,
    certify_all,
    equivalence_by_id,
)


class CertifiableEquivalenceTests(unittest.TestCase):
    def test_every_declared_equivalence_certifies(self) -> None:
        results = certify_all()

        self.assertEqual(len(results), len(CERTIFIABLE_EQUIVALENCES))
        self.assertTrue(all(result.certified for result in results))
        self.assertEqual(
            {result.equivalence_id for result in results},
            {case.id for case in CERTIFIABLE_EQUIVALENCES},
        )

    def test_transport_read_equivalence_ignores_transport_envelope_fields(self) -> None:
        result = equivalence_by_id("transport.rest-jsonrpc-websocket-read").certify()

        self.assertEqual(result.status, "equivalent")
        self.assertEqual(result.evidence["transport_count"], 3)
        self.assertEqual(
            result.evidence["normalized_result"],
            {
                "diagnostics": {"classification": "ok"},
                "effects": ("read:item-1",),
                "value": {"id": "item-1", "name": "Ada"},
            },
        )

    def test_stream_equivalence_preserves_ordering_and_completion(self) -> None:
        result = equivalence_by_id("transport.stream-sse-webtransport-tail").certify()

        self.assertEqual(result.status, "equivalent")
        self.assertEqual(result.evidence["families"], ("stream",))
        self.assertEqual(result.evidence["normalized_result"]["ordering"], "ordered")
        self.assertEqual(result.evidence["normalized_result"]["completion"], "complete")

    def test_router_equivalence_is_projection_not_authority_equivalence(self) -> None:
        result = equivalence_by_id("router.fastapi-flask-tigrbl-prefix").certify()

        self.assertEqual(result.status, "analogous")
        self.assertEqual(
            result.evidence["projection"],
            {
                "path": "/v1/items/{item_id}",
                "methods": ("GET",),
                "endpoint": "Item.read",
            },
        )
        self.assertEqual(
            result.evidence["authorities"]["tigrbl.router"],
            "operation binding",
        )
        self.assertEqual(
            result.evidence["authorities"]["fastapi.apirouter"],
            "path operation",
        )

    def test_table_equivalence_keeps_tigrbl_table_authority_explicit(self) -> None:
        result = equivalence_by_id("table.fastapi-flask-tigrbl-resource").certify()

        self.assertEqual(result.status, "analogous")
        self.assertEqual(result.evidence["profile"], "rest_jsonrpc")
        self.assertEqual(
            result.evidence["projection"]["operations"],
            ("create", "list", "read"),
        )
        self.assertEqual(
            result.evidence["binding_families"],
            ("http.rest", "http.jsonrpc"),
        )
        self.assertEqual(
            result.evidence["authorities"]["tigrbl.table-profile"],
            "TableProfileSpec",
        )

    def test_engine_equivalence_certifies_logical_identity_not_physical_sql_parity(self) -> None:
        result = equivalence_by_id("engine.logical-datatype-lowering").certify()

        self.assertEqual(result.status, "projection-only")
        self.assertEqual(
            result.evidence["lowerings"]["uuid"],
            {"sqlite": "TEXT", "postgres": "UUID"},
        )
        self.assertEqual(
            result.evidence["lowerings"]["json"],
            {"sqlite": "JSON", "postgres": "JSONB"},
        )


if __name__ == "__main__":
    unittest.main()
