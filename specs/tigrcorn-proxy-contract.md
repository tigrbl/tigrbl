# Tigrcorn Proxy Contract

This contract freezes proxy trust, precedence, normalization, and rejection behavior for the public Tigrcorn-facing control surface in this repository.

## Normative points

- trusted forwarding state must be selected explicitly through the public profile/contract surface
- spoofed or conflicting proxy headers must be rejected rather than merged heuristically
- precedence and normalization behavior must be documented before certification language is published
- mixed-topology behavior must fail closed when trusted and untrusted ingress signals conflict

This repo does not implement Tigrcorn internals directly; it governs the public control surface and certification interpretation around an external runtime dependency.
