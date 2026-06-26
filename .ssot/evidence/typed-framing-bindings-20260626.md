# Typed Framing Bindings Proof - 2026-06-26

Scope:

- Canonical BindingSpec framing policy remains typed and rejects profile/framing drift.
- Operator-surface closure includes the WebTransport control-plane package surface.
- `tigrbl_ops_webtransport` control operations are importable and executable through their package tests.

Command:

```powershell
uv run pytest -q pkgs/core/tigrbl_tests/tests/unit/runtime/test_canonical_bindingspec_framing_policy.py pkgs/core/tigrbl_tests/tests/unit/test_operator_surface_closure.py pkgs/core/tigrbl_ops_webtransport/tests/test_control_ops.py
```

Result:

```text
41 passed in 0.67s
```

Additional classification convergence command:

```powershell
uv run pytest -q pkgs/core/tigrbl_tests/tests/unit/runtime/test_contract_classification_consumption_policy.py
```

Result:

```text
4 passed in 0.21s
```

Additional WebTransport bridge command:

```powershell
uv run pytest -q pkgs/core/tigrbl_tests/tests/i9n/test_webtransport_tigrcorn_bridge.py
```

Result:

```text
3 passed in 0.21s
```
