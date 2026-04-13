# `static-origin`

Use this profile when static files and pathsend-like behavior are part of the public deployment contract and path resolution must be tightly constrained.

## Operator contract

- select with `--deployment-profile static-origin`
- use `--origin-static-policy static-origin`
- keep `--proxy-contract strict` unless an explicit trusted edge contract exists
- keep `--early-data-policy reject`

## Failure posture

- reject traversal, mutation, and ambiguous file-selection inputs
- keep HTTP semantics for static/pathsend deterministic
- certify negative behavior before positive throughput claims
