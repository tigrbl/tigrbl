from __future__ import annotations

import json
from types import SimpleNamespace

from tigrbl_kernel.models import OpKey
from tigrbl_atoms.atoms.dispatch import (
    REGISTRY,
    binding_match,
    binding_parse,
    input_normalize,
    op_resolve,
)
from tigrbl_atoms.types import Atom


def test_dispatch_registry_contains_expected_atoms() -> None:
    assert set(REGISTRY) == {
        ("dispatch", "binding_match"),
        ("dispatch", "binding_parse"),
        ("dispatch", "input_normalize"),
        ("dispatch", "op_resolve"),
    }


def test_dispatch_instances_and_impls_use_atom_contract() -> None:
    for module in (binding_match, binding_parse, input_normalize, op_resolve):
        assert isinstance(module.INSTANCE, Atom)
        assert issubclass(module.AtomImpl, Atom)
        assert module.INSTANCE.anchor == module.ANCHOR


def test_binding_match_parse_normalize_and_resolve() -> None:
    plan = SimpleNamespace(
        proto_indices={
            "http.jsonrpc": {
                "endpoints": {
                    "default": {
                        "Widget.create": {
                            "meta_index": 0,
                            "selector": "default:Widget.create",
                            "rpc_method": "Widget.create",
                            "endpoint": "default",
                        }
                    }
                }
            }
        },
        opmeta=[SimpleNamespace(model="Widget", alias="create", target="widgets")],
        opkey_to_meta={OpKey("http.jsonrpc", "default:Widget.create"): 0},
    )
    ctx = SimpleNamespace(
        method="POST",
        path="/rpc",
        body=json.dumps(
            {"jsonrpc": "2.0", "method": "Widget.create", "params": {"name": "x"}}
        ).encode(),
        temp={"dispatch": {}, "route": {}},
        kernel_plan=plan,
    )

    binding_parse._run(None, ctx)
    binding_match._run(None, ctx)
    input_normalize._run(None, ctx)
    op_resolve._run(None, ctx)

    assert ctx.temp["dispatch"]["binding_protocol"] == "http.jsonrpc"
    assert ctx.temp["dispatch"]["binding_selector"] == "default:Widget.create"
    assert ctx.temp["dispatch"]["endpoint"] == "default"
    assert ctx.payload == {"name": "x"}
    assert ctx.op == "create"
    assert ctx.opmeta_index == 0
