# Gate D: Reproducibility

## Objective

Prove clean-room package assembly and installed-package reproducibility on the selected candidate build.

## Status

Passed in the Phase 12 checkpoint.

## What Phase 12 proves

- wheel and sdist assembly succeed for `pkgs/core/tigrbl` on the selected candidate build
- wheel metadata exposes the governed `tigrbl = tigrbl.cli:console_main` console entry point
- installed-package CLI smoke succeeds from a isolated target install root using built artifacts
- installed-package server-runner translation smoke succeeds for Uvicorn, Hypercorn, Gunicorn, and Tigrcorn without relying on the working tree import path
- the dev-bundle evidence index, build notes, artifact manifests, and gate-result summary agree on the same candidate build identity: `0.3.18.dev1`

## Primary proof surfaces

- `tools/conformance/clean_room_package_smoke.py`
- `tools/conformance/installed_package_smoke.py`
- `tools/ci/validate_gate_d_reproducibility.py`
- `.github/workflows/gate-d-reproducibility.yml`
- `docs/conformance/dev/0.3.18.dev1/gate-results/gate-d-reproducibility.md`
- `docs/conformance/dev/0.3.18.dev1/artifacts/clean-room-package-manifest.json`
- `docs/conformance/dev/0.3.18.dev1/artifacts/installed-package-smoke-manifest.json`
- `docs/conformance/releases/0.3.18/gate-results/gate-d-reproducibility.md`

## Position after Gate E

Gate D does not itself promote the package. Promotion is now recorded separately in Gate E for stable release `0.3.18`.
