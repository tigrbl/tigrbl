# `strict-mtls-origin`

Use this profile when mutual TLS is required at the origin and revocation behavior must be explicit.

## Operator contract

- select with `--deployment-profile strict-mtls-origin`
- pair with `--ocsp-policy strict`
- pair with `--revocation-policy strict`
- keep `--proxy-contract strict`
- keep `--early-data-policy reject`

## Failure posture

- fail closed on missing or invalid client-certificate expectations
- do not certify soft-fail revocation behavior under this profile
- reject mixed-topology ambiguity between trusted and untrusted ingress paths
