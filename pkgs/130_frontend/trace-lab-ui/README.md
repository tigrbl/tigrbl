# Trace Lab UI

## Overview

React explorer, event karyogram, timeline and empirical distributions. The Vite bundle uses same-origin endpoints served by the Python lab. See the [public walkthrough](../../170_examples/trace-lab-demo/README.md).

## Getting Started

From the workspace root, run `pnpm install --frozen-lockfile` followed by `pnpm --filter @tigrbl/trace-lab-ui build`. The backend serves the resulting `dist/` directory.

## Usage

The demo explorer reads `GET /demo/trace` and shows the live transport scenario. Collector mode opens **Correlations**, which reads `GET /api/correlations`. Sign in with the configured operator credentials, then enter an `x-correlation-id` to open its waterfall. In the shared tab bar, select **Events** or **Distributions** to explore the timeline, or **Compare** or **Unassigned** to inspect correlation evidence. The **Events** tab carries the selected live correlation across from its waterfall. The capture bar shows the live status and time on every page. Pause and resume the live feed there, or select **Recorded** to choose a synthetic recording. The footer contains the theme and Explorer spacing settings. Paper is the default theme.

In live collector views, paste a full correlation ID into **Find an ID** to look it up across stored traces. Select an ID in the event table or inspector to open its waterfall. When the same ID appears in multiple traces, the event link uses the selected event to find its trace.

The waterfall shows a transaction as one span from begin to commit or rollback. Expand it to see separate rows for the lifecycle boundaries, flushes, queries, and any `PRE_COMMIT` hooks linked to that transaction. The begin row marks the start of the timer. Commit and rollback report the full transaction duration when measured. Collapsing the transaction keeps its event nodes on the same timeline. Phases with multiple hooks also expand into individual rows and collapse into a single timeline. Select a node to inspect its evidence. A shared transaction appears once, with links to the invocations that use it.

The **Round trip** row contains the request, reply, and nested execution lanes. The measured HTTP interval runs from server entry to response start. Collapse the row to see the event nodes together on one timeline.

When the producer enables detailed atom timing, executed atoms appear in their operation's phase alongside hooks. Select an atom to inspect its elapsed time, execution order, and outcome.

## Verification

Run `pnpm --filter @tigrbl/trace-lab-ui lint` for TypeScript checking and `pnpm --filter @tigrbl/trace-lab-ui build` to verify bundling. The backend smoke test checks the served demo bundle. [Workspace verification](../../../README.md#verification)
