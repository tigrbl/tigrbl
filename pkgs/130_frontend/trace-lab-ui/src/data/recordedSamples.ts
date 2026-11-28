import {
  PrimaryProtocol,
  RawTraceEvent,
  RecordedDatasetId,
  TraceRollup,
  TraceSnapshot,
} from '../types/trace';

// Deterministic Mulberry32 PRNG so fixtures are 100% reproducible
function createRng(seed: number) {
  let t = seed >>> 0;
  return () => {
    t += 0x6d2b79f5;
    let r = Math.imul(t ^ (t >>> 15), 1 | t);
    r ^= r + Math.imul(r ^ (r >>> 7), 61 | r);
    return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
  };
}

function computeSnapshotRollup(events: RawTraceEvent[]): TraceRollup {
  const connections = new Set<string>();
  const transportSessions = new Set<string>();
  const invocations = new Set<string>();
  const subscriptions = new Set<string>();
  const publications = new Set<string>();
  const deliveries = new Set<string>();
  const transactions = new Set<string>();

  const byProtocol: TraceRollup['by_protocol'] = {
    rest: { events: 0, connections: 0, sessions: 0, invocations: 0, errors: 0 },
    http_jsonrpc: { events: 0, connections: 0, sessions: 0, invocations: 0, errors: 0 },
    websocket: { events: 0, connections: 0, sessions: 0, invocations: 0, errors: 0 },
    webtransport: { events: 0, connections: 0, sessions: 0, invocations: 0, errors: 0 },
  };

  const pConns: Record<PrimaryProtocol, Set<string>> = {
    rest: new Set(),
    http_jsonrpc: new Set(),
    websocket: new Set(),
    webtransport: new Set(),
  };
  const pSess: Record<PrimaryProtocol, Set<string>> = {
    rest: new Set(),
    http_jsonrpc: new Set(),
    websocket: new Set(),
    webtransport: new Set(),
  };
  const pInv: Record<PrimaryProtocol, Set<string>> = {
    rest: new Set(),
    http_jsonrpc: new Set(),
    websocket: new Set(),
    webtransport: new Set(),
  };

  for (const ev of events) {
    if (ev.connection_id) connections.add(ev.connection_id);
    if (ev.transport_session_id) transportSessions.add(ev.transport_session_id);
    if (ev.invocation_id) invocations.add(ev.invocation_id);
    if (ev.subscription_id) subscriptions.add(ev.subscription_id);
    if (ev.publication_id) publications.add(ev.publication_id);
    if (ev.delivery_id) deliveries.add(ev.delivery_id);
    if (ev.engine_session_id && ev.transaction_id) {
      transactions.add(`${ev.engine_session_id}::${ev.transaction_id}`);
    }
    if (ev.transport !== 'database') {
      const p = ev.transport;
      byProtocol[p].events += 1;
      if (ev.connection_id) pConns[p].add(ev.connection_id);
      if (ev.transport_session_id) pSess[p].add(ev.transport_session_id);
      if (ev.invocation_id) pInv[p].add(ev.invocation_id);
      if (ev.outcome === 'rejected' || ev.outcome === 'failed' || ev.outcome === 'rolled_back') {
        byProtocol[p].errors += 1;
      }
    }
  }

  (['rest', 'http_jsonrpc', 'websocket', 'webtransport'] as PrimaryProtocol[]).forEach((p) => {
    byProtocol[p].connections = pConns[p].size;
    byProtocol[p].sessions = pSess[p].size;
    byProtocol[p].invocations = pInv[p].size;
  });

  return {
    connections: connections.size,
    transport_sessions: transportSessions.size,
    invocations: invocations.size,
    subscriptions: subscriptions.size,
    publications: publications.size,
    deliveries: deliveries.size,
    transactions: transactions.size,
    by_protocol: byProtocol,
  };
}

