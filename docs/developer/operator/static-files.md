# Static Files

## Current public surface

The framework now exposes a first-class static-files mount:

- `mount_static(directory=..., path="/static")`

Static file serving is path-based and remains bounded to the configured directory root.

## Notes

- file responses and favicon support continue to exist
- the operator-surface tests verify a mounted nested static path round-trip
