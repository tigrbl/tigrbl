# Phase 12 — Gate D Reproducibility

## Scope

This audit records the Gate D proof for the selected candidate build `0.3.18.dev1`.

## Verified in this checkpoint

- wheel and sdist assembly for `pkgs/core/tigrbl`
- installed-package CLI smoke from an isolated target install root
- installed-package runner translation smoke for Uvicorn, Hypercorn, Gunicorn, and Tigrcorn
- governed docs/build validation for pointers, layout, and evidence bundles

## Important note

The installed-package smoke in this checkpoint uses the built `tigrbl` wheel plus an isolated target install root for local workspace dependencies. The native binding import is satisfied through the repository source path `bindings/python/tigrbl_native/python` because this checkpoint does not produce a built native-binding wheel in the current container environment.

## Primary files

- `clean_room_package.log`
- `validate_doc_pointers.log`
- `validate_package_layout.log`
- `validate_evidence_bundles.log`
- `../..//../dev/0.3.18.dev1/artifacts/clean-room-package-manifest.json`
- `../..//../dev/0.3.18.dev1/artifacts/installed-package-smoke-manifest.json`
