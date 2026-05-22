# Proposal Draft: S3-Backed and KMS-Backed Material Providers for Tigrbl

Status: proposal draft

This draft is not an accepted ADR, SPEC, feature row, or release claim. It scopes a possible native Tigrbl material-provider surface for S3-backed and KMS-backed keys, certificates, credentials, and signing material. It does not propose turning Tigrbl into object storage.

## Current Model

Tigrbl currently models reusable providers primarily as engine/session providers:

- `EngineSpec` normalizes DSN, mapping, and engine configuration.
- `EngineProviderSpec` wraps an `EngineSpec`.
- `EngineProviderBase` exposes a small provider protocol around `spec` and `to_provider()`.
- Concrete engine providers lazily build an engine and session factory.
- Engine registrations are keyed by engine `kind` and expose `build(...)` plus `capabilities(...)`.

That model is useful precedent, but it is not a key/cert/material provider model. `SessionSpec.kms_key_alias` exists as a backend-agnostic data-protection hint; it is not currently wired to a reusable KMS provider.

## Proposed Shape

Introduce a separate material-provider family rather than overloading engine providers.

```python
MaterialSpec(
    uri="s3://security-bucket/tigrbl/jwks/current.json",
    kind="s3",
    purpose="jwks",
    required_encryption="aws:kms",
    kms_key_id="arn:aws:kms:us-east-1:123456789012:key/...",
)
```

Core concepts:

- `MaterialSpec`: declarative source and policy for material.
- `MaterialProviderSpec`: concrete-agnostic wrapper around `MaterialSpec`.
- `MaterialProviderBase`: resolves bytes, JSON, text, or structured material.
- `CryptoProviderBase`: performs signing, verification, encryption, decryption, key wrapping, or data-key generation where material should not leave the backend.
- `MaterialRegistry`: registers providers by scheme or kind, such as `file`, `env`, `s3`, `kms`, or `vault`.

Separate these two provider families:

- S3-backed material: fetch bytes or structured documents from S3.
- KMS-backed crypto: perform operations through KMS without treating KMS as file storage.

## Good S3-Backed Candidates

These are good candidates because Tigrbl can consume them as configuration, verification material, policy documents, credentials, or secrets without becoming an object store.

| Candidate | Why it fits | Suggested purpose |
|---|---|---|
| JWKS public key sets | Public verification material often rotates and benefits from central publication | `jwks` |
| JWT verification public keys | Similar to JWKS, but simpler deployments may use PEM bundles | `jwt_verification_keys` |
| Webhook signing secret blobs | Operators may centralize shared secrets with S3 encryption policy | `webhook_secret` |
| Webhook verification public keys | Useful for asymmetric webhook verification | `webhook_verification_keys` |
| Engine credential bundles | Avoid embedding passwords, DSNs, or account JSON directly in app config | `engine_credentials` |
| Engine DSN secret files | Maps cleanly to existing engine provider configuration | `engine_dsn` |
| Tenant policy bundles | App-level authorization or tenant routing policy can be stored centrally | `tenant_policy` |
| Runtime config fragments | Allows immutable deployment config documents to be pulled at startup | `runtime_config` |
| Release or audit evidence roots | Useful when applications verify governed artifacts or evidence manifests | `evidence_root` |
| Public certificate bundles | Good fit for verification trust material, not private signing | `certificate_bundle` |

S3 provider policy should support requiring observed object encryption:

- `AES256` for SSE-S3.
- `aws:kms` for SSE-KMS.
- `aws:kms:dsse` or equivalent normalized value for DSSE-KMS, depending on SDK metadata shape.

The provider should verify encryption mode through object metadata where possible, fail closed when required policy is absent, and avoid logging object contents.

## Good KMS-Backed Candidates

These are good candidates because KMS can perform a cryptographic operation or protect a data key without exposing raw key material.

