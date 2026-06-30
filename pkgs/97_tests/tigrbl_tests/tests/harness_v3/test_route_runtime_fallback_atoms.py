from __future__ import annotations

from types import SimpleNamespace

from tigrbl_atoms.atoms.dispatch import binding_match, binding_parse, input_normalize, op_resolve


def test_rest_route_runtime_fallback_atoms_resolve_payload_and_status() -> None:
    plan = SimpleNamespace(
        proto_indices={
            "http.rest": {
                "exact": {
                    "PATCH /widgets/7": {"selector": "PATCH /widgets/7"},
                }
            }
        },
        opkey_to_meta={("http.rest", "PATCH /widgets/7"): 0},
        opmeta=(SimpleNamespace(model="Widget", alias="replace", target="replace"),),
    )
    ctx = SimpleNamespace(
        method="PATCH",
        path="/widgets/7",
        body={"name": "Ada"},
        temp={"dispatch": {}, "route": {}},
        kernel_plan=plan,
    )

    binding_match._run(None, ctx)
    binding_parse._run(None, ctx)
    input_normalize._run(None, ctx)
    op_resolve._run(None, ctx)

    assert ctx.protocol == "http.rest"
    assert ctx.selector == "PATCH /widgets/7"
    assert ctx.payload == {"name": "Ada"}
    assert ctx.model == "Widget"
    assert ctx.op == "replace"
    assert ctx.status_code == 200
    assert ctx.temp["dispatch"]["binding"] == 0
    assert ctx.temp["route"]["payload"] == {"name": "Ada"}
