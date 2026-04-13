# Tigrcorn Origin, Pathsend, and Static Contract

This contract freezes origin/pathsend/static semantics for path resolution, file selection, HTTP semantics, and send behavior at the public operator surface.

## Normative points

- path resolution must fail closed on traversal or mutation attempts
- file selection and send behavior must be deterministic and documented
- static/pathsend semantics must preserve HTTP correctness before throughput claims are published
- CONNECT relay abuse and mixed-topology abuse stay in the negative certification corpus

This repo governs the public contract and negative-certification posture, not the underlying Tigrcorn implementation.
