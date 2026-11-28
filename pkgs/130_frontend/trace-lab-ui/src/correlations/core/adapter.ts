import type {
  DirectionLabel,
  KnownEventKind,
  NormalizedSnapshot,
  NormalizedTraceEvent,
  RawTraceEventInput,
  TimeBasis,
  TraceSnapshotInput,
} from './types';

export const ADAPTER_VERSION = '2.1.0';

const KNOWN_EVENT_KINDS = new Set<KnownEventKind>([
  'http.request.received',
  'http.response.sent',
  'rpc.document.received',
  'rpc.batch.item.invoked',
  'rpc.batch.item.completed',
  'rpc.notification.received',
  'rpc.response.sent',
  'invocation.started',
  'invocation.completed',
  'hook.completed',
  'atom.completed',
  'atom.failed',
  'db.tx.participant',
  'db.tx.begin',
  'db.tx.query',
  'db.tx.commit',
  'db.tx.rollback',
  'db.flush.completed',
  'db.flush.failed',
  'ws.session.opened',
  'ws.frame.received',
  'ws.frame.sent',
  'ws.broker.publish',
  'ws.broker.delivery',
  'ws.subscription.attached',
  'wt.quic.connected',
  'wt.session.opened',
  'wt.stream.opened',
  'wt.stream.frame.received',
  'wt.stream.frame.sent',
  'wt.stream.closed',
  'wt.datagram.received',
  'wt.datagram.sent',
]);

// Strictly allowlisted metadata keys surfaced in inspector & URLs
export const ALLOWLISTED_META_KEYS = new Set<string>([
  'method',
  'route',
  'topic',
  'bytes',
  'status_code',
  'note',
  'timing_boundary',
  'clock_domain',
  'observer',
  'service',
  'environment',
  'op_model',
  'op_alias',
  'hook_name',
  'hook_phase',
  'flush_id',
  'atom_label',
  'atom_phase',
  'atom_ordinal',
  'atom_trace_dropped',
  'rpc_item_index',
  'rpc_is_notification',
]);

/**
 * Losslessly normalizes opaque identifiers (strings or large/numeric IDs) to strings.
 * Empty/null/undefined returns undefined.
 */
export function normalizeOpaqueId(val: unknown): string | undefined {
  if (val === null || val === undefined) return undefined;
  if (typeof val === 'string') {
    const trimmed = val.trim();
    return trimmed.length > 0 ? trimmed : undefined;
  }
  if (typeof val === 'number') {
    if (!Number.isFinite(val)) return undefined;
    return String(val);
  }
  if (typeof val === 'bigint') {
    return val.toString();
  }
  return undefined;
}

function parseTimestampMs(iso: string | null | undefined): number | undefined {
  if (!iso || typeof iso !== 'string') return undefined;
  const ms = Date.parse(iso);
  return Number.isFinite(ms) ? ms : undefined;
}

function parseSourceTimestampMs(iso: string | null | undefined): number | undefined {
  const ms = parseTimestampMs(iso);
  if (ms === undefined) return undefined;
  const fraction = iso?.match(/\.\d{3}(\d+)/)?.[1];
  return fraction ? ms + Number(`0.${fraction}`) : ms;
}

function resolveDirectionLabel(
  rawDirection: RawTraceEventInput['direction'],
  observer: string | undefined,
  kind: string
): { label: DirectionLabel; raw: 'inbound' | 'outbound' | 'internal' | 'unknown' } {
  if (rawDirection === 'inbound') {
    return { label: 'Ingress', raw: 'inbound' };
  }
  if (rawDirection === 'outbound') {
    return { label: 'Egress', raw: 'outbound' };
  }
  if (rawDirection === 'internal') {
    return { label: 'Observed at server', raw: 'internal' };
  }
  if (rawDirection === 'unknown') {
    return { label: 'Direction unavailable', raw: 'unknown' };
  }

  // Fallback by explicit known event semantics only (never guess unknown kinds)
  if (
    kind === 'http.request.received' ||
    kind === 'rpc.document.received' ||
    kind === 'rpc.notification.received' ||
    kind === 'ws.frame.received' ||
    kind === 'wt.stream.frame.received' ||
    kind === 'wt.datagram.received'
  ) {
    return { label: 'Ingress', raw: 'inbound' };
  }
  if (
    kind === 'http.response.sent' ||
    kind === 'rpc.response.sent' ||
    kind === 'ws.frame.sent' ||
    kind === 'ws.broker.delivery' ||
    kind === 'wt.stream.frame.sent' ||
    kind === 'wt.datagram.sent'
  ) {
    return { label: 'Egress', raw: 'outbound' };
  }
  if (observer && observer.trim().length > 0 && KNOWN_EVENT_KINDS.has(kind as KnownEventKind)) {
    return { label: 'Observed at server', raw: 'internal' };
  }
  return { label: 'Direction unavailable', raw: 'unknown' };
}

function resolveTimeBasis(
  raw: RawTraceEventInput,
  sourceStartMs?: number,
  sourceEndMs?: number,
  atMs?: number
): TimeBasis {
  if (
    typeof raw.measured_duration_ms === 'number' &&
    Number.isFinite(raw.measured_duration_ms) &&
    raw.measured_duration_ms >= 0 &&
    raw.timing_boundary && raw.clock_domain && raw.clock_domain !== 'mixed'
  ) {
    return 'measured_monotonic';
  }
  if (sourceStartMs !== undefined && sourceEndMs !== undefined) {
    if (sourceEndMs < sourceStartMs) {
      return 'clock_skewed';
    }
    return 'partial_mixed';
  }
  if (sourceStartMs !== undefined && atMs !== undefined) {
    return 'partial_mixed';
  }
  return 'recorded_at';
}