| Candidate | Why it fits | Suggested purpose |
|---|---|---|
| JWT/JWS signing | Private signing key can remain in KMS | `jwt_signing` |
| Webhook signing | KMS can back asymmetric signatures or unwrap HMAC secrets | `webhook_signing` |
| Token/session signing | Reduces local key custody for high-value runtime tokens | `token_signing` |
| Envelope encryption for app secrets | KMS protects data keys while Tigrbl handles local plaintext only at use time | `secret_envelope` |
| Engine credential decryption | Keep stored credential bundles encrypted and decrypt at startup or use time | `engine_credentials_decrypt` |
| Field or column encryption key wrapping | Maps to data-protection hints such as `kms_key_alias` | `field_key_wrap` |
| Tenant data-key generation | Tenant isolation can be modeled as per-tenant key alias or encryption context | `tenant_data_key` |
| Audit or evidence signing | Creates attestable signatures for governed outputs | `evidence_signing` |

KMS provider policy should capture:

- KMS key id, alias, or ARN.
- Allowed algorithms.
- Encryption context requirements.
- Region and endpoint configuration.
- Fail-closed behavior for ambiguous key identity.
- Audit metadata without secret leakage.

## Good DSSE-KMS Candidates

DSSE-KMS is an S3 server-side encryption mode for S3 objects. It is not a generic KMS signing mode. In Tigrbl it should be modeled as a required policy on S3-backed material, not as a standalone KMS provider.

Good DSSE-KMS candidates:

- Engine credential bundles stored in S3.
- Webhook HMAC secret blobs stored in S3.
- Runtime secret bundles stored in S3.
- Tenant configuration bundles containing sensitive routing or policy data.
- Private key PEMs stored in S3 only when the operator accepts in-process key material.
- Release signing material or high-value evidence roots stored as S3 objects.

Poor DSSE-KMS candidates:

- Direct `kms://...` signing keys.
- Public JWKS or public certificate bundles where confidentiality is not meaningful.
- Runtime traffic keys or protocol-derived ephemeral secrets.

## Non-Goals

- Do not make Tigrbl an object-storage service.
- Do not expose S3 bucket/object CRUD as a core Tigrbl feature under this proposal.
- Do not imply DSSE-KMS applies to direct KMS signing operations.
- Do not replace existing engine providers with material providers.
- Do not promote `kms_key_alias` to a release claim without tests and provider wiring.

## Proposal Interfaces

Sketch only:

```python
class MaterialProviderBase(Protocol):
    spec: MaterialSpec

    async def read_bytes(self) -> bytes: ...
    async def read_text(self, encoding: str = "utf-8") -> str: ...
    async def describe(self) -> MaterialMetadata: ...


class CryptoProviderBase(Protocol):
    spec: CryptoSpec

    async def sign(self, message: bytes, *, algorithm: str) -> bytes: ...
    async def decrypt(self, ciphertext: bytes, *, context: dict[str, str] | None = None) -> bytes: ...
    async def generate_data_key(self, *, context: dict[str, str] | None = None) -> DataKey: ...
```

Example config:

```toml
[tigrbl.materials.jwt_verification]
uri = "s3://security-bucket/tigrbl/jwks/current.json"
required_encryption = "aws:kms"
kms_key_id = "alias/security-material"

[tigrbl.crypto.jwt_signing]
uri = "kms://alias/tigrbl-jwt-signing"
algorithm = "RSASSA_PSS_SHA_256"
```

## Open Questions

- Should material providers live in `tigrbl_core`, `tigrbl_base`, or a new optional package?
- Should `MaterialSpec` be a general Tigrbl primitive or limited to security-sensitive runtime inputs?
- Should `SessionSpec.kms_key_alias` be enforced by engines, material providers, or a separate data-protection policy layer?
- Should S3-backed private key PEM loading be allowed by default, or require an explicit unsafe/local-custody acknowledgement?
- Which provider schemes should be first-class in the initial release: `file`, `env`, `s3`, `kms`, or only `s3` and `kms`?

## Suggested First Slice

1. Add `MaterialSpec`, `MaterialProviderBase`, and registry primitives.
2. Implement `file://` and `s3://` material providers.
3. Require S3 encryption-policy checks for sensitive purposes.
4. Add `CryptoSpec` and `kms://` provider separately for signing and decrypt operations.
5. Wire one narrow consumer first, such as JWT verification material or webhook signing material.
6. Add SSOT ADR, SPEC, feature, claim, test, and evidence rows before treating this as accepted support.
