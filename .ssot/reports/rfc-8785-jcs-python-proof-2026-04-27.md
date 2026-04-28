# RFC 8785 JCS Python Proof

## Scope

This proof covers the core-owned Python canonical JSON helper exported at
`tigrbl_core.canonical_json`, with `tigrbl.canonical_json` retained only as an
import/export compatibility projection. Runtime and runtime executor packages
do not own or expose this canonicalization surface.

## Verified Behavior

- Object members are emitted in deterministic lexical order.
- Equivalent nested payloads emit identical UTF-8 JSON bytes.
- Non-finite JSON numbers (`NaN`, `Infinity`, and `-Infinity`) are rejected.

## Verification

Command:

```powershell
uv run pytest pkgs/core/tigrbl_tests/tests/unit/test_jcs_canonicalization_contract.py -q --basetemp .tmp\pytest-jcs-proof
```

Result:

```text
5 passed in 0.11s
```

## Executable Guard Refresh

On 2026-04-27T20:03:50-05:00, the stale xfail fallback in
`pkgs/core/tigrbl_tests/tests/unit/test_jcs_canonicalization_contract.py` was
removed so the governed test now fails closed if the exported helper disappears.

Command:

```powershell
.\.venv\Scripts\python.exe -m pytest pkgs\core\tigrbl_tests\tests\unit\test_jcs_canonicalization_contract.py -q --basetemp .tmp\pytest-jcs-current
```

Result:

```text
5 passed in 0.16s
```
