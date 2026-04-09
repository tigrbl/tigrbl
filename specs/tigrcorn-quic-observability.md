# Tigrcorn QUIC Observability

This spec freezes the public observability boundary for Tigrcorn-facing QUIC behavior.

## Normative points

- stable counters come first: `connections`, `handshake`, `retry`, `migration`
- qlog-like export is explicitly experimental
- counter names and meanings must remain stable before richer trace formats are treated as certifiable evidence
- QUIC Retry/token/migration remains part of the negative certification corpus
