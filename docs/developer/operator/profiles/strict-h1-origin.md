# `strict-h1-origin`

Use this profile when Tigrbl is deployed behind a minimal HTTP/1.1 origin topology with no trusted forwarding headers by default.

## Operator contract

- select with `--deployment-profile strict-h1-origin`
- keep `--proxy-contract strict`
- keep `--early-data-policy reject`
- keep `--origin-static-policy strict`
- use stable QUIC counters only when HTTP/3 is enabled upstream; qlog-like export stays experimental

## Failure posture

- reject ambiguous proxy headers
- reject early data at the application boundary
- reject traversal/mutation attempts in static/pathsend flows
- certify only safe failure, not optimistic forwarding behavior