function buildContractFixture(): TraceSnapshot {
  const rng = createRng(20261123);
  const baseMs = Date.UTC(2026, 10, 23, 21, 30, 0, 0);
  const captureId = 'rec_v1_2_synth';
  const runId = 'rec_run_01';
  let seq = 100; // Start at 101 to test non-zero retained lower bound (100 evicted prior events)
  let t = 0;

  const events: RawTraceEvent[] = [];
  const push = (
    dtMs: number,
    ev: Omit<RawTraceEvent, 'sequence' | 'at' | 'capture_id' | 'scenario_run_id'>
  ) => {
    t += dtMs;
    seq += 1;
    events.push({
      ...ev,
      sequence: seq,
      at: new Date(baseMs + t).toISOString(),
      capture_id: captureId,
      scenario_run_id: runId,
    });
  };

  const reqSess = 'req_sess_demo_01';
  const sharedNote = 'note_shared_4829';

  // ------------------------------------------------------------------
  // 1. Primary Demo Narrative: REST write note + HTTP JSON-RPC batch read
  //    (includes large opaque numeric ID > MAX_SAFE_INTEGER & shared DB tx)
  // ------------------------------------------------------------------
  push(0, {
    transport: 'rest',
    source: 'kernel',
    kind: 'http.request.received',
    framing: 'http/1.1',
    outcome: 'open',
    direction: 'inbound',
    label: 'POST /api/notes received',
    session_id: reqSess,
    connection_id: 'tcp_http_01',
    request_id: 'req_rest_write_01',
    correlation_id: 'corr_rest_write_01',
    note_id: sharedNote,
    metadata: { http_method: 'POST', route: '/api/notes', note_title: 'Trace Lab Verification' },
  });

  push(12, {
    transport: 'rest',
    source: 'app',
    kind: 'invocation.started',
    framing: 'rest-json',
    outcome: 'open',
    label: 'notes.create started',
    session_id: reqSess,
    connection_id: 'tcp_http_01',
    request_id: 'req_rest_write_01',
    correlation_id: 'corr_rest_write_01',
    invocation_id: 'inv_rest_write_01',
    note_id: sharedNote,
  });

  // Retried transaction: Attempt 1 rolls back on serialization conflict, Attempt 2 commits
  push(8, {
    transport: 'database',
    source: 'database',
    kind: 'db.tx.begin',
    outcome: 'open',
    label: 'DB tx begin (attempt 1)',
    session_id: reqSess,
    correlation_id: 'corr_rest_write_01',
    invocation_id: 'inv_rest_write_01',
    engine_session_id: 'eng_pg_01',
    transaction_id: 'tx_write_01_a1',
    note_id: sharedNote,
    metadata: { isolation_level: 'SERIALIZABLE', sql_op: 'INSERT', table: 'notes', retries: 0 },
  });

  push(18, {
    transport: 'database',
    source: 'database',
    kind: 'db.tx.rollback',
    outcome: 'rolled_back',
    label: 'DB tx rolled back (serialization retry)',
    session_id: reqSess,
    correlation_id: 'corr_rest_write_01',
    invocation_id: 'inv_rest_write_01',
    engine_session_id: 'eng_pg_01',
    transaction_id: 'tx_write_01_a1',
    note_id: sharedNote,
    duration_ms: 9.4,
    clock_domain: 'server.monotonic_ns',
    timing_boundary: 'db.tx.begin -> db.tx.rollback',
    observation: {
      measure: 'transaction_latency',
      unit: 'ms',
      value: 9.4,
      clock_domain: 'server.monotonic_ns',
      timing_boundary: 'db.tx.begin -> db.tx.rollback',
      provenance: 'tigrbl.db.engine',
    },
    metadata: { sql_op: 'INSERT', table: 'notes', retries: 1 },
  });

  push(6, {
    transport: 'database',
    source: 'database',
    kind: 'db.tx.begin',
    outcome: 'open',
    label: 'DB tx begin (retry commit)',
    session_id: reqSess,
    correlation_id: 'corr_rest_write_01',
    invocation_id: 'inv_rest_write_01',
    engine_session_id: 'eng_pg_01',
    transaction_id: 'tx_write_01_a2',
    note_id: sharedNote,
    metadata: { isolation_level: 'SERIALIZABLE', sql_op: 'INSERT', table: 'notes', retries: 1 },
  });

  push(14, {
    transport: 'database',
    source: 'database',
    kind: 'db.tx.commit',
    outcome: 'committed',
    label: 'DB tx committed (note persisted)',
    session_id: reqSess,
    correlation_id: 'corr_rest_write_01',
    invocation_id: 'inv_rest_write_01',
    engine_session_id: 'eng_pg_01',
    transaction_id: 'tx_write_01_a2',
    note_id: sharedNote,
    duration_ms: 7.2,
    clock_domain: 'server.monotonic_ns',
    timing_boundary: 'db.tx.begin -> db.tx.commit',
    observation: {
      measure: 'transaction_latency',
      unit: 'ms',
      value: 7.2,
      clock_domain: 'server.monotonic_ns',
      timing_boundary: 'db.tx.begin -> db.tx.commit',
      provenance: 'tigrbl.db.engine',
    },
    metadata: { statement_count: 2, sql_op: 'INSERT', table: 'notes' },
  });

  push(5, {
    transport: 'rest',
    source: 'app',
    kind: 'invocation.completed',
    framing: 'rest-json',
    outcome: 'ok',
    http_status: 201,
    label: 'notes.create completed',
    session_id: reqSess,
    connection_id: 'tcp_http_01',
    request_id: 'req_rest_write_01',
    correlation_id: 'corr_rest_write_01',
    invocation_id: 'inv_rest_write_01',
    engine_session_id: 'eng_pg_01',
    transaction_id: 'tx_write_01_a2',
    note_id: sharedNote,
    duration_ms: 24.6,
    clock_domain: 'server.monotonic_ns',
    timing_boundary: 'invocation.started -> invocation.completed',
    observation: {
      measure: 'invocation_latency',
      unit: 'ms',
      value: 24.6,
      clock_domain: 'server.monotonic_ns',
      timing_boundary: 'invocation.started -> invocation.completed',
      provenance: 'tigrbl.runtime',
    },
  });

  push(4, {
    transport: 'rest',
    source: 'kernel',
    kind: 'http.response.sent',
    framing: 'http/1.1',
    outcome: 'ok',
    http_status: 201,
    direction: 'outbound',
    label: 'HTTP 201 Created',
    session_id: reqSess,
    connection_id: 'tcp_http_01',
    request_id: 'req_rest_write_01',
    correlation_id: 'corr_rest_write_01',
    invocation_id: 'inv_rest_write_01',
    note_id: sharedNote,
    metadata: { bytes_len: 196 },
  });

  // HTTP JSON-RPC batch read (2 items sharing a single DB read-snapshot transaction!)
  const largeOpaqueRpcId0 = '9007199254740993184';
  const largeOpaqueRpcId1 = '9007199254740993185';
  push(45, {
    transport: 'http_jsonrpc',
    source: 'kernel',
    kind: 'http.request.received',
    framing: 'json-rpc-2.0/http',
    outcome: 'open',
    direction: 'inbound',
    label: 'POST /rpc batch (2 items)',
    session_id: reqSess,
    connection_id: 'tcp_http_01',
    request_id: 'req_rpc_batch_01',
    correlation_id: 'corr_rpc_batch_01',
    note_id: sharedNote,
    metadata: { http_method: 'POST', route: '/rpc', batch_size: 2 },
  });

  push(5, {
    transport: 'http_jsonrpc',
    source: 'app',
    kind: 'invocation.started',
    framing: 'json-rpc-2.0',
    outcome: 'open',
    label: 'notes.get [batch #0] started',
    session_id: reqSess,
    connection_id: 'tcp_http_01',
    request_id: 'req_rpc_batch_01',
    correlation_id: 'corr_rpc_batch_01',
    invocation_id: 'inv_rpc_read_01_b0',
    rpc_id: largeOpaqueRpcId0,
    rpc_item_index: 0,
    note_id: sharedNote,
    metadata: { rpc_method: 'notes.get' },
  });

  push(4, {
    transport: 'http_jsonrpc',
    source: 'app',
    kind: 'invocation.started',
    framing: 'json-rpc-2.0',
    outcome: 'open',
    label: 'notes.audit [batch #1] started',
    session_id: reqSess,
    connection_id: 'tcp_http_01',
    request_id: 'req_rpc_batch_01',
    correlation_id: 'corr_rpc_batch_01',
    invocation_id: 'inv_rpc_read_01_b1',
    rpc_id: largeOpaqueRpcId1,
    rpc_item_index: 1,
    note_id: sharedNote,
    metadata: { rpc_method: 'notes.audit' },
  });

  // Shared transaction participating with BOTH batch invocations (many-to-many linkage!)
  push(6, {
    transport: 'database',
    source: 'database',
    kind: 'db.tx.begin',
    outcome: 'open',
    label: 'Shared DB read snapshot begin',
    session_id: reqSess,
    correlation_id: 'corr_rpc_batch_01',
    invocation_id: 'inv_rpc_read_01_b0',
    engine_session_id: 'eng_pg_02',
    transaction_id: 'tx_shared_read_01',
    note_id: sharedNote,
    metadata: { isolation_level: 'REPEATABLE READ', sql_op: 'SELECT', table: 'notes' },
  });

  push(9, {
    transport: 'database',
    source: 'database',
    kind: 'db.tx.participant',
    outcome: 'open',
    label: 'Batch #1 joined shared tx',
    session_id: reqSess,
    correlation_id: 'corr_rpc_batch_01',
    invocation_id: 'inv_rpc_read_01_b1',
    engine_session_id: 'eng_pg_02',
    transaction_id: 'tx_shared_read_01',
    note_id: sharedNote,
    metadata: { sql_op: 'SELECT', table: 'note_audit' },
  });

  push(11, {
    transport: 'database',
    source: 'database',
    kind: 'db.tx.commit',
    outcome: 'committed',
    label: 'Shared DB read tx committed',
    session_id: reqSess,
    correlation_id: 'corr_rpc_batch_01',
    invocation_id: 'inv_rpc_read_01_b0',
    engine_session_id: 'eng_pg_02',
    transaction_id: 'tx_shared_read_01',
    note_id: sharedNote,
    duration_ms: 4.8,
    clock_domain: 'server.monotonic_ns',
    timing_boundary: 'db.tx.begin -> db.tx.commit',
    observation: {
      measure: 'transaction_latency',
      unit: 'ms',
      value: 4.8,
      clock_domain: 'server.monotonic_ns',
      timing_boundary: 'db.tx.begin -> db.tx.commit',
      provenance: 'tigrbl.db.engine',
    },
    metadata: { statement_count: 2 },
  });

  push(4, {
    transport: 'http_jsonrpc',
    source: 'app',
    kind: 'invocation.completed',
    framing: 'json-rpc-2.0',
    outcome: 'ok',
    http_status: 200,
    label: 'notes.get [batch #0] completed',
    session_id: reqSess,
    connection_id: 'tcp_http_01',
    request_id: 'req_rpc_batch_01',
    correlation_id: 'corr_rpc_batch_01',
    invocation_id: 'inv_rpc_read_01_b0',
    rpc_id: largeOpaqueRpcId0,
    rpc_item_index: 0,
    engine_session_id: 'eng_pg_02',
    transaction_id: 'tx_shared_read_01',
    note_id: sharedNote,
    duration_ms: 11.4,
    clock_domain: 'server.monotonic_ns',
    timing_boundary: 'invocation.started -> invocation.completed',
    observation: {
      measure: 'invocation_latency',
      unit: 'ms',
      value: 11.4,
      clock_domain: 'server.monotonic_ns',
      timing_boundary: 'invocation.started -> invocation.completed',
      provenance: 'tigrbl.runtime',
    },
  });

  push(3, {
    transport: 'http_jsonrpc',
    source: 'app',
    kind: 'invocation.completed',
    framing: 'json-rpc-2.0',
    outcome: 'ok',
    http_status: 200,
    label: 'notes.audit [batch #1] completed',
    session_id: reqSess,
    connection_id: 'tcp_http_01',
    request_id: 'req_rpc_batch_01',
    correlation_id: 'corr_rpc_batch_01',
    invocation_id: 'inv_rpc_read_01_b1',
    rpc_id: largeOpaqueRpcId1,
    rpc_item_index: 1,
    engine_session_id: 'eng_pg_02',
    transaction_id: 'tx_shared_read_01',
    note_id: sharedNote,
    duration_ms: 12.1,
    clock_domain: 'server.monotonic_ns',
    timing_boundary: 'invocation.started -> invocation.completed',
    observation: {
      measure: 'invocation_latency',
      unit: 'ms',
      value: 12.1,
      clock_domain: 'server.monotonic_ns',
      timing_boundary: 'invocation.started -> invocation.completed',
      provenance: 'tigrbl.runtime',
    },
  });

  push(4, {
    transport: 'http_jsonrpc',
    source: 'kernel',
    kind: 'http.response.sent',
    framing: 'json-rpc-2.0/http',
    outcome: 'ok',
    http_status: 200,
    direction: 'outbound',
    label: 'HTTP 200 JSON-RPC batch response',
    session_id: reqSess,
    connection_id: 'tcp_http_01',
    request_id: 'req_rpc_batch_01',
    correlation_id: 'corr_rpc_batch_01',
    note_id: sharedNote,
    metadata: { batch_size: 2, bytes_len: 388 },
  });

  // ------------------------------------------------------------------
  // 2. WebSocket — Subscribe (gen 1) -> Reattach (gen 2) -> Publish -> Delivery
  // ------------------------------------------------------------------
  push(65, {
    transport: 'websocket',
    source: 'kernel',
    kind: 'ws.session.opened',
    framing: 'ws-jsonrpc-v2',
    outcome: 'ok',
    label: 'WS subscriber socket 1 opened',
    session_id: reqSess,
    connection_id: 'ws_conn_sub_01',
    transport_session_id: 'ws_tsess_sub_01',
    metadata: { subprotocol: 'tigrbl.jsonrpc.v2' },
  });

  push(14, {
    transport: 'websocket',
    source: 'kernel',
    kind: 'ws.session.opened',
    framing: 'ws-jsonrpc-v2',
    outcome: 'ok',
    label: 'WS publisher socket opened',
    session_id: reqSess,
    connection_id: 'ws_conn_pub_01',
    transport_session_id: 'ws_tsess_pub_01',
    metadata: { subprotocol: 'tigrbl.jsonrpc.v2' },
  });

  push(16, {
    transport: 'websocket',
    source: 'app',
    kind: 'ws.message.received',
    framing: 'ws-jsonrpc-v2',
    outcome: 'open',
    direction: 'inbound',
    label: 'WS notes.subscribe frame',
    session_id: reqSess,
    connection_id: 'ws_conn_sub_01',
    transport_session_id: 'ws_tsess_sub_01',
    correlation_id: 'corr_ws_sub_01',
    invocation_id: 'inv_ws_sub_01',
    rpc_id: '101',
    metadata: { rpc_method: 'notes.subscribe', topic: `notes.${sharedNote}` },
  });

  push(12, {
    transport: 'websocket',
    source: 'broker',
    kind: 'broker.subscription.acknowledged',
    framing: 'ws-jsonrpc-v2',
    outcome: 'ok',
    label: 'Subscription v2 ack (gen 1)',
    session_id: reqSess,
    connection_id: 'ws_conn_sub_01',
    transport_session_id: 'ws_tsess_sub_01',
    correlation_id: 'corr_ws_sub_01',
    invocation_id: 'inv_ws_sub_01',
    subscription_id: 'sub_notes_primary',
    attachment_generation: 1,
    lease_id: 'lease_notes_g1',
    note_id: sharedNote,
    metadata: { ack_version: 'v2', topic: `notes.${sharedNote}` },
  });

  // Attachment generation 2 on rotated transport session retaining same logical subscription_id
  push(42, {
    transport: 'websocket',
    source: 'kernel',
    kind: 'ws.session.opened',
    framing: 'ws-jsonrpc-v2',
    outcome: 'ok',
    label: 'WS subscriber socket 2 opened (resume)',
    session_id: reqSess,
    connection_id: 'ws_conn_sub_02',
    transport_session_id: 'ws_tsess_sub_02',
    metadata: { subprotocol: 'tigrbl.jsonrpc.v2' },
  });

  push(15, {
    transport: 'websocket',
    source: 'broker',
    kind: 'broker.subscription.reattached',
    framing: 'ws-jsonrpc-v2',
    outcome: 'ok',
    label: 'Subscription reattached (gen 2)',
    session_id: reqSess,
    connection_id: 'ws_conn_sub_02',
    transport_session_id: 'ws_tsess_sub_02',
    subscription_id: 'sub_notes_primary',
    attachment_generation: 2,
    lease_id: 'lease_notes_g2',
    note_id: sharedNote,
    metadata: { ack_version: 'v2', topic: `notes.${sharedNote}` },
  });

  // Publish -> Deliveries
  push(38, {
    transport: 'websocket',
    source: 'app',
    kind: 'invocation.started',
    framing: 'ws-jsonrpc-v2',
    outcome: 'open',
    direction: 'inbound',
    label: 'WS notes.publish started',
    session_id: reqSess,
    connection_id: 'ws_conn_pub_01',
    transport_session_id: 'ws_tsess_pub_01',
    correlation_id: 'corr_ws_pub_01',
    invocation_id: 'inv_ws_pub_01',
    rpc_id: '101', // Same wire rpc_id "101" scoped to a different exchange!
    note_id: sharedNote,
    metadata: { rpc_method: 'notes.publish', topic: `notes.${sharedNote}` },
  });

  push(9, {
    transport: 'websocket',
    source: 'broker',
    kind: 'broker.publication.created',
    framing: 'broker-internal',
    outcome: 'ok',
    label: 'Broker publication accepted',
    session_id: reqSess,
    connection_id: 'ws_conn_pub_01',
    transport_session_id: 'ws_tsess_pub_01',
    correlation_id: 'corr_ws_pub_01',
    invocation_id: 'inv_ws_pub_01',
    publication_id: 'pub_notes_01',
    origin_invocation_id: 'inv_ws_pub_01',
    origin_correlation_id: 'corr_ws_pub_01',
    note_id: sharedNote,
    metadata: { topic: `notes.${sharedNote}` },
  });

  push(16, {
    transport: 'websocket',
    source: 'broker',
    kind: 'broker.delivery.dispatched',
    framing: 'ws-jsonrpc-v2',
    outcome: 'delivered',
    direction: 'outbound',
    label: 'Notification delivered (gen 2 attachment)',
    session_id: reqSess,
    connection_id: 'ws_conn_sub_02',
    transport_session_id: 'ws_tsess_sub_02',
    subscription_id: 'sub_notes_primary',
    attachment_generation: 2,
    lease_id: 'lease_notes_g2',
    publication_id: 'pub_notes_01',
    delivery_id: 'deliv_notes_01_r1',
    origin_invocation_id: 'inv_ws_pub_01',
    origin_correlation_id: 'corr_ws_pub_01',
    note_id: sharedNote,
    duration_ms: 4.3,
    clock_domain: 'broker.monotonic_ns',
    timing_boundary: 'broker.publication.created -> broker.delivery.dispatched',
    observation: {
      measure: 'delivery_latency',
      unit: 'ms',
      value: 4.3,
      clock_domain: 'broker.monotonic_ns',
      timing_boundary: 'broker.publication.created -> broker.delivery.dispatched',
      provenance: 'tigrbl.broker',
    },
    metadata: { delivery_state: 'delivered', topic: `notes.${sharedNote}` },
  });

  // Delivery with unretained origin invocation (tests dashed link indicator!)
  push(18, {
    transport: 'websocket',
    source: 'broker',
    kind: 'broker.delivery.rejected',
    framing: 'ws-jsonrpc-v2',
    outcome: 'rejected',
    direction: 'outbound',
    label: 'Stale gen-1 delivery rejected',
    session_id: reqSess,
    connection_id: 'ws_conn_sub_01',
    transport_session_id: 'ws_tsess_sub_01',
    subscription_id: 'sub_notes_primary',
    attachment_generation: 1,
    lease_id: 'lease_notes_g1',
    publication_id: 'pub_notes_evicted_00',
    delivery_id: 'deliv_notes_00_stale',
    origin_invocation_id: 'inv_ws_pub_evicted_00',
    metadata: { delivery_state: 'rejected_stale_generation', reject_reason: 'Lease superseded by gen 2' },
  });

  push(7, {
    transport: 'websocket',
    source: 'app',
    kind: 'invocation.completed',
    framing: 'ws-jsonrpc-v2',
    outcome: 'ok',
    label: 'WS notes.publish completed',
    session_id: reqSess,
    connection_id: 'ws_conn_pub_01',
    transport_session_id: 'ws_tsess_pub_01',
    correlation_id: 'corr_ws_pub_01',
    invocation_id: 'inv_ws_pub_01',
    publication_id: 'pub_notes_01',
    note_id: sharedNote,
    duration_ms: 10.2,
    clock_domain: 'server.monotonic_ns',
    timing_boundary: 'invocation.started -> invocation.completed',
    observation: {
      measure: 'invocation_latency',
      unit: 'ms',
      value: 10.2,
      clock_domain: 'server.monotonic_ns',
      timing_boundary: 'invocation.started -> invocation.completed',
      provenance: 'tigrbl.runtime',
    },
  });

  push(20, {
    transport: 'websocket',
    source: 'kernel',
    kind: 'ws.session.closed',
    framing: 'ws-jsonrpc-v2',
    outcome: 'ok',
    label: 'WS subscriber socket 1 closed',
    connection_id: 'ws_conn_sub_01',
    transport_session_id: 'ws_tsess_sub_01',
  });

  // ------------------------------------------------------------------
  // 3. WebTransport — 1 QUIC connection -> 2 sessions (A & B), UDP rebind,
  //    interleaved streams, datagrams, framed JSON-RPC echo, Session B reject
  // ------------------------------------------------------------------
  push(55, {
    transport: 'webtransport',
    source: 'kernel',
    kind: 'quic.connection.established',
    framing: 'quic-h3',
    outcome: 'ok',
    label: 'QUIC connection established',
    connection_id: 'quic_conn_01',
    metadata: { quic_alpn: 'h3' },
  });

  push(10, {
    transport: 'webtransport',
    source: 'kernel',
    kind: 'wt.session.opened',
    framing: 'webtransport-h3',
    outcome: 'ok',
    label: 'WT Session A opened',
    session_id: reqSess,
    connection_id: 'quic_conn_01',
    transport_session_id: 'wt_tsess_a',
    correlation_id: 'corr_wt_session_a',
  });

  push(8, {
    transport: 'webtransport',
    source: 'kernel',
    kind: 'wt.session.opened',
    framing: 'webtransport-h3',
    outcome: 'ok',
    label: 'WT Session B opened',
    session_id: reqSess,
    connection_id: 'quic_conn_01',
    transport_session_id: 'wt_tsess_b',
    correlation_id: 'corr_wt_session_b',
  });

  push(14, {
    transport: 'webtransport',
    source: 'kernel',
    kind: 'wt.stream.opened',
    framing: 'length-prefixed-jsonrpc',
    outcome: 'open',
    direction: 'bidirectional',
    label: 'Session A bidi stream #0 opened',
    connection_id: 'quic_conn_01',
    transport_session_id: 'wt_tsess_a',
    correlation_id: 'corr_wt_session_a',
    stream_id: '0',
    stream_correlation_id: 'scorr_a_0',
    metadata: { stream_type: 'bidirectional', frame_codec: 'tigrbl.framed.v1' },
  });

  push(9, {
    transport: 'webtransport',
    source: 'kernel',
    kind: 'wt.datagram.received',
    framing: 'h3-datagram',
    outcome: 'ok',
    direction: 'inbound',
    label: 'Session A datagram received',
    connection_id: 'quic_conn_01',
    transport_session_id: 'wt_tsess_a',
    correlation_id: 'corr_wt_session_a',
    datagram_id: 'dg_a_001',
    metadata: { bytes_len: 48 },
  });

  push(11, {
    transport: 'webtransport',
    source: 'app',
    kind: 'invocation.started',
    framing: 'framed-json-rpc-2.0',
    outcome: 'open',
    direction: 'inbound',
    label: 'WT framed JSON-RPC echo started',
    session_id: reqSess,
    connection_id: 'quic_conn_01',
    transport_session_id: 'wt_tsess_a',
    correlation_id: 'corr_wt_session_a',
    stream_id: '0',
    stream_correlation_id: 'scorr_a_0',
    invocation_id: 'inv_wt_echo_01',
    rpc_id: 'echo-01',
    metadata: { rpc_method: 'lab.echo' },
  });

  push(16, {
    transport: 'webtransport',
    source: 'kernel',
    kind: 'wt.connection.rebind',
    framing: 'quic-h3',
    outcome: 'ok',
    label: 'QUIC UDP path rebind',
    connection_id: 'quic_conn_01',
    transport_session_id: 'wt_tsess_a',
    correlation_id: 'corr_wt_session_a',
    metadata: {
      peer_addr_before: '127.0.0.1:52014',
      peer_addr_after: '127.0.0.1:52099',
      rebind_reason: 'client_udp_socket_migrated',
    },
  });

  push(12, {
    transport: 'webtransport',
    source: 'kernel',
    kind: 'wt.stream.opened',
    framing: 'tigrbl-framed',
    outcome: 'ok',
    direction: 'unidirectional',
    label: 'Session A uni stream #4 opened',
    connection_id: 'quic_conn_01',
    transport_session_id: 'wt_tsess_a',
    correlation_id: 'corr_wt_session_a',
    stream_id: '4',
    stream_correlation_id: 'scorr_a_4',
    metadata: { stream_type: 'unidirectional', bytes_len: 112 },
  });

  push(10, {
    transport: 'webtransport',
    source: 'kernel',
    kind: 'wt.datagram.sent',
    framing: 'h3-datagram',
    outcome: 'ok',
    direction: 'outbound',
    label: 'Session A datagram echoed',
    connection_id: 'quic_conn_01',
    transport_session_id: 'wt_tsess_a',
    correlation_id: 'corr_wt_session_a',
    datagram_id: 'dg_a_002',
    metadata: { bytes_len: 48 },
  });

  push(14, {
    transport: 'webtransport',
    source: 'app',
    kind: 'invocation.completed',
    framing: 'framed-json-rpc-2.0',
    outcome: 'ok',
    label: 'WT framed JSON-RPC echo completed',
    session_id: reqSess,
    connection_id: 'quic_conn_01',
    transport_session_id: 'wt_tsess_a',
    correlation_id: 'corr_wt_session_a',
    stream_id: '0',
    stream_correlation_id: 'scorr_a_0',
    invocation_id: 'inv_wt_echo_01',
    rpc_id: 'echo-01',
    duration_ms: 5.4,
    clock_domain: 'server.monotonic_ns',
    timing_boundary: 'invocation.started -> invocation.completed',
    observation: {
      measure: 'invocation_latency',
      unit: 'ms',
      value: 5.4,
      clock_domain: 'server.monotonic_ns',
      timing_boundary: 'invocation.started -> invocation.completed',
      provenance: 'tigrbl.runtime',
    },
  });

  push(8, {
    transport: 'webtransport',
    source: 'kernel',
    kind: 'wt.stream.closed',
    framing: 'length-prefixed-jsonrpc',
    outcome: 'ok',
    direction: 'bidirectional',
    label: 'Session A stream #0 closed',
    connection_id: 'quic_conn_01',
    transport_session_id: 'wt_tsess_a',
    correlation_id: 'corr_wt_session_a',
    stream_id: '0',
    stream_correlation_id: 'scorr_a_0',
  });

  // Session B streams, datagrams, and malformed stream-record rejection
  push(12, {
    transport: 'webtransport',
    source: 'kernel',
    kind: 'wt.datagram.received',
    framing: 'h3-datagram',
    outcome: 'ok',
    direction: 'inbound',
    label: 'Session B datagram received',
    connection_id: 'quic_conn_01',
    transport_session_id: 'wt_tsess_b',
    correlation_id: 'corr_wt_session_b',
    datagram_id: 'dg_b_001',
    metadata: { bytes_len: 36 },
  });

  push(10, {
    transport: 'webtransport',
    source: 'kernel',
    kind: 'wt.stream.opened',
    framing: 'length-prefixed-jsonrpc',
    outcome: 'open',
    direction: 'bidirectional',
    label: 'Session B bidi stream #0 opened',
    connection_id: 'quic_conn_01',
    transport_session_id: 'wt_tsess_b',
    correlation_id: 'corr_wt_session_b',
    stream_id: '0', // Same stream_id "0" scoped strictly under wt_tsess_b!
    stream_correlation_id: 'scorr_b_0',
    metadata: { stream_type: 'bidirectional', frame_codec: 'tigrbl.framed.v1' },
  });

  push(16, {
    transport: 'webtransport',
    source: 'runtime',
    kind: 'wt.stream.rejected',
    framing: 'length-prefixed-jsonrpc',
    outcome: 'rejected',
    direction: 'inbound',
    label: 'Malformed stream record rejected',
    connection_id: 'quic_conn_01',
    transport_session_id: 'wt_tsess_b',
    correlation_id: 'corr_wt_session_b',
    stream_id: '0',
    stream_correlation_id: 'scorr_b_0',
    metadata: {
      reject_code: 'ERR_MALFORMED_FRAME_HEADER',
      reject_reason: 'Truncated varint length prefix on Session B stream #0',
    },
  });

  // Unknown event kind kept visible in Event Table for adapter contract verification
  push(12, {
    transport: 'webtransport',
    source: 'kernel',
    kind: 'kernel.experimental.ecn_probe',
    framing: 'quic-h3',
    outcome: 'unknown',
    label: 'kernel.experimental.ecn_probe',
    connection_id: 'quic_conn_01',
    transport_session_id: 'wt_tsess_a',
    correlation_id: 'corr_wt_session_a',
  });

  // Still-open database transaction (missing terminal commit/rollback — tests dotted cap!)
  push(20, {
    transport: 'database',
    source: 'database',
    kind: 'db.tx.begin',
    outcome: 'open',
    label: 'DB tx begin (in-flight / open)',
    session_id: reqSess,
    engine_session_id: 'eng_pg_03',
    transaction_id: 'tx_open_inflight_99',
    metadata: { isolation_level: 'READ COMMITTED', sql_op: 'UPDATE', table: 'notes' },
  });

  // ------------------------------------------------------------------
  // 4. Additional statistically rich observations for Distributions
  //    - REST: 26 invocations (enables p50, p90, p95; tests outliers & 2 sink-only excluded)
  //    - HTTP JSON-RPC: 22 invocations (enables p50, p90, p95)
  //    - WebSocket: 14 invocations + 12 deliveries (enables p50, p90)
  //    - WebTransport: 6 invocations (n < 10 -> tests limited-sample rule: p50 only!)
  //    - Database: 24 transactions (enables p50, p90, p95)
  // ------------------------------------------------------------------
  const sampleLatency = (mean: number, spread: number, outlierChance = 0.08) => {
    const u = (rng() + rng() + rng()) / 3; // bell-ish around 0.5
    let val = mean + (u - 0.5) * spread * 2;
    if (rng() < outlierChance) {
      val += spread * (1.8 + rng() * 1.4);
    }
    return Number(Math.max(1.1, val).toFixed(2));
  };

  for (let i = 2; i <= 26; i++) {
    const idx = i.toString().padStart(2, '0');
    const isErr = i === 14 || i === 23;
    const dur = sampleLatency(14.5, 8.5, 0.1);
    const missingTiming = i === 25 || i === 26;
    push(35 + Math.floor(rng() * 55), {
      transport: 'rest',
      source: 'app',
      kind: isErr ? 'invocation.failed' : 'invocation.completed',
      framing: 'rest-json',
      outcome: isErr ? 'failed' : 'ok',
      http_status: isErr ? 422 : 200,
      label: isErr ? `notes.update validation failed (#${idx})` : `notes.read completed (#${idx})`,
      session_id: reqSess,
      connection_id: i % 2 === 0 ? 'tcp_http_01' : 'tcp_http_02',
      request_id: `req_rest_${idx}`,
      correlation_id: `corr_rest_${idx}`,
      invocation_id: `inv_rest_${idx}`,
      ...(missingTiming
        ? {}
        : {
            duration_ms: dur,
            clock_domain: 'server.monotonic_ns',
            timing_boundary: 'invocation.started -> invocation.completed',
            observation: {
              measure: 'invocation_latency',
              unit: 'ms',
              value: dur,
              clock_domain: 'server.monotonic_ns',
              timing_boundary: 'invocation.started -> invocation.completed',
              provenance: 'tigrbl.runtime',
            },
          }),
    });
  }

  for (let i = 2; i <= 21; i++) {
    const idx = i.toString().padStart(2, '0');
    const dur = sampleLatency(11.2, 6.4, 0.08);
    push(30 + Math.floor(rng() * 50), {
      transport: 'http_jsonrpc',
      source: 'app',
      kind: 'invocation.completed',
      framing: 'json-rpc-2.0',
      outcome: i === 17 ? 'rejected' : 'ok',
      http_status: i === 17 ? 400 : 200,
      label: i === 17 ? `notes.patch rejected (#${idx})` : `notes.get completed (#${idx})`,
      session_id: reqSess,
      connection_id: 'tcp_http_02',
      request_id: `req_rpc_${idx}`,
      correlation_id: `corr_rpc_${idx}`,
      invocation_id: `inv_rpc_${idx}`,
      rpc_id: `rpc_${idx}`,
      duration_ms: dur,
      clock_domain: 'server.monotonic_ns',
      timing_boundary: 'invocation.started -> invocation.completed',
      observation: {
        measure: 'invocation_latency',
        unit: 'ms',
        value: dur,
        clock_domain: 'server.monotonic_ns',
        timing_boundary: 'invocation.started -> invocation.completed',
        provenance: 'tigrbl.runtime',
      },
    });
  }

  for (let i = 2; i <= 14; i++) {
    const idx = i.toString().padStart(2, '0');
    const invDur = sampleLatency(8.8, 5.2, 0.08);
    const delDur = sampleLatency(4.4, 2.9, 0.12);
    push(28 + Math.floor(rng() * 48), {
      transport: 'websocket',
      source: 'app',
      kind: 'invocation.completed',
      framing: 'ws-jsonrpc-v2',
      outcome: 'ok',
      label: `WS notes.publish (#${idx})`,
      session_id: reqSess,
      connection_id: 'ws_conn_pub_01',
      transport_session_id: 'ws_tsess_pub_01',
      correlation_id: `corr_ws_pub_${idx}`,
      invocation_id: `inv_ws_pub_${idx}`,
      publication_id: `pub_notes_${idx}`,
      duration_ms: invDur,
      clock_domain: 'server.monotonic_ns',
      timing_boundary: 'invocation.started -> invocation.completed',
      observation: {
        measure: 'invocation_latency',
        unit: 'ms',
        value: invDur,
        clock_domain: 'server.monotonic_ns',
        timing_boundary: 'invocation.started -> invocation.completed',
        provenance: 'tigrbl.runtime',
      },
    });

    if (i <= 12) {
      push(8, {
        transport: 'websocket',
        source: 'broker',
        kind: 'broker.delivery.dispatched',
        framing: 'ws-jsonrpc-v2',
        outcome: 'delivered',
        direction: 'outbound',
        label: `Notification delivered (#${idx})`,
        session_id: reqSess,
        connection_id: 'ws_conn_sub_02',
        transport_session_id: 'ws_tsess_sub_02',
        subscription_id: 'sub_notes_primary',
        attachment_generation: 2,
        lease_id: 'lease_notes_g2',
        publication_id: `pub_notes_${idx}`,
        delivery_id: `deliv_notes_${idx}`,
        origin_invocation_id: `inv_ws_pub_${idx}`,
        origin_correlation_id: `corr_ws_pub_${idx}`,
        duration_ms: delDur,
        clock_domain: 'broker.monotonic_ns',
        timing_boundary: 'broker.publication.created -> broker.delivery.dispatched',
        observation: {
          measure: 'delivery_latency',
          unit: 'ms',
          value: delDur,
          clock_domain: 'broker.monotonic_ns',
          timing_boundary: 'broker.publication.created -> broker.delivery.dispatched',
          provenance: 'tigrbl.broker',
        },
        metadata: { delivery_state: 'delivered' },
      });
    }
  }

  // WebTransport low-sample cohort (total n = 6 -> tests p50 only, limited-sample badge)
  for (let i = 2; i <= 6; i++) {
    const idx = i.toString().padStart(2, '0');
    const dur = sampleLatency(6.1, 3.0, 0.05);
    push(35, {
      transport: 'webtransport',
      source: 'app',
      kind: 'invocation.completed',
      framing: 'framed-json-rpc-2.0',
      outcome: 'ok',
      label: `WT framed echo (#${idx})`,
      session_id: reqSess,
      connection_id: 'quic_conn_01',
      transport_session_id: 'wt_tsess_a',
      correlation_id: 'corr_wt_session_a',
      stream_id: '0',
      stream_correlation_id: 'scorr_a_0',
      invocation_id: `inv_wt_echo_${idx}`,
      rpc_id: `echo-${idx}`,
      duration_ms: dur,
      clock_domain: 'server.monotonic_ns',
      timing_boundary: 'invocation.started -> invocation.completed',
      observation: {
        measure: 'invocation_latency',
        unit: 'ms',
        value: dur,
        clock_domain: 'server.monotonic_ns',
        timing_boundary: 'invocation.started -> invocation.completed',
        provenance: 'tigrbl.runtime',
      },
    });
  }

  // Additional DB transactions for distribution depth (n = 24 total measured)
  for (let i = 3; i <= 23; i++) {
    const idx = i.toString().padStart(2, '0');
    const dur = sampleLatency(5.6, 3.8, 0.1);
    const rolledBack = i === 11;
    push(24, {
      transport: 'database',
      source: 'database',
      kind: rolledBack ? 'db.tx.rollback' : 'db.tx.commit',
      outcome: rolledBack ? 'rolled_back' : 'committed',
      label: rolledBack ? `DB tx rolled back (#${idx})` : `DB tx committed (#${idx})`,
      session_id: reqSess,
      invocation_id: `inv_rest_${idx}`,
      engine_session_id: i % 2 === 0 ? 'eng_pg_01' : 'eng_pg_02',
      transaction_id: `tx_batch_${idx}`,
      duration_ms: dur,
      clock_domain: 'server.monotonic_ns',
      timing_boundary: 'db.tx.begin -> db.tx.commit',
      observation: {
        measure: 'transaction_latency',
        unit: 'ms',
        value: dur,
        clock_domain: 'server.monotonic_ns',
        timing_boundary: 'db.tx.begin -> db.tx.commit',
        provenance: 'tigrbl.db.engine',
      },
    });
  }

  // Close QUIC sessions & connection at end of window
  push(25, {
    transport: 'webtransport',
    source: 'kernel',
    kind: 'wt.session.closed',
    framing: 'webtransport-h3',
    outcome: 'ok',
    label: 'WT Session A closed',
    connection_id: 'quic_conn_01',
    transport_session_id: 'wt_tsess_a',
    correlation_id: 'corr_wt_session_a',
  });
  push(8, {
    transport: 'webtransport',
    source: 'kernel',
    kind: 'wt.session.closed',
    framing: 'webtransport-h3',
    outcome: 'ok',
    label: 'WT Session B closed',
    connection_id: 'quic_conn_01',
    transport_session_id: 'wt_tsess_b',
    correlation_id: 'corr_wt_session_b',
  });
  push(6, {
    transport: 'webtransport',
    source: 'kernel',
    kind: 'quic.connection.closed',
    framing: 'quic-h3',
    outcome: 'ok',
    label: 'QUIC connection closed',
    connection_id: 'quic_conn_01',
  });

  return {
    revision: 1200,
    capture_id: captureId,
    captured_at: new Date(baseMs + t).toISOString(),
    dataset_label: 'Recorded synthetic contract fixture v1.2',
    is_synthetic: true,
    retention_limit: 750,
    retained_range: {
      min_sequence: events[0].sequence,
      max_sequence: events[events.length - 1].sequence,
      total_emitted: events[events.length - 1].sequence,
      evicted_count: 100, // Explicitly surfaces bounded retention indicator
    },
    running: false,
    active_run_id: null,
    last_run_summary: {
      run_id: runId,
      status: 'completed',
      started_at: new Date(baseMs).toISOString(),
      completed_at: new Date(baseMs + t).toISOString(),
      duration_ms: t,
      emitted_events: events.length,
      note_id: sharedNote,
      transports: {
        rest: 'POST /api/notes + retry commit + 25 reads',
        http_jsonrpc: '2-item batch read (shared tx) + 20 calls',
        websocket: 'v2 subscribe, gen-2 reattach, publish -> delivery',
        webtransport: '1 QUIC conn, 2 sessions, UDP rebind, echo, Session B reject',
      },
    },
    events,
    rollup: computeSnapshotRollup(events),
  };
}

