# Tigrcorn Early-Data Contract

This contract freezes early-data admission, replay handling, Retry expectations, and app-visible semantics for the public Tigrcorn-facing surface.

## Normative points

- early data must be rejected by default
- any admission policy must be explicit and profile-bound
- `425 Too Early` and replay-related behavior must be treated as certification-relevant negative behavior
- application-visible semantics must remain explicit rather than implicit runtime magic

This repo governs the contract and public controls; it does not claim to implement Tigrcorn transport internals directly.
