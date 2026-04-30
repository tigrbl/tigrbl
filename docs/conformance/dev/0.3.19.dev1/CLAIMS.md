# Claims — 0.3.19.dev1

Supported claim ids: `HANDOFF-001`, `HANDOFF-002`, `NEXT-001`, `NEXT-002`

This bundle records the governed post-promotion handoff, active next-target
planning line, and the SSOT-certified 0.3.19 candidate boundary.

It claims certification only inside `bnd:tigrbl-0.3.19-certification-001`.
AsyncAPI UI, JSON Schema UI, and non-security-scheme OIDC/OAuth/JWT/DPoP
closure remain out of bounds.

| Claim ID | Status | Meaning |
|---|---|---|
| HANDOFF-001 | verified in checkpoint | stable release history is frozen and the active line is isolated |
| HANDOFF-002 | implemented | dedicated validator and workflow exist for the handoff checkpoint |
| NEXT-001 | verified in checkpoint | active line `0.3.19.dev1` is opened in docs and package metadata |
| NEXT-002 | verified in checkpoint | datatype/table work is governed as next-target scope |
| CERT-0.3.19-001 | certified | `rel:tigrbl-0.3.19` certified 251 implemented in-boundary features |
| CERT-0.3.19-002 | published | `rel:tigrbl-0.3.19` was promoted and published from the frozen boundary |