export function normalizeEvent(raw: RawTraceEventInput): NormalizedTraceEvent {
  const atMs = parseTimestampMs(raw.at) ?? 0;
  const sourceStartedAtMs = parseSourceTimestampMs(raw.source_started_at);
  const sourceEndedAtMs = parseSourceTimestampMs(raw.source_ended_at);
  const isKnownKind = KNOWN_EVENT_KINDS.has(raw.kind as KnownEventKind);

  const engineSessionId = normalizeOpaqueId(raw.engine_session_id);
  const transactionId = normalizeOpaqueId(raw.transaction_id);
  const transactionKey =
    engineSessionId && transactionId
      ? `${engineSessionId}::${transactionId}`
      : transactionId
      ? `unscoped_engine::${transactionId}`
      : undefined;

  const { label: directionLabel, raw: rawDirection } = resolveDirectionLabel(
    raw.direction,
    raw.observer,
    raw.kind
  );

  const timeBasis = resolveTimeBasis(raw, sourceStartedAtMs, sourceEndedAtMs, atMs);

  const measuredDurationMs =
    typeof raw.measured_duration_ms === 'number' &&
    Number.isFinite(raw.measured_duration_ms) &&
    raw.measured_duration_ms >= 0
      ? raw.measured_duration_ms
      : timeBasis === 'measured_monotonic' &&
        sourceStartedAtMs !== undefined &&
        sourceEndedAtMs !== undefined &&
        sourceEndedAtMs >= sourceStartedAtMs
      ? sourceEndedAtMs - sourceStartedAtMs
      : undefined;

  const allowlistedMeta: Record<string, string | number | boolean> = {};
  for (const key of ALLOWLISTED_META_KEYS) {
    const val = raw[key];
    if (
      typeof val === 'string' ||
      typeof val === 'number' ||
      typeof val === 'boolean'
    ) {
      if (typeof val === 'string' && val.trim().length === 0) continue;
      allowlistedMeta[key] = val;
    }
  }

  return {
    seq: Number.isFinite(raw.seq) ? raw.seq : 0,
    at: raw.at,
    atMs,
    kind: raw.kind,
    isKnownKind,
    protocol: raw.protocol,
    service: raw.service,
    environment: raw.environment,
    directionLabel,
    rawDirection,
    observer: typeof raw.observer === 'string' && raw.observer.trim() ? raw.observer.trim() : 'sink',
    correlationId: normalizeOpaqueId(raw.correlation_id),
    originCorrelationId: normalizeOpaqueId(raw.origin_correlation_id),
    originInvocationId: normalizeOpaqueId(raw.origin_invocation_id),
    receivingCorrelationId: normalizeOpaqueId(raw.receiving_correlation_id),
    requestId: normalizeOpaqueId(raw.request_id),
    rpcId: normalizeOpaqueId(raw.rpc_id),
    rpcItemIndex: typeof raw.rpc_item_index === 'number' ? raw.rpc_item_index : undefined,
    rpcIsNotification: Boolean(raw.rpc_is_notification || raw.kind === 'rpc.notification.received'),
    invocationId: normalizeOpaqueId(raw.invocation_id),
    transportSessionId: normalizeOpaqueId(raw.transport_session_id),
    requesterSessionId: normalizeOpaqueId(raw.requester_session_id),
    quicConnectionId: normalizeOpaqueId(raw.quic_connection_id),
    streamId: normalizeOpaqueId(raw.stream_id),
    streamCorrelationId: normalizeOpaqueId(raw.stream_correlation_id),
    datagramId: normalizeOpaqueId(raw.datagram_id),
    subscriptionId: normalizeOpaqueId(raw.subscription_id),
    attachmentGeneration: normalizeOpaqueId(raw.attachment_generation),
    destinationId: normalizeOpaqueId(raw.destination_id),
    engineSessionId,
    transactionId,
    transactionKey,
    sourceStartedAt: raw.source_started_at ?? undefined,
    sourceStartedAtMs,
    sourceEndedAt: raw.source_ended_at ?? undefined,
    sourceEndedAtMs,
    measuredDurationMs,
    timingBoundary: raw.timing_boundary ?? undefined,
    clockDomain: raw.clock_domain ?? undefined,
    timeBasis,
    outcome: raw.outcome ?? 'unknown',
    statusCode: typeof raw.status_code === 'number' ? raw.status_code : undefined,
    allowlistedMeta,
    linkedFromSeq: typeof raw.linked_from_seq === 'number' ? raw.linked_from_seq : undefined,
    externalEndpointLabel:
      typeof raw.external_endpoint_label === 'string' ? raw.external_endpoint_label : undefined,
    evictedEndpointId: normalizeOpaqueId(raw.evicted_endpoint_id),
  };
}

export function adaptSnapshot(input: TraceSnapshotInput): NormalizedSnapshot {
  const events: NormalizedTraceEvent[] = [];
  let unknownKindCount = 0;

  for (const raw of input.events ?? []) {
    const ev = normalizeEvent(raw);
    if (!ev.isKnownKind) unknownKindCount++;
    events.push(ev);
  }

  // Deterministic ordering by recorded time, then capture sequence for ties
  events.sort((a, b) => (a.atMs !== b.atMs ? a.atMs - b.atMs : a.seq - b.seq));

  return {
    captureId: input.capture_id,
    adapterVersion: input.adapter_version ?? ADAPTER_VERSION,
    mode: input.mode,
    syntheticLabel: input.synthetic_label,
    fixtureId: input.fixture_id,
    sequenceFloor: input.sequence_floor,
    sequenceCeiling: input.sequence_ceiling,
    retainedCount: input.retained_count,
    evictedCount: input.evicted_count,
    generatedAt: input.generated_at,
    bounded: input.bounded,
    events,
    unknownKindCount,
  };
}
