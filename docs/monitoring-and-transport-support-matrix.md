# Monitoring And Transport Support Matrix

## Purpose

This document captures the current-checkout answer to three related questions:

1. What system-status and monitoring support does Tigrbl provide?
2. Does Tigrbl support a live event stream like the illustrated UI?
3. Does Tigrbl support transport health monitoring on a per-transport or per-protocol basis?

This is a repo-grounded implementation summary, not a new SSOT authority document. It reflects the live surfaces present in this checkout.

## Support Legend

- `🟢` supported / implemented
- `🟡` partial / active-line / limited
- `🟠` provisional / tracked but not first-class
- `⚪` not a built-in surface
- `🔧` admin/operator-facing only

## Executive Summary

Tigrbl currently exposes a bounded diagnostics surface centered on `healthz`, `methodz`, `hookz`, and `kernelz`. Those are real framework-owned surfaces. Tigrbl also supports app-defined live event delivery through SSE and WebSocket surfaces.

What it does not currently ship is a built-in monitoring dashboard that reports uptime, active connection counts, throughput, latency by transport, or a live transport-health board like the illustrated UI. Some operator-facing metrics and observability controls exist through the CLI and supported runner integration, but those are configuration and inspection surfaces rather than a framework-native monitoring product.

## Compact Support Matrix

| Capability | Public | Admin | Status | Notes |
|---|---:|---:|---:|---|
| `healthz` | Yes | Yes | 🟢 | Minimal health check, optional DB check |
| `methodz` | Yes | Yes | 🟢 | Operation inventory |
| `hookz` | Yes | Yes | 🟢 | Hook-order diagnostics |
| `kernelz` | Yes | Yes | 🟢 | Kernel-plan diagnostics |
| Health UI page | Yes | Yes | 🟢 | Human-viewable wrapper over health JSON |
| Uptime | No | No | ⚪ | No built-in uptime surface found |
| Connection count | No | No | ⚪ | No built-in live counter found |
| Throughput | No | No | ⚪ | Perf artifacts exist, not live monitoring |
| Live event stream via SSE | App-defined | App-defined | 🟢 | `EventStreamResponse(...)` |
| Live event stream via WebSocket | App-defined | App-defined | 🟢 | `router.websocket(...)` / `app.websocket(...)` |
| Built-in live event console | No | No | ⚪ | The illustrated console is not a shipped framework surface |
| WebSocket text surface | Yes | Yes | 🟢 | Current-target |
| WebSocket JSON-RPC framing | Yes | Yes | 🟡 | Active-line, not frozen current-target |
| WebTransport surface | Limited | Limited | 🟠 | Tracked/provisional, partial specialization |
| Per-transport event model | No | Yes | 🟡 | Registry exists for HTTP/WS/WebTransport |
| Per-transport health endpoint | No | No | ⚪ | No built-in per-proto health surface |
| CLI `doctor` | No | Yes | 🔧 | Route counts, docs paths, engine/server info |
| CLI `capabilities` | No | Yes | 🔧 | CLI/server/engine capability summary |
| Metrics export knobs | No | Yes | 🔧 | StatsD / OTEL / QUIC config surfaces |

## Monitoring Status Matrix

| Surface | Public | Admin/Operator | Implemented now | Notes |
|---|---|---:|---:|---|
| `healthz` | Yes | Yes | Yes | Stable bounded health payload; primarily `{"ok": true}` plus optional DB health details |
| `methodz` | Yes | Yes | Yes | Operation inventory, not runtime health |
| `hookz` | Yes | Yes | Yes | Hook-order diagnostics, not runtime health |
| `kernelz` | Yes | Yes | Yes | Kernel-plan visibility, not live system telemetry |
| Health UI page | Yes | Yes | Yes | Human-viewable page that fetches the JSON health payload |
| Uptime | No built-in surface found | No built-in surface found | No | Not implemented as a built-in endpoint or dashboard |
| Active connections count | No built-in surface found | No built-in surface found | No | No framework-owned live counter surface found |
| Throughput metrics | No built-in live surface found | No built-in live surface found | No | Perf artifacts and benchmarks exist, but not as a built-in live endpoint |
| Per-transport latency/status board | No | No built-in surface found | No | The illustrated UI suggests this, but the repo does not ship it |
| CLI diagnostic summary | No | Yes | Yes | `tigrbl doctor` reports route counts, docs paths, engine capabilities, supported servers, operator controls |
| CLI capabilities summary | No | Yes | Yes | `tigrbl capabilities` reports the CLI/server/engine capability summary |
| Metrics export controls | No | Yes | Yes | Operator-facing config surface only; not a Tigrbl-native dashboard |

