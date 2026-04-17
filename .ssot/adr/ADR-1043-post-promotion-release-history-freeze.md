# ADR-1043: Post-promotion release-history freeze

﻿
Accepted.

## Decision

After stable release promotion, freeze the promoted release bundle as governed release history and open any subsequent work on a separate development line.

For the current checkpoint this means:

- stable release `0.3.18` remains the frozen current-boundary release history
- promotion-source dev bundle `0.3.18.dev1` remains the exact source evidence for that release
- the working-tree line advances independently to `0.3.19.dev1`
- the active development line may not reuse Tier 3 certification wording without a later governed closure

## Rationale

This prevents the repository from blurring three different states:

1. frozen release history
2. active development metadata
3. next-target planning work

## Consequences

- current-target release evidence stays stable and auditable
- new work can begin without silently reopening the promoted release boundary
- current-boundary certification wording remains attached only to the frozen stable release bundle