let cachedContractFixture: TraceSnapshot | null = null;
let cachedStressFixture: TraceSnapshot | null = null;

function buildStressFixture10k(): TraceSnapshot {
  const rng = createRng(99887766);
  const baseMs = Date.UTC(2026, 10, 23, 21, 0, 0, 0);
  const captureId = 'rec_stress_10k';
  const events: RawTraceEvent[] = [];
  const total = 10000;
  const transports: Array<'rest' | 'http_jsonrpc' | 'websocket' | 'webtransport' | 'database'> = [
    'rest',
    'http_jsonrpc',
    'websocket',
    'webtransport',
    'database',
  ];

  for (let i = 1; i <= total; i++) {
    const tr = transports[i % 5];
    const atMs = baseMs + i * 3;
    const isErr = i % 47 === 0;
    const bucketGroup = (i % 12) + 1;
    const dur = Number((2.5 + ((rng() + rng()) * 14) + (isErr ? 18 : 0)).toFixed(2));
    const hasTiming = i % 6 !== 0;

    if (tr === 'rest') {
      events.push({
        sequence: i,
        at: new Date(atMs).toISOString(),
        capture_id: captureId,
        transport: 'rest',
        source: 'app',
        kind: isErr ? 'invocation.failed' : 'invocation.completed',
        outcome: isErr ? 'failed' : 'ok',
        http_status: isErr ? 500 : 200,
        label: `REST op #${i}`,
        connection_id: `tcp_stress_${bucketGroup % 4}`,
        request_id: `req_s_${bucketGroup}`,
        correlation_id: `corr_s_rest_${bucketGroup}`,
        invocation_id: `inv_s_rest_${i}`,
        ...(hasTiming
          ? {
              duration_ms: dur,
              clock_domain: 'server.monotonic_ns',
              timing_boundary: 'invocation.started -> invocation.completed',
              observation: {
                measure: 'invocation_latency',
                unit: 'ms',
                value: dur,
                clock_domain: 'server.monotonic_ns',
                timing_boundary: 'invocation.started -> invocation.completed',
                provenance: 'tigrbl.stress',
              },
            }
          : {}),
      });
    } else if (tr === 'http_jsonrpc') {
      events.push({
        sequence: i,
        at: new Date(atMs).toISOString(),
        capture_id: captureId,
        transport: 'http_jsonrpc',
        source: 'app',
        kind: isErr ? 'invocation.failed' : 'invocation.completed',
        outcome: isErr ? 'rejected' : 'ok',
        http_status: isErr ? 400 : 200,
        label: `JSON-RPC op #${i}`,
        connection_id: `tcp_stress_${bucketGroup % 4}`,
        request_id: `req_rpc_s_${bucketGroup}`,
        correlation_id: `corr_s_rpc_${bucketGroup}`,
        invocation_id: `inv_s_rpc_${i}`,
        rpc_id: `w_${i}`,
        ...(hasTiming
          ? {
              duration_ms: dur * 0.85,
              clock_domain: 'server.monotonic_ns',
              timing_boundary: 'invocation.started -> invocation.completed',
              observation: {
                measure: 'invocation_latency',
                unit: 'ms',
                value: Number((dur * 0.85).toFixed(2)),
                clock_domain: 'server.monotonic_ns',
                timing_boundary: 'invocation.started -> invocation.completed',
                provenance: 'tigrbl.stress',
              },
            }
          : {}),
      });
    } else if (tr === 'websocket') {
      const isDeliv = i % 2 === 0;
      events.push({
        sequence: i,
        at: new Date(atMs).toISOString(),
        capture_id: captureId,
        transport: 'websocket',
        source: isDeliv ? 'broker' : 'app',
        kind: isDeliv ? 'broker.delivery.dispatched' : 'invocation.completed',
        outcome: isErr ? 'rejected' : isDeliv ? 'delivered' : 'ok',
        label: isDeliv ? `WS delivery #${i}` : `WS publish #${i}`,
        connection_id: `ws_conn_s_${bucketGroup % 3}`,
        transport_session_id: `ws_tsess_s_${bucketGroup % 4}`,
        subscription_id: `sub_s_${bucketGroup % 3}`,
        attachment_generation: 1,
        publication_id: `pub_s_${Math.floor(i / 2)}`,
        ...(isDeliv ? { delivery_id: `deliv_s_${i}` } : { invocation_id: `inv_s_ws_${i}` }),
        ...(hasTiming
          ? {
              duration_ms: Number((dur * 0.5).toFixed(2)),
              clock_domain: 'broker.monotonic_ns',
              timing_boundary: isDeliv
                ? 'broker.publication.created -> broker.delivery.dispatched'
                : 'invocation.started -> invocation.completed',
              observation: {
                measure: isDeliv ? 'delivery_latency' : 'invocation_latency',
                unit: 'ms',
                value: Number((dur * 0.5).toFixed(2)),
                clock_domain: 'broker.monotonic_ns',
                timing_boundary: isDeliv
                  ? 'broker.publication.created -> broker.delivery.dispatched'
                  : 'invocation.started -> invocation.completed',
                provenance: 'tigrbl.stress',
              },
            }
          : {}),
      });
    } else if (tr === 'webtransport') {
      const isDgram = i % 3 === 0;
      const sess = bucketGroup % 2 === 0 ? 'wt_tsess_s_a' : 'wt_tsess_s_b';
      events.push({
        sequence: i,
        at: new Date(atMs).toISOString(),
        capture_id: captureId,
        transport: 'webtransport',
        source: isDgram ? 'kernel' : 'app',
        kind: isErr
          ? 'wt.stream.rejected'
          : isDgram
            ? 'wt.datagram.received'
            : 'invocation.completed',
        outcome: isErr ? 'rejected' : 'ok',
        direction: isDgram ? 'inbound' : 'bidirectional',
        label: isDgram ? `WT datagram #${i}` : `WT stream echo #${i}`,
        connection_id: 'quic_conn_stress_01',
        transport_session_id: sess,
        correlation_id: sess === 'wt_tsess_s_a' ? 'corr_wt_s_a' : 'corr_wt_s_b',
        ...(isDgram
          ? { datagram_id: `dg_s_${i}` }
          : {
              stream_id: `${(bucketGroup % 3) * 4}`,
              stream_correlation_id: `scorr_s_${sess}_${bucketGroup % 3}`,
              invocation_id: `inv_s_wt_${i}`,
            }),
        ...(!isDgram && hasTiming
          ? {
              duration_ms: Number((dur * 0.6).toFixed(2)),
              clock_domain: 'server.monotonic_ns',
              timing_boundary: 'invocation.started -> invocation.completed',
              observation: {
                measure: 'invocation_latency',
                unit: 'ms',
                value: Number((dur * 0.6).toFixed(2)),
                clock_domain: 'server.monotonic_ns',
                timing_boundary: 'invocation.started -> invocation.completed',
                provenance: 'tigrbl.stress',
              },
            }
          : {}),
      });
    } else {
      events.push({
        sequence: i,
        at: new Date(atMs).toISOString(),
        capture_id: captureId,
        transport: 'database',
        source: 'database',
        kind: isErr ? 'db.tx.rollback' : 'db.tx.commit',
        outcome: isErr ? 'rolled_back' : 'committed',
        label: `DB tx #${i}`,
        engine_session_id: `eng_s_${bucketGroup % 3}`,
        transaction_id: `tx_s_${i}`,
        invocation_id: `inv_s_rest_${i - 4}`,
        ...(hasTiming
          ? {
              duration_ms: Number((dur * 0.45).toFixed(2)),
              clock_domain: 'server.monotonic_ns',
              timing_boundary: 'db.tx.begin -> db.tx.commit',
              observation: {
                measure: 'transaction_latency',
                unit: 'ms',
                value: Number((dur * 0.45).toFixed(2)),
                clock_domain: 'server.monotonic_ns',
                timing_boundary: 'db.tx.begin -> db.tx.commit',
                provenance: 'tigrbl.db.engine',
              },
            }
          : {}),
      });
    }
  }

  return {
    revision: 10000,
    capture_id: captureId,
    captured_at: new Date(baseMs + total * 3).toISOString(),
    dataset_label: 'Recorded synthetic 10,000-row stress fixture',
    is_synthetic: true,
    retention_limit: 10000,
    retained_range: {
      min_sequence: 1,
      max_sequence: total,
      total_emitted: total,
      evicted_count: 0,
    },
    running: false,
    active_run_id: null,
    last_run_summary: null,
    events,
    rollup: computeSnapshotRollup(events),
  };
}

export function getRecordedSnapshot(datasetId: RecordedDatasetId): TraceSnapshot {
  if (datasetId === 'recorded-stress-10k') {
    if (!cachedStressFixture) {
      cachedStressFixture = buildStressFixture10k();
    }
    return cachedStressFixture;
  }
  if (!cachedContractFixture) {
    cachedContractFixture = buildContractFixture();
  }
  return cachedContractFixture;
}
