# Installed-Package Smoke Lane

This lane records the installed-package CLI and runner-translation proof used by Gate D.

## Verified now

- installed `tigrbl` command from built artifact in an isolated target install root
- CLI smoke for `capabilities`, `openapi`, `openrpc`, `doctor`, and `routes`
- installed-package runner translation smoke for Uvicorn, Hypercorn, Gunicorn, and Tigrcorn
- native binding support supplied through `bindings/python/tigrbl_native/python` because no built native binding wheel is produced in this repository checkpoint

## Primary manifest

- `docs/conformance/dev/0.3.18.dev1/artifacts/installed-package-smoke-manifest.json`
