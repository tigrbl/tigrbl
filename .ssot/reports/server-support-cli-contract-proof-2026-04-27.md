# Server Support CLI Contract Proof

## Scope

This evidence covers the governed server-selection contract for the public
`tigrbl` CLI. First-class server support is limited to:

- `tigrcorn`
- `uvicorn`
- `hypercorn`
- `gunicorn`

The same contract explicitly tracks `daphne`, `twisted`, and `granian` as
out-of-boundary server options that must not be accepted by the CLI parser.

## Verification

Command:

```powershell
.venv\Scripts\python.exe -m pytest pkgs/core/tigrbl_tests/tests/unit/test_cli_srv.py -q --basetemp .tmp\pytest-server-support-proof
```

Result:

```text
21 passed in 0.31s
```

## Covered Contracts

- `SUPPORTED_SERVERS` is locked to `("tigrcorn", "uvicorn", "hypercorn", "gunicorn")`.
- `run --server <name>` dispatches to each supported server runner.
- `daphne`, `twisted`, and `granian` are rejected by CLI parser choices.
- Uvicorn, Hypercorn, Gunicorn, and Tigrcorn runners translate common serve
  configuration correctly.
- Tigrcorn-specific operational controls validate fail-closed for invalid
  values.

## Certification Result

The server-support feature rows and related claims now have direct executable
evidence for the supported and out-of-boundary server contract.
