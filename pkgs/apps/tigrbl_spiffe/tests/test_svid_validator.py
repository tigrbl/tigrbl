import base64
import json

import pytest

from tigrbl_spiffe.identity.svid_validator import SvidValidator


def _jwt(payload, header=None, signature="sig"):
    def encode(value):
        raw = json.dumps(value, separators=(",", ":")).encode("utf-8")
        return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")

    return ".".join(
        [
            encode(header or {"alg": "RS256", "typ": "JWT"}),
            encode(payload),
            signature,
        ]
    ).encode("ascii")


@pytest.mark.asyncio
async def test_validate_rejects_unknown_kind():
    validator = SvidValidator()
    with pytest.raises(ValueError):
        await validator.validate(kind="otp", material=b"token", bundle_id=None, ctx={})


@pytest.mark.asyncio
async def test_validate_requires_bytes_material():
    validator = SvidValidator()
    with pytest.raises(ValueError):
        await validator.validate(kind="jwt", material="token", bundle_id=None, ctx={})


@pytest.mark.asyncio
async def test_validate_enforces_minimum_x509_size():
    validator = SvidValidator()
    with pytest.raises(ValueError):
        await validator.validate(
            kind="x509", material=b"0" * 32, bundle_id=None, ctx={}
        )

    with pytest.raises(ValueError):
        await validator.validate(kind="x509", material=b"1" * 64, bundle_id=None, ctx={})


@pytest.mark.asyncio
async def test_validate_accepts_structural_der_x509_material():
    validator = SvidValidator()
    material = b"\x30\x81\x40" + (b"1" * 64)
    await validator.validate(kind="x509", material=material, bundle_id=None, ctx={})


@pytest.mark.asyncio
async def test_validate_rejects_invalid_pem_x509_material():
    validator = SvidValidator()
    with pytest.raises(ValueError):
        await validator.validate(
            kind="x509",
            material=b"-----BEGIN CERTIFICATE-----\nnot-base64\n",
            bundle_id=None,
            ctx={},
        )


@pytest.mark.asyncio
async def test_validate_accepts_jwt_token_bytes():
    validator = SvidValidator()
    await validator.validate(
        kind="jwt",
        material=_jwt({"sub": "spiffe://example.test/workload", "aud": ["api"], "exp": 200}),
        bundle_id=None,
        ctx={"now": 100, "audiences": ["api"]},
    )


@pytest.mark.asyncio
async def test_validate_rejects_malformed_jwt_token():
    validator = SvidValidator()
    with pytest.raises(ValueError):
        await validator.validate(kind="jwt", material=b"header.payload", bundle_id=None, ctx={})


@pytest.mark.asyncio
async def test_validate_rejects_jwt_alg_none():
    validator = SvidValidator()
    with pytest.raises(ValueError):
        await validator.validate(
            kind="jwt",
            material=_jwt({"sub": "spiffe://example.test/workload"}, header={"alg": "none"}),
            bundle_id=None,
            ctx={},
        )


@pytest.mark.asyncio
async def test_validate_rejects_expired_jwt_token():
    validator = SvidValidator()
    with pytest.raises(ValueError):
        await validator.validate(
            kind="jwt",
            material=_jwt({"sub": "spiffe://example.test/workload", "exp": 99}),
            bundle_id=None,
            ctx={"now": 100},
        )


@pytest.mark.asyncio
async def test_validate_rejects_unmatched_jwt_audience():
    validator = SvidValidator()
    with pytest.raises(ValueError):
        await validator.validate(
            kind="jwt",
            material=_jwt({"sub": "spiffe://example.test/workload", "aud": ["api"]}),
            bundle_id=None,
            ctx={"audiences": ["admin"]},
        )
