from __future__ import annotations

from types import SimpleNamespace

from tigrbl_atoms.atoms.dispatch import binding_parse, input_normalize


def test_rest_payload_selection_merges_query_path_and_body_values() -> None:
    ctx = SimpleNamespace(
        body={"name": "Ada", "limit": 20},
        query={"limit": ["5"], "sort": ["name"]},
        temp={
            "dispatch": {
                "binding_protocol": "http.rest",
                "path_params": {"item_id": "7"},
            },
            "route": {},
            "hot": {"raw_query_string": b"limit=5&sort=name"},
        },
    )

    binding_parse._run(None, ctx)
    input_normalize._run(None, ctx)

    assert ctx.temp["dispatch"]["parsed_payload"] == {
        "limit": 20,
        "sort": "name",
        "item_id": "7",
        "name": "Ada",
    }
    assert ctx.payload == {
        "limit": 20,
        "sort": "name",
        "item_id": "7",
        "name": "Ada",
    }
    assert ctx.temp["dispatch"]["path_params"] == {"item_id": "7"}
    assert ctx.temp["route"]["payload"] == ctx.payload
