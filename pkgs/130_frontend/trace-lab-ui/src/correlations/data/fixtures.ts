import { ADAPTER_VERSION } from '../core/adapter';
import type { RawTraceEventInput, TraceSnapshotInput } from '../core/types';

function iso(baseMs: number, offsetMs: number): string {
  return new Date(baseMs + offsetMs).toISOString();
}

// Deterministic PRNG for reproducible recorded cohorts
function mulberry32(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export interface LiveRunOptions {
  captureId: string;
  startSeq: number;
  baseTimeMs: number;
  scale?: 'standard' | 'load750';
  runIndex?: number;
}

export function generateLiveFourTransportEvents(opts: LiveRunOptions): {
  events: RawTraceEventInput[];
  nextSeq: number;
} {
  const { captureId, baseTimeMs, scale = 'standard', runIndex = 1 } = opts;
  let seq = opts.startSeq;
  const next = () => seq++;
  const events: RawTraceEventInput[] = [];
  const tag = `r${runIndex}`;

  // ---------------------------------------------------------
  // 1. REST: Full request -> invocation -> DB tx -> response
  // ---------------------------------------------------------
  const restCorr1 = `corr-rest-order-${tag}`;
  const restReq1 = `req-http-101-${tag}`;
  const restInv1 = `inv-rest-101-${tag}`;
  const sharedEngSess = `eng-sess-07-${tag}`;
  const sharedTxId = `tx-9041-${tag}`;
  const sRestIn = next();
  events.push({
    seq: sRestIn,
    at: iso(baseTimeMs, 10),
    kind: 'http.request.received',
    protocol: 'rest',
    direction: 'inbound',
    observer: 'edge-gateway',
    correlation_id: restCorr1,
    request_id: restReq1,
    method: 'POST',
    route: '/v1/orders/settle',
    bytes: 648,
    outcome: 'ok',
    // Intentionally include non-allowlisted key to verify adapter strips it
    internal_secret_token: 'strip-me',
  });
  events.push({
    seq: next(),
    at: iso(baseTimeMs, 14),
    kind: 'invocation.started',
    protocol: 'rest',
    direction: 'internal',
    observer: 'order-runtime',
    correlation_id: restCorr1,
    request_id: restReq1,
    invocation_id: restInv1,
    linked_from_seq: sRestIn,
    outcome: 'ok',
  });
  events.push({
    seq: next(),
    at: iso(baseTimeMs, 19),
    kind: 'db.tx.begin',
    protocol: 'rest',
    direction: 'internal',
    observer: 'pg-engine',
    invocation_id: restInv1,
    engine_session_id: sharedEngSess,
    transaction_id: sharedTxId,
    outcome: 'ok',
  });
  events.push({
    seq: next(),
    at: iso(baseTimeMs, 27),
    kind: 'db.tx.query',
    protocol: 'rest',
    direction: 'internal',
    observer: 'pg-engine',
    invocation_id: restInv1,
    engine_session_id: sharedEngSess,
    transaction_id: sharedTxId,
    note: 'UPDATE ledger_entries SET settled = true',
    outcome: 'ok',
  });
  events.push({
    seq: next(),
    at: iso(baseTimeMs, 35),
    kind: 'db.tx.commit',
    protocol: 'rest',
    direction: 'internal',
    observer: 'pg-engine',
    invocation_id: restInv1,
    engine_session_id: sharedEngSess,
    transaction_id: sharedTxId,
    measured_duration_ms: 16.4,
    timing_boundary: 'db_tx_begin_to_commit',
    clock_domain: 'engine_monotonic',
    outcome: 'ok',
  });
  events.push({
    seq: next(),
    at: iso(baseTimeMs, 39),
    kind: 'invocation.completed',
    protocol: 'rest',
    direction: 'internal',
    observer: 'order-runtime',
    correlation_id: restCorr1,
    request_id: restReq1,
    invocation_id: restInv1,
    measured_duration_ms: 25.1,
    timing_boundary: 'invocation_monotonic',
    clock_domain: 'runtime_monotonic',
    outcome: 'ok',
  });
  events.push({
    seq: next(),
    at: iso(baseTimeMs, 43),
    kind: 'http.response.sent',
    protocol: 'rest',
    direction: 'outbound',
    observer: 'edge-gateway',
    correlation_id: restCorr1,
    request_id: restReq1,
    invocation_id: restInv1,
    status_code: 200,
    bytes: 1204,
    measured_duration_ms: 33.2,
    timing_boundary: 'ingress_to_egress_monotonic',
    clock_domain: 'server_monotonic',
    outcome: 'ok',
  });

  // ---------------------------------------------------------
  // 1b. REST: Same correlation_id reused across TWO requests (disambiguation test)
  // ---------------------------------------------------------
  const dupCorr = `corr-shared-8841`;
  for (const [idx, reqId, dur, status] of [
    [0, `req-dup-a-${tag}`, 18.6, 200],
    [1, `req-dup-b-${tag}`, 47.9, 502],
  ] as const) {
    const off = 55 + idx * 40;
    const invId = `inv-dup-${idx}-${tag}`;
    const sIn = next();
    events.push({
      seq: sIn,
      at: iso(baseTimeMs, off),
      kind: 'http.request.received',
      protocol: 'rest',
      direction: 'inbound',
      observer: 'edge-gateway',
      correlation_id: dupCorr,
      request_id: reqId,
      method: 'GET',
      route: idx === 0 ? '/v1/inventory/sku-44' : '/v1/inventory/sku-44?retry=1',
      outcome: 'ok',
    });
    events.push({
      seq: next(),
      at: iso(baseTimeMs, off + 5),
      kind: 'invocation.started',
      protocol: 'rest',
      direction: 'internal',
      observer: 'inventory-runtime',
      correlation_id: dupCorr,
      request_id: reqId,
      invocation_id: invId,
      linked_from_seq: sIn,
      outcome: 'ok',
    });
    events.push({
      seq: next(),
      at: iso(baseTimeMs, off + 18 + idx * 14),
      kind: 'invocation.completed',
      protocol: 'rest',
      direction: 'internal',
      observer: 'inventory-runtime',
      correlation_id: dupCorr,
      request_id: reqId,
      invocation_id: invId,
      measured_duration_ms: dur - 4,
      timing_boundary: 'invocation_monotonic',
      clock_domain: 'runtime_monotonic',
      outcome: status >= 400 ? 'error' : 'ok',
    });
    events.push({
      seq: next(),
      at: iso(baseTimeMs, off + 22 + idx * 16),
      kind: 'http.response.sent',
      protocol: 'rest',
      direction: 'outbound',
      observer: 'edge-gateway',
      correlation_id: dupCorr,
      request_id: reqId,
      invocation_id: invId,
      status_code: status,
      measured_duration_ms: dur,
      timing_boundary: 'ingress_to_egress_monotonic',
      clock_domain: 'server_monotonic',
      outcome: status >= 400 ? 'error' : 'ok',
    });
  }

  // ---------------------------------------------------------
  // 2. HTTP JSON-RPC: Batch items + shared DB transaction + notification
  // ---------------------------------------------------------
  const rpcCorr = `corr-rpc-batch-${tag}`;
  const rpcReq = `req-rpc-301-${tag}`;
  const rpcInv = `inv-rpc-301-${tag}`;
  const sRpcDoc = next();
  events.push({
    seq: sRpcDoc,
    at: iso(baseTimeMs, 110),
    kind: 'rpc.document.received',
    protocol: 'jsonrpc',
    direction: 'inbound',
    observer: 'rpc-gateway',
    correlation_id: rpcCorr,
    request_id: rpcReq,
    method: 'batch[2]',
    route: '/rpc',
    bytes: 912,
    outcome: 'ok',
  });
  events.push({
    seq: next(),
    at: iso(baseTimeMs, 114),
    kind: 'rpc.batch.item.invoked',
    protocol: 'jsonrpc',
    direction: 'internal',
    observer: 'rpc-dispatcher',
    correlation_id: rpcCorr,
    request_id: rpcReq,
    rpc_id: 9007199254740991, // numeric wire ID preserved losslessly as string
    rpc_item_index: 0,
    invocation_id: rpcInv,
    linked_from_seq: sRpcDoc,
    method: 'ledger.verify',
    outcome: 'ok',
  });
  events.push({
    seq: next(),
    at: iso(baseTimeMs, 118),
    kind: 'db.tx.query',
    protocol: 'jsonrpc',
    direction: 'internal',
    observer: 'pg-engine',
    correlation_id: rpcCorr,
    request_id: rpcReq,
    invocation_id: rpcInv,
    engine_session_id: sharedEngSess,
    transaction_id: sharedTxId, // Shared transaction with REST order settlement!
    note: 'SELECT balance FROM ledger_entries',
    outcome: 'ok',
  });
  events.push({
    seq: next(),
    at: iso(baseTimeMs, 126),
    kind: 'rpc.batch.item.completed',
    protocol: 'jsonrpc',
    direction: 'internal',
    observer: 'rpc-dispatcher',
    correlation_id: rpcCorr,
    request_id: rpcReq,
    rpc_id: 9007199254740991,
    rpc_item_index: 0,
    invocation_id: rpcInv,
    measured_duration_ms: 11.8,
    timing_boundary: 'invocation_monotonic',
    clock_domain: 'runtime_monotonic',
    outcome: 'ok',
  });
  events.push({
    seq: next(),
    at: iso(baseTimeMs, 121),
    kind: 'rpc.batch.item.invoked',
    protocol: 'jsonrpc',
    direction: 'internal',
    observer: 'rpc-dispatcher',
    correlation_id: rpcCorr,
    request_id: rpcReq,
    rpc_id: 42,
    rpc_item_index: 1,
    invocation_id: `inv-rpc-302-${tag}`,
    linked_from_seq: sRpcDoc,
    method: 'ledger.snapshot',
    outcome: 'ok',
  });
  events.push({
    seq: next(),
    at: iso(baseTimeMs, 134),
    kind: 'rpc.batch.item.completed',
    protocol: 'jsonrpc',
    direction: 'internal',
    observer: 'rpc-dispatcher',
    correlation_id: rpcCorr,
    request_id: rpcReq,
    rpc_id: 42,
    rpc_item_index: 1,
    invocation_id: `inv-rpc-302-${tag}`,
    measured_duration_ms: 13.1,
    timing_boundary: 'invocation_monotonic',
    clock_domain: 'runtime_monotonic',
    outcome: 'ok',
  });
  events.push({
    seq: next(),
    at: iso(baseTimeMs, 139),
    kind: 'rpc.response.sent',
    protocol: 'jsonrpc',
    direction: 'outbound',
    observer: 'rpc-gateway',
    correlation_id: rpcCorr,
    request_id: rpcReq,
    status_code: 200,
    bytes: 1520,
    measured_duration_ms: 29.0,
    timing_boundary: 'ingress_to_egress_monotonic',
    clock_domain: 'server_monotonic',
    outcome: 'ok',
  });

  // JSON-RPC Notification (No reply expected)
  const rpcNotifCorr = `corr-rpc-notify-${tag}`;
  events.push({
    seq: next(),
    at: iso(baseTimeMs, 146),
    kind: 'rpc.notification.received',
    protocol: 'jsonrpc',
    direction: 'inbound',
    observer: 'rpc-gateway',
    correlation_id: rpcNotifCorr,
    request_id: `req-rpc-notif-${tag}`,
    rpc_is_notification: true,
    method: 'audit.heartbeat',
    outcome: 'ok',
  });
  events.push({
    seq: next(),
    at: iso(baseTimeMs, 151),
    kind: 'invocation.completed',
    protocol: 'jsonrpc',
    direction: 'internal',
    observer: 'rpc-dispatcher',
    correlation_id: rpcNotifCorr,
    request_id: `req-rpc-notif-${tag}`,
    invocation_id: `inv-rpc-notif-${tag}`,
    rpc_is_notification: true,
    measured_duration_ms: 4.5,
    timing_boundary: 'invocation_monotonic',
    clock_domain: 'runtime_monotonic',
    outcome: 'ok',
  });

  // ---------------------------------------------------------
  // 3. WebSocket: Publisher -> Broker fan-out -> 2 Subscriber correlations
  // ---------------------------------------------------------
  const wsPubCorr = `corr-ws-pub-${tag}`;
  const wsPubSock = `ws-sock-pub-1`;
  const wsPubReqSess = `req-sess-alpha`;
  const wsPubInv = `inv-ws-pub-${tag}`;
  const wsSubCorrA = `corr-ws-subA-${tag}`;
  const wsSubCorrB = `corr-ws-subB-${tag}`;

  events.push({
    seq: next(),
    at: iso(baseTimeMs, 165),
    kind: 'ws.session.opened',
    protocol: 'websocket',
    direction: 'internal',
    observer: 'ws-hub',
    correlation_id: wsPubCorr,
    transport_session_id: wsPubSock,
    requester_session_id: wsPubReqSess,
    outcome: 'ok',
  });
  const sWsIn = next();
  events.push({
    seq: sWsIn,
    at: iso(baseTimeMs, 170),
    kind: 'ws.frame.received',
    protocol: 'websocket',
    direction: 'inbound',
    observer: 'ws-hub',
    correlation_id: wsPubCorr,
    transport_session_id: wsPubSock,
    requester_session_id: wsPubReqSess,
    topic: 'orders.filled',
    bytes: 412,
    outcome: 'ok',
  });
  events.push({
    seq: next(),
    at: iso(baseTimeMs, 174),
    kind: 'invocation.started',
    protocol: 'websocket',
    direction: 'internal',
    observer: 'ws-runtime',
    correlation_id: wsPubCorr,
    transport_session_id: wsPubSock,
    invocation_id: wsPubInv,
    linked_from_seq: sWsIn,
    outcome: 'ok',
  });
  // Broker publication carries origin_correlation_id WITHOUT top-level correlation_id!
  events.push({
    seq: next(),
    at: iso(baseTimeMs, 180),
    kind: 'ws.broker.publish',
    protocol: 'websocket',
    direction: 'internal',
    observer: 'broker-router',
    origin_correlation_id: wsPubCorr,
    invocation_id: wsPubInv,
    topic: 'orders.filled',
    bytes: 412,
    outcome: 'ok',
  });
  events.push({
    seq: next(),
    at: iso(baseTimeMs, 184),
    kind: 'ws.frame.sent',
    protocol: 'websocket',
    direction: 'outbound',
    observer: 'ws-hub',
    correlation_id: wsPubCorr,
    transport_session_id: wsPubSock,
    measured_duration_ms: 14.2,
    timing_boundary: 'ingress_to_egress_monotonic',
    clock_domain: 'server_monotonic',
    note: 'publish ack',
    outcome: 'ok',
  });

  // Receiving subscription A (separate carrier socket & receiving_correlation_id)
  events.push({
    seq: next(),
    at: iso(baseTimeMs, 187),
    kind: 'ws.subscription.attached',
    protocol: 'websocket',
    direction: 'internal',
    observer: 'broker-router',
    correlation_id: wsSubCorrA,
    transport_session_id: 'ws-sock-sub-A',
    requester_session_id: 'req-sess-desk-1',
    subscription_id: 'sub-orders-desk',
    attachment_generation: 'gen-3',
    destination_id: 'dst-desk-alpha',
    topic: 'orders.filled',
    outcome: 'ok',
  });
  events.push({
    seq: next(),
    at: iso(baseTimeMs, 193),
    kind: 'ws.broker.delivery',
    protocol: 'websocket',
    direction: 'outbound',
    observer: 'ws-hub',
    receiving_correlation_id: wsSubCorrA,
    origin_correlation_id: wsPubCorr,
    transport_session_id: 'ws-sock-sub-A',
    requester_session_id: 'req-sess-desk-1',
    subscription_id: 'sub-orders-desk',
    attachment_generation: 'gen-3',
    destination_id: 'dst-desk-alpha',
    topic: 'orders.filled',
    bytes: 412,
    measured_duration_ms: 12.6,
    timing_boundary: 'ingress_to_egress_monotonic',
    clock_domain: 'server_monotonic',
    outcome: 'ok',
  });

  // Receiving subscription B (second fan-out branch)
  events.push({
    seq: next(),
    at: iso(baseTimeMs, 196),
    kind: 'ws.broker.delivery',
    protocol: 'websocket',
    direction: 'outbound',
    observer: 'ws-hub',
    receiving_correlation_id: wsSubCorrB,
    origin_correlation_id: wsPubCorr,
    transport_session_id: 'ws-sock-sub-B',
    requester_session_id: 'req-sess-risk-2',
    subscription_id: 'sub-orders-risk',
    attachment_generation: 'gen-5',
    destination_id: 'dst-risk-monitor',
    topic: 'orders.filled',
    bytes: 412,
    measured_duration_ms: 15.9,
    timing_boundary: 'ingress_to_egress_monotonic',
    clock_domain: 'server_monotonic',
    outcome: 'ok',
  });

  // ---------------------------------------------------------
  // 4. WebTransport: ONE QUIC connection hosting TWO sibling sessions
  // ---------------------------------------------------------
  const quicConn = `quic-conn-770-${tag}`;
  const wtCorrA = `corr-wt-sessA-${tag}`;
  const wtSessA = `wt-sess-101-${tag}`;
  const wtCorrB = `corr-wt-sessB-${tag}`;
  const wtSessB = `wt-sess-102-${tag}`;

  // Session A
  const sWtA = next();
  events.push({
    seq: sWtA,
    at: iso(baseTimeMs, 210),
    kind: 'wt.quic.connected',
    protocol: 'webtransport',
    direction: 'internal',
    observer: 'quic-edge',
    correlation_id: wtCorrA,
    quic_connection_id: quicConn,
    transport_session_id: wtSessA,
    outcome: 'ok',
  });
  events.push({
    seq: next(),
    at: iso(baseTimeMs, 215),
    kind: 'wt.session.opened',
    protocol: 'webtransport',
    direction: 'inbound',
    observer: 'quic-edge',
    correlation_id: wtCorrA,
    quic_connection_id: quicConn,
    transport_session_id: wtSessA,
    outcome: 'ok',
  });
  // Session A Stream 1
  const sStreamA1 = next();
  events.push({
    seq: sStreamA1,
    at: iso(baseTimeMs, 222),
    kind: 'wt.stream.opened',
    protocol: 'webtransport',
    direction: 'inbound',
    observer: 'quic-edge',
    correlation_id: wtCorrA,
    quic_connection_id: quicConn,
    transport_session_id: wtSessA,
    stream_id: 'bidi-4',
    stream_correlation_id: `scorr-a1-${tag}`,
    linked_from_seq: sWtA,
    outcome: 'ok',
  });
  events.push({
    seq: next(),
    at: iso(baseTimeMs, 226),
    kind: 'wt.stream.frame.received',
    protocol: 'webtransport',
    direction: 'inbound',
    observer: 'quic-edge',
    correlation_id: wtCorrA,
    quic_connection_id: quicConn,
    transport_session_id: wtSessA,
    stream_id: 'bidi-4',
    stream_correlation_id: `scorr-a1-${tag}`,
    invocation_id: `inv-wt-a1-${tag}`,
    bytes: 1024,
    outcome: 'ok',
  });
  // Datagram explicitly attached to stream-a1
  events.push({
    seq: next(),
    at: iso(baseTimeMs, 232),
    kind: 'wt.datagram.received',
    protocol: 'webtransport',
    direction: 'inbound',
    observer: 'quic-edge',
    correlation_id: wtCorrA,
    quic_connection_id: quicConn,
    transport_session_id: wtSessA,
    stream_id: 'bidi-4',
    stream_correlation_id: `scorr-a1-${tag}`,
    datagram_id: `dg-attached-1-${tag}`,
    bytes: 96,
    note: 'Explicitly linked to bidi-4 via stream_correlation_id',
    outcome: 'ok',
  });
  events.push({
    seq: next(),
    at: iso(baseTimeMs, 241),
    kind: 'wt.stream.frame.sent',
    protocol: 'webtransport',
    direction: 'outbound',
    observer: 'quic-edge',
    correlation_id: wtCorrA,
    quic_connection_id: quicConn,
    transport_session_id: wtSessA,
    stream_id: 'bidi-4',
    stream_correlation_id: `scorr-a1-${tag}`,
    invocation_id: `inv-wt-a1-${tag}`,
    measured_duration_ms: 19.3,
    timing_boundary: 'ingress_to_egress_monotonic',
    clock_domain: 'quic_monotonic',
    bytes: 2048,
    outcome: 'ok',
  });
  events.push({
    seq: next(),
    at: iso(baseTimeMs, 245),
    kind: 'wt.stream.closed',
    protocol: 'webtransport',
    direction: 'internal',
    observer: 'quic-edge',
    correlation_id: wtCorrA,
    quic_connection_id: quicConn,
    transport_session_id: wtSessA,
    stream_id: 'bidi-4',
    stream_correlation_id: `scorr-a1-${tag}`,
    measured_duration_ms: 23.1,
    timing_boundary: 'invocation_monotonic',
    clock_domain: 'quic_monotonic',
    outcome: 'ok',
  });

  // Session A Stream 2
  events.push({
    seq: next(),
    at: iso(baseTimeMs, 230),
    kind: 'wt.stream.opened',
    protocol: 'webtransport',
    direction: 'inbound',
    observer: 'quic-edge',
    correlation_id: wtCorrA,
    quic_connection_id: quicConn,
    transport_session_id: wtSessA,
    stream_id: 'bidi-8',
    stream_correlation_id: `scorr-a2-${tag}`,
    linked_from_seq: sWtA,
    outcome: 'ok',
  });
  events.push({
    seq: next(),
    at: iso(baseTimeMs, 256),
    kind: 'wt.stream.frame.sent',
    protocol: 'webtransport',
    direction: 'outbound',
    observer: 'quic-edge',
    correlation_id: wtCorrA,
    quic_connection_id: quicConn,
    transport_session_id: wtSessA,
    stream_id: 'bidi-8',
    stream_correlation_id: `scorr-a2-${tag}`,
    measured_duration_ms: 26.0,
    timing_boundary: 'ingress_to_egress_monotonic',
    clock_domain: 'quic_monotonic',
    outcome: 'ok',
  });

  // Session A separate Datagrams lane (NOT attached to any stream)
  for (let d = 1; d <= 3; d++) {
    events.push({
      seq: next(),
      at: iso(baseTimeMs, 224 + d * 11),
      kind: d % 2 === 1 ? 'wt.datagram.received' : 'wt.datagram.sent',
      protocol: 'webtransport',
      direction: d % 2 === 1 ? 'inbound' : 'outbound',
      observer: 'quic-edge',
      correlation_id: wtCorrA,
      quic_connection_id: quicConn,
      transport_session_id: wtSessA,
      datagram_id: `dg-a-${d}-${tag}`,
      bytes: 64 + d * 16,
      outcome: 'ok',
    });
  }

  // Session B (Sibling on the SAME QUIC connection!)
  const sWtB = next();
  events.push({
    seq: sWtB,
    at: iso(baseTimeMs, 260),
    kind: 'wt.session.opened',
    protocol: 'webtransport',
    direction: 'inbound',
    observer: 'quic-edge',
    correlation_id: wtCorrB,
    quic_connection_id: quicConn,
    transport_session_id: wtSessB,
    outcome: 'ok',
  });
  events.push({
    seq: next(),
    at: iso(baseTimeMs, 268),
    kind: 'wt.stream.opened',
    protocol: 'webtransport',
    direction: 'inbound',
    observer: 'quic-edge',
    correlation_id: wtCorrB,
    quic_connection_id: quicConn,
    transport_session_id: wtSessB,
    stream_id: 'bidi-12',
    stream_correlation_id: `scorr-b1-${tag}`,
    linked_from_seq: sWtB,
    outcome: 'ok',
  });
  events.push({
    seq: next(),
    at: iso(baseTimeMs, 286),
    kind: 'wt.stream.frame.sent',
    protocol: 'webtransport',
    direction: 'outbound',
    observer: 'quic-edge',
    correlation_id: wtCorrB,
    quic_connection_id: quicConn,
    transport_session_id: wtSessB,
    stream_id: 'bidi-12',
    stream_correlation_id: `scorr-b1-${tag}`,
    measured_duration_ms: 17.8,
    timing_boundary: 'ingress_to_egress_monotonic',
    clock_domain: 'quic_monotonic',
    outcome: 'ok',
  });
  events.push({
    seq: next(),
    at: iso(baseTimeMs, 290),
    kind: 'wt.stream.closed',
    protocol: 'webtransport',
    direction: 'internal',
    observer: 'quic-edge',
    correlation_id: wtCorrB,
    quic_connection_id: quicConn,
    transport_session_id: wtSessB,
    stream_id: 'bidi-12',
    stream_correlation_id: `scorr-b1-${tag}`,
    measured_duration_ms: 21.4,
    timing_boundary: 'invocation_monotonic',
    clock_domain: 'quic_monotonic',
    outcome: 'ok',
  });
  for (let d = 1; d <= 2; d++) {
    events.push({
      seq: next(),
      at: iso(baseTimeMs, 272 + d * 12),
      kind: 'wt.datagram.received',
      protocol: 'webtransport',
      direction: 'inbound',
      observer: 'quic-edge',
      correlation_id: wtCorrB,
      quic_connection_id: quicConn,
      transport_session_id: wtSessB,
      datagram_id: `dg-b-${d}-${tag}`,
      bytes: 128,
      outcome: 'ok',
    });
  }

  // ---------------------------------------------------------
  // 5. Unassigned events & Unknown event kind
  // ---------------------------------------------------------
  events.push({
    seq: next(),
    at: iso(baseTimeMs, 296),
    kind: 'http.request.received',
    protocol: 'rest',
    direction: 'inbound',
    observer: 'edge-gateway',
    request_id: `req-uncorr-health-${tag}`,
    method: 'GET',
    route: '/healthz',
    outcome: 'ok',
  });
  // Ambiguous DB row: carries duplicated correlation_id without request_id discriminator
  events.push({
    seq: next(),
    at: iso(baseTimeMs, 298),
    kind: 'db.tx.query',
    protocol: 'rest',
    direction: 'internal',
    observer: 'pg-engine',
    correlation_id: dupCorr,
    engine_session_id: `eng-ambig-${tag}`,
    transaction_id: `tx-ambig-${tag}`,
    note: 'Missing request_id discriminator — ambiguous across 2 requests',
    outcome: 'ok',
  });
  events.push({
    seq: next(),
    at: iso(baseTimeMs, 302),
    kind: 'custom.wire.probe',
    protocol: 'webtransport',
    direction: 'unknown',
    observer: 'quic-edge',
    correlation_id: wtCorrA,
    transport_session_id: wtSessA,
    quic_connection_id: quicConn,
    note: 'Additive producer probe event',
    outcome: 'unknown',
  });

  // Optional burst to exercise >= 750 live rows cleanly
  if (scale === 'load750') {
    const rng = mulberry32(baseTimeMs % 100000);
    const protocols: Array<'rest' | 'jsonrpc' | 'websocket' | 'webtransport'> = [
      'rest',
      'jsonrpc',
      'websocket',
      'webtransport',
    ];
    for (let i = 0; i < 160; i++) {
      const proto = protocols[i % 4];
      const offset = 320 + i * 18;
      const lat = Number((8 + rng() * 55 + (i % 19 === 0 ? 75 : 0)).toFixed(1));
      const corr = `corr-burst-${proto}-${tag}-${String(i).padStart(3, '0')}`;
      const reqId = `req-b-${tag}-${i}`;
      const invId = `inv-b-${tag}-${i}`;

      if (proto === 'rest') {
        const s0 = next();
        events.push({
          seq: s0,
          at: iso(baseTimeMs, offset),
          kind: 'http.request.received',
          protocol: 'rest',
          direction: 'inbound',
          observer: 'edge-gateway',
          correlation_id: corr,
          request_id: reqId,
          method: 'POST',
          route: '/v1/quotes',
          outcome: 'ok',
        });
        events.push({
          seq: next(),
          at: iso(baseTimeMs, offset + 3),
          kind: 'invocation.started',
          protocol: 'rest',
          direction: 'internal',
          observer: 'quote-runtime',
          correlation_id: corr,
          request_id: reqId,
          invocation_id: invId,
          linked_from_seq: s0,
          outcome: 'ok',
        });
        events.push({
          seq: next(),
          at: iso(baseTimeMs, offset + 7),
          kind: 'db.tx.commit',
          protocol: 'rest',
          direction: 'internal',
          observer: 'pg-engine',
          invocation_id: invId,
          engine_session_id: `eng-pool-${i % 8}`,
          transaction_id: `tx-b-${tag}-${i}`,
          measured_duration_ms: Number((lat * 0.42).toFixed(1)),
          timing_boundary: 'db_tx_begin_to_commit',
          clock_domain: 'engine_monotonic',
          outcome: 'ok',
        });
        events.push({
          seq: next(),
          at: iso(baseTimeMs, offset + 11),
          kind: 'invocation.completed',
          protocol: 'rest',
          direction: 'internal',
          observer: 'quote-runtime',
          correlation_id: corr,
          request_id: reqId,
          invocation_id: invId,
          measured_duration_ms: Number((lat * 0.85).toFixed(1)),
          timing_boundary: 'invocation_monotonic',
          clock_domain: 'runtime_monotonic',
          outcome: 'ok',
        });
        events.push({
          seq: next(),
          at: iso(baseTimeMs, offset + 13),
          kind: 'http.response.sent',
          protocol: 'rest',
          direction: 'outbound',
          observer: 'edge-gateway',
          correlation_id: corr,
          request_id: reqId,
          invocation_id: invId,
          status_code: i % 27 === 0 ? 500 : 200,
          measured_duration_ms: lat,
          timing_boundary: 'ingress_to_egress_monotonic',
          clock_domain: 'server_monotonic',
          outcome: i % 27 === 0 ? 'error' : 'ok',
        });
      } else if (proto === 'jsonrpc') {
        const s0 = next();
        events.push({
          seq: s0,
          at: iso(baseTimeMs, offset),
          kind: 'rpc.document.received',
          protocol: 'jsonrpc',
          direction: 'inbound',
          observer: 'rpc-gateway',
          correlation_id: corr,
          request_id: reqId,
          rpc_id: 1000 + i,
          outcome: 'ok',
        });
        events.push({
          seq: next(),
          at: iso(baseTimeMs, offset + 4),
          kind: 'rpc.batch.item.invoked',
          protocol: 'jsonrpc',
          direction: 'internal',
          observer: 'rpc-dispatcher',
          correlation_id: corr,
          request_id: reqId,
          rpc_id: 1000 + i,
          rpc_item_index: 0,
          invocation_id: invId,
          linked_from_seq: s0,
          outcome: 'ok',
        });
        events.push({
          seq: next(),
          at: iso(baseTimeMs, offset + 10),
          kind: 'rpc.batch.item.completed',
          protocol: 'jsonrpc',
          direction: 'internal',
          observer: 'rpc-dispatcher',
          correlation_id: corr,
          request_id: reqId,
          rpc_id: 1000 + i,
          rpc_item_index: 0,
          invocation_id: invId,
          measured_duration_ms: Number((lat * 0.78).toFixed(1)),
          timing_boundary: 'invocation_monotonic',
          clock_domain: 'runtime_monotonic',
          outcome: 'ok',
        });
        events.push({
          seq: next(),
          at: iso(baseTimeMs, offset + 13),
          kind: 'rpc.response.sent',
          protocol: 'jsonrpc',
          direction: 'outbound',
          observer: 'rpc-gateway',
          correlation_id: corr,
          request_id: reqId,
          status_code: 200,
          measured_duration_ms: lat,
          timing_boundary: 'ingress_to_egress_monotonic',
          clock_domain: 'server_monotonic',
          outcome: 'ok',
        });
      } else if (proto === 'websocket') {
        const sess = `ws-pool-${i % 6}`;
        events.push({
          seq: next(),
          at: iso(baseTimeMs, offset),
          kind: 'ws.frame.received',
          protocol: 'websocket',
          direction: 'inbound',
          observer: 'ws-hub',
          correlation_id: corr,
          transport_session_id: sess,
          topic: 'ticks.l2',
          outcome: 'ok',
        });
        events.push({
          seq: next(),
          at: iso(baseTimeMs, offset + 4),
          kind: 'invocation.completed',
          protocol: 'websocket',
          direction: 'internal',
          observer: 'ws-runtime',
          correlation_id: corr,
          transport_session_id: sess,
          invocation_id: invId,
          measured_duration_ms: Number((lat * 0.7).toFixed(1)),
          timing_boundary: 'invocation_monotonic',
          clock_domain: 'runtime_monotonic',
          outcome: 'ok',
        });
        events.push({
          seq: next(),
          at: iso(baseTimeMs, offset + 9),
          kind: 'ws.frame.sent',
          protocol: 'websocket',
          direction: 'outbound',
          observer: 'ws-hub',
          correlation_id: corr,
          transport_session_id: sess,
          measured_duration_ms: lat,
          timing_boundary: 'ingress_to_egress_monotonic',
          clock_domain: 'server_monotonic',
          outcome: 'ok',
        });
      } else {
        const sess = `wt-pool-${i % 4}`;
        const qConn = `quic-pool-${i % 2}`;
        const s0 = next();
        events.push({
          seq: s0,
          at: iso(baseTimeMs, offset),
          kind: 'wt.stream.opened',
          protocol: 'webtransport',
          direction: 'inbound',
          observer: 'quic-edge',
          correlation_id: corr,
          quic_connection_id: qConn,
          transport_session_id: sess,
          stream_id: `bidi-${i * 4}`,
          stream_correlation_id: `sc-${tag}-${i}`,
          outcome: 'ok',
        });
        events.push({
          seq: next(),
          at: iso(baseTimeMs, offset + 6),
          kind: 'wt.stream.frame.sent',
          protocol: 'webtransport',
          direction: 'outbound',
          observer: 'quic-edge',
          correlation_id: corr,
          quic_connection_id: qConn,
          transport_session_id: sess,
          stream_id: `bidi-${i * 4}`,
          stream_correlation_id: `sc-${tag}-${i}`,
          measured_duration_ms: lat,
          timing_boundary: 'ingress_to_egress_monotonic',
          clock_domain: 'quic_monotonic',
          outcome: 'ok',
        });
        events.push({
          seq: next(),
          at: iso(baseTimeMs, offset + 9),
          kind: 'wt.datagram.received',
          protocol: 'webtransport',
          direction: 'inbound',
          observer: 'quic-edge',
          correlation_id: corr,
          quic_connection_id: qConn,
          transport_session_id: sess,
          datagram_id: `dg-b-${tag}-${i}`,
          outcome: 'ok',
        });
      }
    }
  }

  return { events, nextSeq: seq };
}

export type RecordedFixtureId = 'edge-cases' | 'scale-10k';

export function buildRecordedEdgeCasesFixture(): TraceSnapshotInput {
  const baseMs = Date.parse('2026-11-23T10:03:20.000Z');
  const rng = mulberry32(20261123);
  let seq = 1001; // Sequence floor 1000 -> earlier seqs are evicted!
  const next = () => seq++;
  const events: RawTraceEventInput[] = [];

  // 1. Edge case: Incomplete REST response ("Reply not observed")
  const sInc = next();
  events.push({
    seq: sInc,
    at: iso(baseMs, 10),
    kind: 'http.request.received',
    protocol: 'rest',
    direction: 'inbound',
    observer: 'edge-gateway',
    correlation_id: 'corr-rec-incomplete-01',
    request_id: 'req-rec-inc-01',
    method: 'POST',
    route: '/v1/settlement/commit',
    outcome: 'ok',
  });
  events.push({
    seq: next(),
    at: iso(baseMs, 18),
    kind: 'invocation.started',
    protocol: 'rest',
    direction: 'internal',
    observer: 'order-runtime',
    correlation_id: 'corr-rec-incomplete-01',
    request_id: 'req-rec-inc-01',
    invocation_id: 'inv-rec-inc-01',
    linked_from_seq: sInc,
    outcome: 'incomplete',
    note: 'Worker terminated before writing HTTP reply',
  });

  // 2. Edge case: Skewed clocks ("Clock order uncertain" without flipping or deriving duration)
  const sSkew = next();
  events.push({
    seq: sSkew,
    at: iso(baseMs, 35),
    kind: 'http.request.received',
    protocol: 'rest',
    direction: 'inbound',
    observer: 'edge-west',
    correlation_id: 'corr-rec-skew-02',
    request_id: 'req-rec-skew-02',
    source_started_at: iso(baseMs, 42), // skewed ahead by +7ms
    source_ended_at: iso(baseMs, 34), // appears before start!
    clock_domain: 'mixed',
    method: 'PUT',
    route: '/v1/positions/sync',
    outcome: 'ok',
  });
  events.push({
    seq: next(),
    at: iso(baseMs, 32), // Recorded earlier than request due to unsynced host clock
    kind: 'invocation.started',
    protocol: 'rest',
    direction: 'internal',
    observer: 'worker-east',
    correlation_id: 'corr-rec-skew-02',
    request_id: 'req-rec-skew-02',
    invocation_id: 'inv-rec-skew-02',
    linked_from_seq: sSkew,
    source_started_at: iso(baseMs, 39),
    source_ended_at: iso(baseMs, 31),
    clock_domain: 'mixed',
    outcome: 'ok',
  });
  events.push({
    seq: next(),
    at: iso(baseMs, 48),
    kind: 'http.response.sent',
    protocol: 'rest',
    direction: 'outbound',
    observer: 'edge-west',
    correlation_id: 'corr-rec-skew-02',
    request_id: 'req-rec-skew-02',
    invocation_id: 'inv-rec-skew-02',
    status_code: 200,
    outcome: 'ok',
  });

  // 3. Edge case: Evicted upstream endpoint + external peer chip
  events.push({
    seq: next(),
    at: iso(baseMs, 60),
    kind: 'http.request.received',
    protocol: 'rest',
    direction: 'inbound',
    observer: 'edge-gateway',
    correlation_id: 'corr-rec-evicted-03',
    request_id: 'req-rec-ev-03',
    evicted_endpoint_id: 'corr-upstream-seq-940',
    method: 'GET',
    route: '/v1/orders/trace',
    outcome: 'ok',
  });
  events.push({
    seq: next(),
    at: iso(baseMs, 74),
    kind: 'http.response.sent',
    protocol: 'rest',
    direction: 'outbound',
    observer: 'edge-gateway',
    correlation_id: 'corr-rec-evicted-03',
    request_id: 'req-rec-ev-03',
    external_endpoint_label: 'partner-clearinghouse',
    status_code: 200,
    outcome: 'ok',
  });

  // 4. Shared DB transaction across 2 distinct correlations (counted ONCE in Compare)
  const sharedTxKeySess = 'eng-rec-01';
  const sharedTxId = 'tx-shared-55';
  for (const [idx, corr, reqId, invId, proto] of [
    [0, 'corr-rec-tx-alpha', 'req-tx-a', 'inv-tx-a', 'rest'],
    [1, 'corr-rec-tx-beta', 'req-tx-b', 'inv-tx-b', 'jsonrpc'],
  ] as const) {
    const off = 90 + idx * 14;
    const s0 = next();
    events.push({
      seq: s0,
      at: iso(baseMs, off),
      kind: proto === 'rest' ? 'http.request.received' : 'rpc.document.received',
      protocol: proto,
      direction: 'inbound',
      observer: proto === 'rest' ? 'edge-gateway' : 'rpc-gateway',
      correlation_id: corr,
      request_id: reqId,
      method: proto === 'rest' ? 'POST' : 'tx.join',
      route: proto === 'rest' ? '/v1/tx/join' : '/rpc',
      outcome: 'ok',
    });
    events.push({
      seq: next(),
      at: iso(baseMs, off + 3),
      kind: 'invocation.started',
      protocol: proto,
      direction: 'internal',
      observer: 'runtime',
      correlation_id: corr,
      request_id: reqId,
      invocation_id: invId,
      linked_from_seq: s0,
      outcome: 'ok',
    });
    events.push({
      seq: next(),
      at: iso(baseMs, off + 6),
      kind: idx === 0 ? 'db.tx.begin' : 'db.tx.query',
      protocol: proto,
      direction: 'internal',
      observer: 'pg-engine',
      invocation_id: invId,
      engine_session_id: sharedTxKeySess,
      transaction_id: sharedTxId,
      outcome: 'ok',
    });
    events.push({
      seq: next(),
      at: iso(baseMs, off + 16),
      kind: 'db.tx.commit',
      protocol: proto,
      direction: 'internal',
      observer: 'pg-engine',
      invocation_id: invId,
      engine_session_id: sharedTxKeySess,
      transaction_id: sharedTxId,
      measured_duration_ms: 24.5,
      timing_boundary: 'db_tx_begin_to_commit',
      clock_domain: 'engine_monotonic',
      outcome: 'ok',
    });
    events.push({
      seq: next(),
      at: iso(baseMs, off + 21),
      kind: proto === 'rest' ? 'http.response.sent' : 'rpc.response.sent',
      protocol: proto,
      direction: 'outbound',
      observer: proto === 'rest' ? 'edge-gateway' : 'rpc-gateway',
      correlation_id: corr,
      request_id: reqId,
      status_code: 200,
      measured_duration_ms: idx === 0 ? 31.2 : 28.4,
      timing_boundary: 'ingress_to_egress_monotonic',
      clock_domain: 'server_monotonic',
      outcome: 'ok',
    });
  }

  // 5. Base four-transport scenario (includes reused correlation ID, RPC batch/notification, WS fan-out, WT 2 siblings)
  const baseRun = generateLiveFourTransportEvents({
    captureId: 'rec-edge-2026-11-23',
    startSeq: seq,
    baseTimeMs: baseMs + 140,
    scale: 'standard',
    runIndex: 1,
  });
  events.push(...baseRun.events);
  seq = baseRun.nextSeq;

  // 6. Rich reproducible timing cohorts for Compare screen (with tail outliers to drill into!)
  // 28 REST samples (so n >= 20 -> p95 visible, p99 suppressed!)
  for (let i = 0; i < 28; i++) {
    const off = 500 + i * 24;
    const isTail = i >= 25;
    const lat = Number(
      (isTail ? 118 + (i - 25) * 24 + rng() * 8 : 14 + rng() * 44).toFixed(1)
    );
    const txDur = Number((lat * 0.45).toFixed(1));
    const corr = `corr-rec-rest-${String(i + 1).padStart(2, '0')}`;
    const reqId = `req-rec-${i + 1}`;
    const invId = `inv-rec-${i + 1}`;
    const s0 = next();
    events.push({
      seq: s0,
      at: iso(baseMs, off),
      kind: 'http.request.received',
      protocol: 'rest',
      direction: 'inbound',
      observer: 'edge-gateway',
      correlation_id: corr,
      request_id: reqId,
      method: 'POST',
      route: isTail ? '/v1/orders/rebalance-heavy' : '/v1/orders/quote',
      outcome: 'ok',
    });
    events.push({
      seq: next(),
      at: iso(baseMs, off + 4),
      kind: 'invocation.started',
      protocol: 'rest',
      direction: 'internal',
      observer: 'order-runtime',
      correlation_id: corr,
      request_id: reqId,
      invocation_id: invId,
      linked_from_seq: s0,
      outcome: 'ok',
    });
    events.push({
      seq: next(),
      at: iso(baseMs, off + 9),
      kind: 'db.tx.commit',
      protocol: 'rest',
      direction: 'internal',
      observer: 'pg-engine',
      invocation_id: invId,
      engine_session_id: `eng-rec-${i % 4}`,
      transaction_id: `tx-rec-${i + 1}`,
      measured_duration_ms: txDur,
      timing_boundary: 'db_tx_begin_to_commit',
      clock_domain: 'engine_monotonic',
      outcome: 'ok',
    });
    events.push({
      seq: next(),
      at: iso(baseMs, off + 14),
      kind: 'invocation.completed',
      protocol: 'rest',
      direction: 'internal',
      observer: 'order-runtime',
      correlation_id: corr,
      request_id: reqId,
      invocation_id: invId,
      measured_duration_ms: Number((lat * 0.86).toFixed(1)),
      timing_boundary: 'invocation_monotonic',
      clock_domain: 'runtime_monotonic',
      outcome: 'ok',
    });
    events.push({
      seq: next(),
      at: iso(baseMs, off + 17),
      kind: 'http.response.sent',
      protocol: 'rest',
      direction: 'outbound',
      observer: 'edge-gateway',
      correlation_id: corr,
      request_id: reqId,
      invocation_id: invId,
      status_code: isTail && i === 27 ? 504 : 200,
      measured_duration_ms: lat,
      timing_boundary: 'ingress_to_egress_monotonic',
      clock_domain: 'server_monotonic',
      outcome: isTail && i === 27 ? 'error' : 'ok',
    });
  }

  // 12 JSON-RPC samples (n < 20 -> demonstrates p95 AND p99 suppression!)
  for (let i = 0; i < 12; i++) {
    const off = 1200 + i * 26;
    const lat = Number((18 + rng() * 38 + (i === 11 ? 52 : 0)).toFixed(1));
    const corr = `corr-rec-rpc-${String(i + 1).padStart(2, '0')}`;
    const reqId = `req-rec-rpc-${i + 1}`;
    const invId = `inv-rec-rpc-${i + 1}`;
    const s0 = next();
    events.push({
      seq: s0,
      at: iso(baseMs, off),
      kind: 'rpc.document.received',
      protocol: 'jsonrpc',
      direction: 'inbound',
      observer: 'rpc-gateway',
      correlation_id: corr,
      request_id: reqId,
      rpc_id: 5000 + i,
      outcome: 'ok',
    });
    events.push({
      seq: next(),
      at: iso(baseMs, off + 8),
      kind: 'rpc.batch.item.completed',
      protocol: 'jsonrpc',
      direction: 'internal',
      observer: 'rpc-dispatcher',
      correlation_id: corr,
      request_id: reqId,
      rpc_id: 5000 + i,
      rpc_item_index: 0,
      invocation_id: invId,
      measured_duration_ms: Number((lat * 0.8).toFixed(1)),
      timing_boundary: 'invocation_monotonic',
      clock_domain: 'runtime_monotonic',
      outcome: 'ok',
    });
    events.push({
      seq: next(),
      at: iso(baseMs, off + 12),
      kind: 'rpc.response.sent',
      protocol: 'jsonrpc',
      direction: 'outbound',
      observer: 'rpc-gateway',
      correlation_id: corr,
      request_id: reqId,
      status_code: 200,
      measured_duration_ms: lat,
      timing_boundary: 'ingress_to_egress_monotonic',
      clock_domain: 'server_monotonic',
      outcome: 'ok',
    });
  }

  // 22 WebTransport samples (n >= 20 -> p95 visible, p99 suppressed)
  for (let i = 0; i < 22; i++) {
    const off = 1550 + i * 20;
    const lat = Number((9 + rng() * 26 + (i >= 20 ? 48 : 0)).toFixed(1));
    const corr = `corr-rec-wt-${String(i + 1).padStart(2, '0')}`;
    const sess = `wt-rec-sess-${(i % 4) + 1}`;
    const qConn = `quic-rec-cohort-${(i % 2) + 1}`;
    const s0 = next();
    events.push({
      seq: s0,
      at: iso(baseMs, off),
      kind: 'wt.stream.opened',
      protocol: 'webtransport',
      direction: 'inbound',
      observer: 'quic-edge',
      correlation_id: corr,
      quic_connection_id: qConn,
      transport_session_id: sess,
      stream_id: `bidi-${i * 4 + 4}`,
      stream_correlation_id: `sc-rec-${i + 1}`,
      outcome: 'ok',
    });
    events.push({
      seq: next(),
      at: iso(baseMs, off + 9),
      kind: 'wt.stream.frame.sent',
      protocol: 'webtransport',
      direction: 'outbound',
      observer: 'quic-edge',
      correlation_id: corr,
      quic_connection_id: qConn,
      transport_session_id: sess,
      stream_id: `bidi-${i * 4 + 4}`,
      stream_correlation_id: `sc-rec-${i + 1}`,
      measured_duration_ms: lat,
      timing_boundary: 'ingress_to_egress_monotonic',
      clock_domain: 'quic_monotonic',
      outcome: 'ok',
    });
    events.push({
      seq: next(),
      at: iso(baseMs, off + 12),
      kind: 'wt.stream.closed',
      protocol: 'webtransport',
      direction: 'internal',
      observer: 'quic-edge',
      correlation_id: corr,
      quic_connection_id: qConn,
      transport_session_id: sess,
      stream_id: `bidi-${i * 4 + 4}`,
      stream_correlation_id: `sc-rec-${i + 1}`,
      measured_duration_ms: Number((lat + 1.8).toFixed(1)),
      timing_boundary: 'invocation_monotonic',
      clock_domain: 'quic_monotonic',
      outcome: 'ok',
    });
  }

  // 22 WebSocket samples (plus 4 recorded-only samples excluded from measured latency!)
  for (let i = 0; i < 22; i++) {
    const off = 2020 + i * 18;
    const hasMeasured = i < 18;
    const lat = Number((7 + rng() * 24 + (i === 17 ? 38 : 0)).toFixed(1));
    const corr = `corr-rec-ws-${String(i + 1).padStart(2, '0')}`;
    const sess = `ws-rec-sess-${(i % 5) + 1}`;
    events.push({
      seq: next(),
      at: iso(baseMs, off),
      kind: 'ws.frame.received',
      protocol: 'websocket',
      direction: 'inbound',
      observer: 'ws-hub',
      correlation_id: corr,
      transport_session_id: sess,
      topic: 'quotes.stream',
      outcome: 'ok',
    });
    events.push({
      seq: next(),
      at: iso(baseMs, off + 8),
      kind: 'ws.frame.sent',
      protocol: 'websocket',
      direction: 'outbound',
      observer: 'ws-hub',
      correlation_id: corr,
      transport_session_id: sess,
      ...(hasMeasured
        ? {
            measured_duration_ms: lat,
            timing_boundary: 'ingress_to_egress_monotonic',
            clock_domain: 'server_monotonic',
          }
        : {}),
      outcome: 'ok',
    });
  }

  return {
    capture_id: 'rec-edge-2026-11-23',
    adapter_version: ADAPTER_VERSION,
    mode: 'recorded',
    synthetic_label: 'Recorded Synthetic Fixture · Edge Cases & Reproducible Timing',
    fixture_id: 'edge-cases',
    sequence_floor: 1000,
    sequence_ceiling: seq - 1,
    retained_count: events.length,
    evicted_count: 999,
    generated_at: '2026-11-23T10:03:25.000Z',
    events,
  };
}

export function buildRecorded10kFixture(): TraceSnapshotInput {
  const baseMs = Date.parse('2026-11-23T11:00:00.000Z');
  const rng = mulberry32(10000);
  let seq = 1;
  const next = () => seq++;
  const events: RawTraceEventInput[] = [];

  // Generate exactly 10,000 events across 2,500 correlations (4 events each) across all 4 transports
  const totalCorrelations = 2500;
  const protos: Array<'rest' | 'jsonrpc' | 'websocket' | 'webtransport'> = [
    'rest',
    'jsonrpc',
    'websocket',
    'webtransport',
  ];

  for (let i = 0; i < totalCorrelations; i++) {
    const proto = protos[i % 4];
    const off = i * 4;
    const baseLat =
      proto === 'rest'
        ? 22
        : proto === 'jsonrpc'
        ? 26
        : proto === 'websocket'
        ? 12
        : 15;
    const isTail = i % 47 === 0;
    const lat = Number(
      (baseLat + rng() * 28 + (isTail ? 65 + rng() * 45 : 0)).toFixed(1)
    );
    const corr = `corr-10k-${proto}-${String(i + 1).padStart(4, '0')}`;
    const reqId = `req-10k-${i + 1}`;
    const invId = `inv-10k-${i + 1}`;

    if (proto === 'rest') {
      const s0 = next();
      events.push({
        seq: s0,
        at: iso(baseMs, off),
        kind: 'http.request.received',
        protocol: 'rest',
        direction: 'inbound',
        observer: 'edge-gateway',
        correlation_id: corr,
        request_id: reqId,
        method: 'GET',
        route: '/v1/ledger/entry',
        outcome: 'ok',
      });
      events.push({
        seq: next(),
        at: iso(baseMs, off + 1),
        kind: 'invocation.started',
        protocol: 'rest',
        direction: 'internal',
        observer: 'runtime',
        correlation_id: corr,
        request_id: reqId,
        invocation_id: invId,
        linked_from_seq: s0,
        outcome: 'ok',
      });
      events.push({
        seq: next(),
        at: iso(baseMs, off + 2),
        kind: 'db.tx.commit',
        protocol: 'rest',
        direction: 'internal',
        observer: 'pg-engine',
        invocation_id: invId,
        engine_session_id: `eng-10k-${i % 16}`,
        transaction_id: `tx-10k-${i}`,
        measured_duration_ms: Number((lat * 0.4).toFixed(1)),
        timing_boundary: 'db_tx_begin_to_commit',
        clock_domain: 'engine_monotonic',
        outcome: 'ok',
      });
      events.push({
        seq: next(),
        at: iso(baseMs, off + 3),
        kind: 'http.response.sent',
        protocol: 'rest',
        direction: 'outbound',
        observer: 'edge-gateway',
        correlation_id: corr,
        request_id: reqId,
        status_code: isTail && i % 3 === 0 ? 503 : 200,
        measured_duration_ms: lat,
        timing_boundary: 'ingress_to_egress_monotonic',
        clock_domain: 'server_monotonic',
        outcome: isTail && i % 3 === 0 ? 'error' : 'ok',
      });
    } else if (proto === 'jsonrpc') {
      const s0 = next();
      events.push({
        seq: s0,
        at: iso(baseMs, off),
        kind: 'rpc.document.received',
        protocol: 'jsonrpc',
        direction: 'inbound',
        observer: 'rpc-gateway',
        correlation_id: corr,
        request_id: reqId,
        rpc_id: 20000 + i,
        outcome: 'ok',
      });
      events.push({
        seq: next(),
        at: iso(baseMs, off + 1),
        kind: 'rpc.batch.item.invoked',
        protocol: 'jsonrpc',
        direction: 'internal',
        observer: 'rpc-dispatcher',
        correlation_id: corr,
        request_id: reqId,
        rpc_id: 20000 + i,
        rpc_item_index: 0,
        invocation_id: invId,
        linked_from_seq: s0,
        outcome: 'ok',
      });
      events.push({
        seq: next(),
        at: iso(baseMs, off + 2),
        kind: 'rpc.batch.item.completed',
        protocol: 'jsonrpc',
        direction: 'internal',
        observer: 'rpc-dispatcher',
        correlation_id: corr,
        request_id: reqId,
        rpc_id: 20000 + i,
        rpc_item_index: 0,
        invocation_id: invId,
        measured_duration_ms: Number((lat * 0.8).toFixed(1)),
        timing_boundary: 'invocation_monotonic',
        clock_domain: 'runtime_monotonic',
        outcome: 'ok',
      });
      events.push({
        seq: next(),
        at: iso(baseMs, off + 3),
        kind: 'rpc.response.sent',
        protocol: 'jsonrpc',
        direction: 'outbound',
        observer: 'rpc-gateway',
        correlation_id: corr,
        request_id: reqId,
        status_code: 200,
        measured_duration_ms: lat,
        timing_boundary: 'ingress_to_egress_monotonic',
        clock_domain: 'server_monotonic',
        outcome: 'ok',
      });
    } else if (proto === 'websocket') {
      const sess = `ws-10k-${i % 12}`;
      const s0 = next();
      events.push({
        seq: s0,
        at: iso(baseMs, off),
        kind: 'ws.frame.received',
        protocol: 'websocket',
        direction: 'inbound',
        observer: 'ws-hub',
        correlation_id: corr,
        transport_session_id: sess,
        topic: 'stream.l2',
        outcome: 'ok',
      });
      events.push({
        seq: next(),
        at: iso(baseMs, off + 1),
        kind: 'invocation.started',
        protocol: 'websocket',
        direction: 'internal',
        observer: 'ws-runtime',
        correlation_id: corr,
        transport_session_id: sess,
        invocation_id: invId,
        linked_from_seq: s0,
        outcome: 'ok',
      });
      events.push({
        seq: next(),
        at: iso(baseMs, off + 2),
        kind: 'invocation.completed',
        protocol: 'websocket',
        direction: 'internal',
        observer: 'ws-runtime',
        correlation_id: corr,
        transport_session_id: sess,
        invocation_id: invId,
        measured_duration_ms: Number((lat * 0.72).toFixed(1)),
        timing_boundary: 'invocation_monotonic',
        clock_domain: 'runtime_monotonic',
        outcome: 'ok',
      });
      events.push({
        seq: next(),
        at: iso(baseMs, off + 3),
        kind: 'ws.frame.sent',
        protocol: 'websocket',
        direction: 'outbound',
        observer: 'ws-hub',
        correlation_id: corr,
        transport_session_id: sess,
        measured_duration_ms: lat,
        timing_boundary: 'ingress_to_egress_monotonic',
        clock_domain: 'server_monotonic',
        outcome: 'ok',
      });
    } else {
      const sess = `wt-10k-sess-${i}`;
      const qConn = `quic-10k-${Math.floor(i / 8)}`;
      const s0 = next();
      events.push({
        seq: s0,
        at: iso(baseMs, off),
        kind: 'wt.stream.opened',
        protocol: 'webtransport',
        direction: 'inbound',
        observer: 'quic-edge',
        correlation_id: corr,
        quic_connection_id: qConn,
        transport_session_id: sess,
        stream_id: `bidi-${i * 4}`,
        stream_correlation_id: `sc-10k-${i}`,
        outcome: 'ok',
      });
      events.push({
        seq: next(),
        at: iso(baseMs, off + 1),
        kind: 'wt.stream.frame.received',
        protocol: 'webtransport',
        direction: 'inbound',
        observer: 'quic-edge',
        correlation_id: corr,
        quic_connection_id: qConn,
        transport_session_id: sess,
        stream_id: `bidi-${i * 4}`,
        stream_correlation_id: `sc-10k-${i}`,
        outcome: 'ok',
      });
      events.push({
        seq: next(),
        at: iso(baseMs, off + 2),
        kind: 'wt.stream.frame.sent',
        protocol: 'webtransport',
        direction: 'outbound',
        observer: 'quic-edge',
        correlation_id: corr,
        quic_connection_id: qConn,
        transport_session_id: sess,
        stream_id: `bidi-${i * 4}`,
        stream_correlation_id: `sc-10k-${i}`,
        measured_duration_ms: lat,
        timing_boundary: 'ingress_to_egress_monotonic',
        clock_domain: 'quic_monotonic',
        outcome: 'ok',
      });
      events.push({
        seq: next(),
        at: iso(baseMs, off + 3),
        kind: 'wt.datagram.received',
        protocol: 'webtransport',
        direction: 'inbound',
        observer: 'quic-edge',
        correlation_id: corr,
        quic_connection_id: qConn,
        transport_session_id: sess,
        datagram_id: `dg-10k-${i}`,
        outcome: 'ok',
      });
    }
  }

  return {
    capture_id: 'rec-10k-2026-11-23',
    adapter_version: ADAPTER_VERSION,
    mode: 'recorded',
    synthetic_label: 'Recorded Synthetic Fixture · 10,000-Row Stress Cohort',
    fixture_id: 'scale-10k',
    sequence_floor: 1,
    sequence_ceiling: events.length,
    retained_count: events.length,
    evicted_count: 0,
    generated_at: '2026-11-23T11:00:10.000Z',
    events,
  };
}

export function getRecordedFixture(fixtureId: RecordedFixtureId): TraceSnapshotInput {
  return fixtureId === 'scale-10k'
    ? buildRecorded10kFixture()
    : buildRecordedEdgeCasesFixture();
}
