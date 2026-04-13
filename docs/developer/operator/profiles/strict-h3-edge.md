# `strict-h3-edge`

Use this profile when Tigrcorn is the HTTP/3 / QUIC edge and Tigrbl exposes the public hardening surface through the CLI adapter.

## Operator contract

- select with `--deployment-profile strict-h3-edge`
- use `--proxy-contract edge-normalized`
- use `--early-data-policy edge-replay-guarded`
- use stable QUIC counters via `--quic-metrics`
- treat `--qlog-dir` as experimental output only

## Failure posture

- reject spoofed or conflicting forwarding state
- surface `425` / replay behavior as explicit policy, not implicit retry magic
- keep QUIC observability stable at the counter layer before publishing richer trace formats