## Built-In Diagnostics Matrix

| Endpoint / Surface | Kind | Purpose | Monitoring grade |
|---|---|---|---|
| `/system/healthz` or mounted prefix equivalent | JSON endpoint | Health / DB connectivity check | Minimal health only |
| `/system/methodz` | JSON endpoint | Canonical operation list | Inventory / diagnostics |
| `/system/hookz` | JSON endpoint | Hook execution ordering | Diagnostics |
| `/system/kernelz` | JSON endpoint | Kernel phase-chain plan by operation | Diagnostics |
| `/healthz` | HTML UI | Human-readable page for the health payload | Minimal health UI |

### Diagnostics Explanation

The built-in diagnostics surface is narrow by design. It exposes whether the framework and optional DB dependency are reachable, what methods exist, how hooks are ordered, and how kernel plans were materialized. It does not attempt to be a general runtime-monitoring stack.

That means these surfaces are useful for diagnostics, operator inspection, and supportability, but they should not be described as uptime monitoring, throughput telemetry, or connection-health analytics.

## Live Event Stream Matrix

| Capability | Support level | Implemented now | Notes |
|---|---:|---:|---|
| WebSocket route surface | Current target | Yes | First-class `router.websocket(...)` / `app.websocket(...)` |
| SSE response surface | Current target | Yes | `EventStreamResponse(...)` with `text/event-stream` framing |
| App-defined live event feed over WebSocket | Yes | Yes | A Tigrbl app can expose one |
| App-defined live event feed over SSE | Yes | Yes | A Tigrbl app can expose one |
| Built-in framework live operational event feed | No | No | No built-in system event stream was found |
| Built-in streaming transport-status feed | No | No | Not implemented as a framework-owned monitoring feed |
| AsyncAPI spec emission | Unsupported | No | AsyncAPI generation and `/asyncapi.json` mounting are intentionally unsupported |
| AsyncAPI interactive UI | Unsupported | No | AsyncAPI UI is intentionally unsupported |

### Live Event Stream Explanation

If the question is whether Tigrbl can power a live event stream in an application, the answer is yes. The framework ships the necessary WebSocket and SSE surfaces for an app to build that experience.

If the question is whether Tigrbl itself ships a built-in live operational console that streams router, transport, and engine health updates, the answer in this checkout is no.

## Transport / Proto Support Matrix

| Transport / Proto Surface | Support level in repo | Implemented now | Monitoring / health support |
|---|---:|---:|---|
| HTTP unary / REST | Current target | Yes | Only generic `healthz`-style monitoring |
| HTTP streaming | Current target | Yes | No built-in per-stream health board |
| SSE / WHATWG event stream | Current target | Yes | No built-in per-SSE health monitor |
| WebSocket text surface | Current target | Yes | No built-in per-WebSocket health monitor |
| WebSocket JSON-RPC framing | Active line | Yes | Not certified current-target support |
| WebTransport session surface | Provisional | Partial | Not something to present as fully supported monitoring |
| WebTransport stream/datagram event registry | Tracked | Partial | Event model exists; monitoring surface does not |

### Transport Explanation

The repo distinguishes between supported public/operator surfaces and lower-level runtime tracking. WebSockets and SSE are stronger, clearer public surfaces in the current target. WebTransport is present in the code and governance model, but it remains provisional and partially specialized.

