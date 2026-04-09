# `strict-h2-origin`

Use this profile when Tigrbl is deployed behind a strict HTTP/2 origin topology with conservative proxy trust and no early-data admission.

## Operator contract

- select with `--deployment-profile strict-h2-origin`
- keep `--proxy-contract strict`
- keep `--early-data-policy reject`
- keep `--origin-static-policy strict`
- use `--http2-max-concurrent-streams` and `--http2-initial-window-size` as the public HTTP/2 control surface

## Failure posture

- reject proxy ambiguity rather than guessing precedence
- reject replay-prone early-data requests
- reject unsafe static/pathsend resolution behavior
