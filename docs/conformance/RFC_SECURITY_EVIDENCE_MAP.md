# RFC Security Evidence Map

This file is the Phase 11 per-RFC evidence mapping for the current target.

## Retained and proved in Gate C

| Row | Phase 11 status | Owner | Code | Tests / evidence | Notes |
|---|---|---|---|---|---|
| RFC 7235 | Gate C passed | Auth & Security | `pkgs/core/tigrbl_concrete/tigrbl_concrete/_concrete/_security/http_basic.py`<br>`pkgs/core/tigrbl_concrete/tigrbl_concrete/_concrete/_security/http_bearer.py`<br>`pkgs/core/tigrbl_runtime/tigrbl_runtime/executors/packed.py`<br>`pkgs/core/tigrbl_atoms/tigrbl_atoms/atoms/egress/asgi_send.py` | `tools/ci/tests/test_http_auth_challenges.py`<br>`docs/conformance/audit/2026/p11-gate-c/pytest_gate_c_conformance_security.log` | The retained framework-owned scope is HTTP authentication challenge semantics and header propagation. |
| RFC 7617 | Gate C passed | Auth & Security | `pkgs/core/tigrbl_concrete/tigrbl_concrete/_concrete/_security/http_basic.py` | `tools/ci/tests/test_http_auth_challenges.py`<br>`docs/conformance/audit/2026/p11-gate-c/pytest_gate_c_conformance_security.log` | The retained scope is Basic credentials parsing plus `WWW-Authenticate: Basic ...` challenge behavior. |
| RFC 6750 | Gate C passed | Auth & Security | `pkgs/core/tigrbl_concrete/tigrbl_concrete/_concrete/_security/http_bearer.py` | `tools/ci/tests/test_http_auth_challenges.py`<br>`docs/conformance/audit/2026/p11-gate-c/pytest_gate_c_conformance_security.log` | The retained scope is Bearer credential parsing plus challenge/error signaling through `WWW-Authenticate`. |

## Explicitly de-scoped from the current cycle

| Row | Current status | Owner | Evidence | Rationale |
|---|---|---|---|---|
| OIDC Core 1.0 | de-scoped | Governance + Auth & Security | `docs/governance/TARGET_BOUNDARY.md`<br>`docs/conformance/CURRENT_TARGET.md` | The repo closes the OAS `openIdConnect` scheme row, but it does not implement the broader OIDC Core discovery/claims/flow surface. |
| RFC 6749 | de-scoped | Governance + Auth & Security | `docs/governance/TARGET_BOUNDARY.md`<br>`docs/conformance/CURRENT_TARGET.md` | The repo closes the OAS `oauth2` scheme row, but it does not implement broader OAuth 2.0 runtime-flow closure. |
| RFC 7519 | de-scoped | Governance + Auth & Security | `docs/governance/TARGET_BOUNDARY.md` | No first-class JWT validation/claims surface exists in the framework core. |
| RFC 7636 | de-scoped | Governance + Auth & Security | `docs/governance/TARGET_BOUNDARY.md` | No first-class PKCE runtime/docs surface exists. |
| RFC 8414 | de-scoped | Governance + Auth & Security | `docs/governance/TARGET_BOUNDARY.md` | No first-class discovery/metadata surface is retained in the current boundary. |
| RFC 8705 | de-scoped | Governance + Auth & Security | `docs/governance/TARGET_BOUNDARY.md` | The OAS `mutualTLS` scheme row is retained, but exact mTLS RFC runtime closure is not. |
| RFC 9110 exact row | de-scoped | Governance + Docs & Runtime | `docs/governance/TARGET_BOUNDARY.md` | The repo still has framework-owned request/response semantics, but the exact RFC 9110 closure row is too broad for the current cycle. |
| RFC 9449 | de-scoped | Governance + Auth & Security | `docs/governance/TARGET_BOUNDARY.md` | No DPoP implementation exists in the framework tree. |
| OIDC discovery/docs surface | de-scoped | Governance + Auth & Security | `docs/governance/TARGET_BOUNDARY.md` | No first-class discovery/docs route surface exists and it is not retained for the current cycle. |