That distinction matters. Presence in runtime code or event-registry rows should not be confused with a claim that the framework ships a complete operational support story for that transport.

## Per-Transport Health Monitoring Matrix

| Detail | HTTP | SSE | WebSocket | WebTransport |
|---|---:|---:|---:|---:|
| Canonical transport event registry exists | Yes | Indirect via HTTP stream model | Yes | Yes |
| Required transport event rows defined | Yes | Partially via stream/SSE model | Yes | Yes |
| Scope validation logic exists | Yes | Yes | Yes | Yes, with QUIC metadata requirement |
| Built-in per-transport health endpoint | No | No | No | No |
| Built-in per-transport latency counters | No | No | No | No |
| Built-in per-transport active connection counts | No | No | No | No |
| Built-in per-transport throughput counters | No | No | No | No |
| Built-in transport health dashboard | No | No | No | No |

### Per-Transport Health Explanation

Tigrbl does have transport-aware internals: event registries, transport event contracts, and transport validation logic. That means the framework understands transport families structurally.

What it does not provide yet is a first-class built-in monitoring layer that publishes those transport states as health summaries, live counters, latencies, throughput, or dashboards on a per-transport basis.

## Admin Vs Public Matrix

| Surface | Publicly consumable | Admin/operator oriented | Notes |
|---|---:|---:|---|
| `healthz` JSON | Yes | Yes | Safe bounded payload by design |
| `healthz` HTML page | Yes | Yes | Human-viewable wrapper over JSON health |
| `methodz` | Yes | Yes | Reveals operation inventory |
| `hookz` | Yes | Yes | More diagnostic/operator flavored |
| `kernelz` | Yes | Yes | Strongly operator/developer flavored |
| `tigrbl doctor` | No | Yes | CLI inspection, not a remote public endpoint |
| `tigrbl capabilities` | No | Yes | CLI inspection, not a remote public endpoint |
| StatsD / OTEL / QUIC metric knobs | No | Yes | Config surface for supported runners |

## What The Illustrated UI Gets Right And Wrong

### What it gets right

- Tigrbl does have WebSocket and SSE support.
- Tigrbl does track transport/runtime concepts deeply enough to model eventful transports.
- Tigrbl does expose a small diagnostics surface that can be mounted for operator inspection.

### What it overstates

- A full system-status dashboard with uptime, connection counts, and throughput.
- A transport-health board with per-protocol latency/health measurements.
- A built-in live event console showing router and engine updates.
- A mature WebTransport operational support story equivalent to the stronger current-target surfaces.

## Practical Interpretation

The most accurate current description is:

- Tigrbl supports bounded diagnostics.
- Tigrbl supports app-defined live event streaming through SSE and WebSocket.
- Tigrbl tracks transport/runtime events structurally.
- Tigrbl does not yet ship a built-in monitoring product for uptime, connection counts, throughput, or per-transport health analytics.

## File Pointers

- Diagnostics router: `pkgs/core/tigrbl_concrete/tigrbl_concrete/system/diagnostics/router.py`
- Health implementation: `pkgs/core/tigrbl/tigrbl/system/diagnostics/healthz.py`
- Kernel diagnostics: `pkgs/core/tigrbl/tigrbl/system/diagnostics/kernelz.py`
- Method diagnostics: `pkgs/core/tigrbl/tigrbl/system/diagnostics/methodz.py`
- Hook diagnostics: `pkgs/core/tigrbl/tigrbl/system/diagnostics/hookz.py`
- Operator WebSocket and SSE docs: `docs/developer/operator/websockets-and-sse.md`
- CLI operator and observability controls: `docs/developer/CLI_REFERENCE.md`
- Current-target operator surface summary: `docs/conformance/CURRENT_TARGET.md`
- Eventful support-level policy: `.ssot/specs/SPEC-2058-support-level-matrix-for-eventful-surfaces.yaml`
- Transport event registry: `pkgs/core/tigrbl_kernel/tigrbl_kernel/transport_events.py`
