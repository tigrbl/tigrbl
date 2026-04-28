from __future__ import annotations

import base64
import json
import time
from typing import Any, Optional


_X509_PEM_BEGIN = b"-----BEGIN CERTIFICATE-----"
_X509_PEM_END = b"-----END CERTIFICATE-----"


class SvidValidator:
    """Pluggable SVID validator.
    Keep it independent from kernel atoms; use only ctx extras and provided trust bundles.
    """

    async def validate(
        self,
        *,
        kind: str,
        material: bytes,
        bundle_id: Optional[str],
        ctx: dict[str, Any],
    ) -> None:
        if kind not in {"x509", "jwt", "cwt"}:
            raise ValueError("unsupported SVID kind: %s" % kind)

        if not isinstance(material, (bytes, bytearray)):
            raise ValueError("material must be bytes for storage")

        if kind == "x509":
            _validate_x509_material(bytes(material))
            return

        if kind == "jwt":
            _validate_jwt_svid(bytes(material), ctx)
            return

        if kind == "cwt" and not material:
            raise ValueError("cwt material must not be empty")


def _validate_x509_material(material: bytes) -> None:
    if _X509_PEM_BEGIN in material:
        if _X509_PEM_END not in material:
            raise ValueError("x509 PEM certificate is missing end marker")
        body = material.split(_X509_PEM_BEGIN, 1)[1].split(_X509_PEM_END, 1)[0]
        body = b"".join(body.split())
        try:
            decoded = base64.b64decode(body, validate=True)
        except Exception as exc:
            raise ValueError("x509 PEM certificate body is not valid base64") from exc
        if len(decoded) < 64:
            raise ValueError("x509 certificate body is too small")
        return

    if len(material) < 64:
        raise ValueError("x509 material too small to be a certificate chain")
    if material[0] != 0x30:
        raise ValueError("x509 DER material must start with an ASN.1 sequence")
    _read_der_length(material)


def _read_der_length(material: bytes) -> int:
    if len(material) < 2:
        raise ValueError("x509 DER material is truncated")
    first = material[1]
    if first < 0x80:
        declared = first
        header_len = 2
    else:
        octets = first & 0x7F
        if octets == 0 or octets > 4 or len(material) < 2 + octets:
            raise ValueError("x509 DER length is invalid")
        declared = int.from_bytes(material[2 : 2 + octets], "big")
        header_len = 2 + octets
    if declared <= 0 or header_len + declared > len(material):
        raise ValueError("x509 DER length exceeds material size")
    return header_len + declared


def _validate_jwt_svid(material: bytes, ctx: dict[str, Any]) -> None:
    try:
        token = material.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("jwt material must be utf-8 token") from exc

    parts = token.split(".")
    if len(parts) != 3 or not all(parts):
        raise ValueError("jwt material must contain header, payload, and signature")

    header = _decode_json_segment(parts[0], "jwt header")
    payload = _decode_json_segment(parts[1], "jwt payload")
    if str(header.get("alg", "")).lower() == "none":
        raise ValueError("jwt alg none is not accepted")

    now = int(ctx.get("now", time.time()))
    exp = payload.get("exp")
    if exp is not None and int(exp) <= now:
        raise ValueError("jwt token is expired")
    nbf = payload.get("nbf")
    if nbf is not None and int(nbf) > now:
        raise ValueError("jwt token is not yet valid")

    expected_audiences = ctx.get("audiences") or ctx.get("audience")
    if expected_audiences:
        if isinstance(expected_audiences, str):
            expected = {expected_audiences}
        else:
            expected = {str(item) for item in expected_audiences}
        actual = payload.get("aud")
        actual_set = {actual} if isinstance(actual, str) else {str(item) for item in actual or []}
        if not expected.intersection(actual_set):
            raise ValueError("jwt audience does not match context")


def _decode_json_segment(segment: str, label: str) -> dict[str, Any]:
    padded = segment + "=" * (-len(segment) % 4)
    try:
        raw = base64.urlsafe_b64decode(padded.encode("ascii"))
        decoded = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise ValueError(f"{label} is not valid base64url JSON") from exc
    if not isinstance(decoded, dict):
        raise ValueError(f"{label} must decode to an object")
    return decoded
