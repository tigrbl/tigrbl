# Callback And Webhook Taxonomy Contracts

Planned verification placeholder for the callback/webhook taxonomy correction.

Coverage targets:

- Inbound webhook spec contract.
- Inbound webhook lowering to path-owned HTTP POST custom ops.
- Inbound webhook signature verification and idempotency policy.
- Inbound webhook authoring helper normalization.
- Historical baseline: absence of public `CallbackSpec`. ADR-1210 proposes replacing that assertion with public authoring coverage.
- `POST_EMIT` remains runtime-owned.
- Surface matrix rows for inbound webhook, outbound callback delivery, `TableProfileSpec`, and concrete table profile classes.
- Outbound callback delivery replacement for prior outbound webhook delivery naming.

The successor verification plan is [Webhook and Callback Authoring Verification](webhook-callback-authoring-verification.md).
