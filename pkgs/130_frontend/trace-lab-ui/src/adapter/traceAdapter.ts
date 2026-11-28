import { PROTOCOL_LABELS } from '../theme/tokens';
import {
  DistributionBin,
  DistributionLaneResult,
  DistributionMeasure,
  EntityKind,
  EventOutcome,
  EventRole,
  FilterState,
  KaryogramRow,
  NormalizedEvent,
  PrimaryProtocol,
  QuantileSummary,
  RawTraceEvent,
  RelationshipArc,
  SelectionState,
  TraceSnapshot,
  TransportProtocol,
  TypedEntity,
  TypedIdKey,
} from '../types/trace';

const KNOWN_KINDS = new Set([
  'http.request.received',
  'http.response.sent',
  'invocation.started',
  'invocation.completed',
  'invocation.failed',
  'hook.completed',
  'atom.completed',
  'atom.failed',
  'ws.session.opened',
  'ws.session.closed',
  'ws.message.received',
  'ws.message.sent',
  'broker.subscription.acknowledged',
  'broker.subscription.reattached',
  'broker.publication.created',
  'broker.delivery.dispatched',
  'broker.delivery.rejected',
  'quic.connection.established',
  'quic.connection.closed',
  'wt.connection.rebind',
  'wt.session.opened',
  'wt.session.closed',
  'wt.stream.opened',
  'wt.stream.closed',
  'wt.stream.rejected',
  'wt.datagram.received',
  'wt.datagram.sent',
  'db.tx.begin',
  'db.tx.participant',
  'db.tx.commit',
  'db.tx.rollback',
  'db.flush.completed',
  'db.flush.failed',
]);

export const TYPED_ID_KEYS: Array<{ key: TypedIdKey; label: string }> = [
  { key: 'session_id', label: 'Requester session' },
  { key: 'connection_id', label: 'Connection' },
  { key: 'transport_session_id', label: 'Transport session' },
  { key: 'request_id', label: 'Request' },
  { key: 'correlation_id', label: 'Correlation' },
  { key: 'stream_id', label: 'Stream ID' },
  { key: 'stream_correlation_id', label: 'Stream correlation' },
  { key: 'invocation_id', label: 'Invocation' },
  { key: 'rpc_id', label: 'JSON-RPC wire ID' },
  { key: 'datagram_id', label: 'Datagram' },
  { key: 'subscription_id', label: 'Subscription' },
  { key: 'lease_id', label: 'Lease' },
  { key: 'publication_id', label: 'Publication' },
  { key: 'delivery_id', label: 'Delivery' },
  { key: 'origin_invocation_id', label: 'Origin invocation' },
  { key: 'origin_correlation_id', label: 'Origin correlation' },
  { key: 'engine_session_id', label: 'Engine session' },
  { key: 'transaction_id', label: 'Transaction' },
];

export function truncateId(id: string, max = 18): string {
  if (id.length <= max) return id;
  const keep = Math.max(4, Math.floor((max - 1) / 2));
  return `${id.slice(0, keep)}…${id.slice(-keep)}`;
}

export function formatUtcTime(ms: number, includeMs = true): string {
  const d = new Date(ms);
  const hh = d.getUTCHours().toString().padStart(2, '0');
  const mm = d.getUTCMinutes().toString().padStart(2, '0');
  const ss = d.getUTCSeconds().toString().padStart(2, '0');
  if (!includeMs) return `${hh}:${mm}:${ss}Z`;
  const mmm = d.getUTCMilliseconds().toString().padStart(3, '0');
  return `${hh}:${mm}:${ss}.${mmm}Z`;
}

export function formatOffsetMs(deltaMs: number): string {
  if (Math.abs(deltaMs) < 1000) return `+${Math.round(deltaMs)}ms`;
  return `+${(deltaMs / 1000).toFixed(2)}s`;
}

function deriveEventRole(ev: RawTraceEvent): EventRole {
  const outcome = ev.outcome ?? 'unknown';
  if (outcome === 'rejected' || outcome === 'failed' || outcome === 'rolled_back') {
    return 'rejected';
  }
  if (ev.kind === 'wt.datagram.received' || ev.kind === 'wt.datagram.sent') {
    return 'neutral';
  }
  if (outcome === 'open' || outcome === 'partial') {
    if (
      ev.kind.startsWith('quic.') ||
      ev.kind.startsWith('ws.session') ||
      ev.kind.startsWith('wt.session') ||
      ev.kind.startsWith('wt.stream')
    ) {
      return 'carrier';
    }
    if (ev.kind.startsWith('invocation.') || ev.kind.startsWith('db.tx')) {
      return 'invocation';
    }
    return 'partial';
  }
  if (
    ev.kind === 'invocation.completed' ||
    ev.kind === 'http.response.sent' ||
    ev.kind === 'db.tx.commit' ||
    ev.kind === 'broker.delivery.dispatched' ||
    ev.kind === 'broker.subscription.acknowledged' ||
    ev.kind === 'broker.subscription.reattached'
  ) {
    return 'success';
  }
  if (
    ev.kind.startsWith('quic.') ||
    ev.kind.startsWith('wt.connection') ||
    ev.kind.startsWith('wt.session') ||
    ev.kind.startsWith('wt.stream') ||
    ev.kind.startsWith('ws.session')
  ) {
    return 'carrier';
  }
  if (
    ev.kind.startsWith('invocation.') ||
    ev.kind.startsWith('broker.') ||
    ev.kind.startsWith('db.tx')
  ) {
    return 'invocation';
  }
  return 'neutral';
}

export function formatOutcomeLabel(outcome: EventOutcome | undefined, httpStatus?: number): string {
  const base = outcome ?? 'unknown';
  const map: Record<EventOutcome, string> = {
    ok: 'OK',
    committed: 'Committed',
    delivered: 'Delivered',
    rejected: 'Rejected',
    failed: 'Failed',
    rolled_back: 'Rolled back',
    open: 'Open',
    partial: 'Partial',
    unknown: 'Unknown',
  };
  const text = map[base] ?? 'Unknown';
  return httpStatus ? `${text} (${httpStatus})` : text;
}

export function normalizeSnapshotEvents(snapshot: TraceSnapshot | null): NormalizedEvent[] {
  if (!snapshot || !Array.isArray(snapshot.events)) return [];

  const captureId = String(snapshot.capture_id || 'cap_unknown');
  const seenSeq = new Set<number>();
  const normalized: NormalizedEvent[] = [];

  for (const raw of snapshot.events) {
    if (typeof raw?.sequence !== 'number' || typeof raw?.at !== 'string') continue;
    // Deduplicate exact duplicate sequence numbers while retaining first authoritative record
    if (seenSeq.has(raw.sequence)) continue;
    seenSeq.add(raw.sequence);

    const parsedMs = Date.parse(raw.at);
    const atMs = Number.isFinite(parsedMs) ? parsedMs : 0;
    const knownKind = KNOWN_KINDS.has(raw.kind);
    const role = deriveEventRole(raw);

    // Ensure all IDs stay opaque strings (never coerced through JS Number)
    const cleanStr = (v: unknown): string | undefined =>
      v === undefined || v === null || v === '' ? undefined : String(v);

    const transportSessionId = cleanStr(raw.transport_session_id);
    const streamId = cleanStr(raw.stream_id);
    const engineSessionId = cleanStr(raw.engine_session_id);
    const transactionId = cleanStr(raw.transaction_id);
    const rpcId = cleanStr(raw.rpc_id);
    const correlationId = cleanStr(raw.correlation_id);
    const requestId = cleanStr(raw.request_id);
    const invocationId = cleanStr(raw.invocation_id);

    const scopedStreamKey =
      transportSessionId && streamId ? `${transportSessionId}::${streamId}` : undefined;
    const scopedTransactionKey =
      engineSessionId && transactionId ? `${engineSessionId}::${transactionId}` : undefined;
    const exchangeScope = correlationId || requestId || invocationId || 'exchange';
    const scopedRpcKey = rpcId
      ? `${exchangeScope}::${rpcId}${raw.rpc_item_index !== undefined ? `#${raw.rpc_item_index}` : ''}`
      : undefined;

    normalized.push({
      ...raw,
      session_id: cleanStr(raw.session_id),
      transport_session_id: transportSessionId,
      connection_id: cleanStr(raw.connection_id),
      request_id: requestId,
      correlation_id: correlationId,
      stream_id: streamId,
      stream_correlation_id: cleanStr(raw.stream_correlation_id),
      invocation_id: invocationId,
      rpc_id: rpcId,
      datagram_id: cleanStr(raw.datagram_id),
      subscription_id: cleanStr(raw.subscription_id),
      lease_id: cleanStr(raw.lease_id),
      publication_id: cleanStr(raw.publication_id),
      delivery_id: cleanStr(raw.delivery_id),
      origin_invocation_id: cleanStr(raw.origin_invocation_id),
      origin_correlation_id: cleanStr(raw.origin_correlation_id),
      engine_session_id: engineSessionId,
      transaction_id: transactionId,
      note_id: cleanStr(raw.note_id),
      id: `${captureId}:${raw.sequence}`,
      atMs,
      normalizedKind: raw.kind,
      knownKind,
      role,
      displayLabel:
        raw.hook_phase && raw.hook_name
          ? `${raw.hook_phase} · ${raw.hook_name}`
          : raw.op_model && raw.op_alias
            ? `${raw.op_model}.${raw.op_alias}`
            : raw.atom_label || raw.label || raw.kind,
      outcomeLabel: formatOutcomeLabel(raw.outcome, raw.http_status),
      source: raw.source ?? 'unknown',
      scopedStreamKey,
      scopedTransactionKey,
      scopedRpcKey,
    });
  }

  // Order strictly by snapshot ingestion sequence (tie-breaking by atMs)
  normalized.sort((a, b) => a.sequence - b.sequence || a.atMs - b.atMs);
  return normalized;
}

export interface EntityGraph {
  entities: Map<string, TypedEntity>;
  rootIds: string[];
  eventToEntityIds: Map<string, string[]>;
  eventById: Map<string, NormalizedEvent>;
  eventBySequence: Map<number, NormalizedEvent>;
  invocationToTxIds: Map<string, Set<string>>;
  txToInvocationIds: Map<string, Set<string>>;
  noteToInvocationIds: Map<string, Set<string>>;
  minMs: number;
  maxMs: number;
}

export function buildEntityGraph(events: NormalizedEvent[]): EntityGraph {
  const entities = new Map<string, TypedEntity>();
  const rootIds: string[] = [];
  const eventToEntityIds = new Map<string, string[]>();
  const eventById = new Map<string, NormalizedEvent>();
  const eventBySequence = new Map<number, NormalizedEvent>();
  const invocationToTxIds = new Map<string, Set<string>>();
  const txToInvocationIds = new Map<string, Set<string>>();
  const noteToInvocationIds = new Map<string, Set<string>>();

  let minMs = Number.POSITIVE_INFINITY;
  let maxMs = Number.NEGATIVE_INFINITY;

  const ensureEntity = (
    id: string,
    init: Omit<TypedEntity, 'eventSequences' | 'startMs' | 'endMs' | 'isOpen' | 'links' | 'childrenIds' | 'typedIds'> & {
      typedIds?: Partial<Record<TypedIdKey, string>>;
    }
  ): TypedEntity => {
    let existing = entities.get(id);
    if (!existing) {
      existing = {
        ...init,
        eventSequences: [],
        startMs: null,
        endMs: null,
        isOpen: false,
        links: [],
        childrenIds: [],
        typedIds: { ...(init.typedIds ?? {}) },
      };
      entities.set(id, existing);
      if (init.parentId === null) {
        if (!rootIds.includes(id)) rootIds.push(id);
      } else {
        const parent = entities.get(init.parentId);
        if (parent && !parent.childrenIds.includes(id)) {
          parent.childrenIds.push(id);
        }
      }
    } else if (init.typedIds) {
      for (const [k, v] of Object.entries(init.typedIds)) {
        if (v && !existing.typedIds[k as TypedIdKey]) {
          existing.typedIds[k as TypedIdKey] = v;
        }
      }
    }
    return existing;
  };

  const attachEvent = (entity: TypedEntity, ev: NormalizedEvent) => {
    entity.eventSequences.push(ev.sequence);
    if (entity.startMs === null || ev.atMs < entity.startMs) entity.startMs = ev.atMs;
    if (entity.endMs === null || ev.atMs > entity.endMs) entity.endMs = ev.atMs;
    if (ev.outcome === 'rejected' || ev.outcome === 'failed' || ev.outcome === 'rolled_back') {
      entity.outcome = ev.outcome;
      entity.role = 'rejected';
    } else if (entity.outcome === 'unknown' && ev.outcome) {
      entity.outcome = ev.outcome;
    }

    const list = eventToEntityIds.get(ev.id) ?? [];
    if (!list.includes(entity.id)) {
      list.push(entity.id);
      eventToEntityIds.set(ev.id, list);
    }
  };

  const addLink = (entity: TypedEntity, link: TypedEntity['links'][number]) => {
    const exists = entity.links.find(
      (l) => l.targetId === link.targetId && l.relationship === link.relationship
    );
    if (!exists) {
      entity.links.push(link);
    } else {
      for (const s of link.evidenceSequences) {
        if (!exists.evidenceSequences.includes(s)) exists.evidenceSequences.push(s);
      }
    }
  };

  // Pre-collect retained invocation IDs for unretained link checks
  const retainedInvocations = new Set<string>();
  for (const ev of events) {
    eventById.set(ev.id, ev);
    eventBySequence.set(ev.sequence, ev);
    if (ev.atMs < minMs) minMs = ev.atMs;
    if (ev.atMs > maxMs) maxMs = ev.atMs;
    if (ev.invocation_id) retainedInvocations.add(ev.invocation_id);
  }

  for (const ev of events) {
    const protoId = `protocol:${ev.transport}`;
    const protoEntity = ensureEntity(protoId, {
      id: protoId,
      entityKind: 'protocol',
      transport: ev.transport,
      label: PROTOCOL_LABELS[ev.transport] || ev.transport,
      shortId: ev.transport,
      fullId: ev.transport,
      idField: 'composite',
      parentId: null,
      outcome: 'ok',
      role: ev.transport === 'database' ? 'invocation' : 'carrier',
    });
    attachEvent(protoEntity, ev);

    if (ev.note_id && ev.invocation_id) {
      const set = noteToInvocationIds.get(ev.note_id) ?? new Set<string>();
      set.add(ev.invocation_id);
      noteToInvocationIds.set(ev.note_id, set);
    }

    if (ev.scopedTransactionKey && ev.invocation_id) {
      const txId = `transaction:${ev.scopedTransactionKey}`;
      const invId = `invocation:${ev.invocation_id}`;
      const txSet = invocationToTxIds.get(invId) ?? new Set<string>();
      txSet.add(txId);
      invocationToTxIds.set(invId, txSet);
      const invSet = txToInvocationIds.get(txId) ?? new Set<string>();
      invSet.add(invId);
      txToInvocationIds.set(txId, invSet);
    }

    // --------------------------------------------------------------
    // Carrier-specific hierarchy indexing
    // --------------------------------------------------------------
    if (ev.transport === 'rest' || ev.transport === 'http_jsonrpc') {
      const reqKey = ev.request_id || ev.correlation_id || `seq_${ev.sequence}`;
      const reqEntityId = `request:${ev.transport}:${reqKey}`;
      const reqEntity = ensureEntity(reqEntityId, {
        id: reqEntityId,
        entityKind: 'request',
        transport: ev.transport,
        label:
          ev.transport === 'http_jsonrpc' && ev.metadata?.batch_size && Number(ev.metadata.batch_size) > 1
            ? `JSON-RPC batch (${ev.metadata.batch_size})`
            : ev.transport === 'http_jsonrpc'
              ? 'JSON-RPC exchange'
              : 'REST request',
        shortId: truncateId(reqKey),
        fullId: reqKey,
        idField: ev.request_id ? 'request_id' : 'correlation_id',
        parentId: protoId,
        outcome: ev.outcome ?? 'unknown',
        role: 'carrier',
        typedIds: {
          session_id: ev.session_id,
          connection_id: ev.connection_id,
          request_id: ev.request_id,
          correlation_id: ev.correlation_id,
        },
      });
      attachEvent(reqEntity, ev);

      if (ev.invocation_id) {
        const invEntityId = `invocation:${ev.invocation_id}`;
        const batchSuffix =
          ev.rpc_item_index !== undefined ? ` [item #${ev.rpc_item_index}]` : '';
        const invEntity = ensureEntity(invEntityId, {
          id: invEntityId,
          entityKind: 'invocation',
          transport: ev.transport,
          label: `${ev.metadata?.rpc_method || (ev.transport === 'rest' ? 'REST operation' : 'RPC invocation')}${batchSuffix}`,
          shortId: truncateId(ev.invocation_id),
          fullId: ev.invocation_id,
          idField: 'invocation_id',
          parentId: reqEntityId,
          outcome: ev.outcome ?? 'unknown',
          role: 'invocation',
          typedIds: {
            session_id: ev.session_id,
            connection_id: ev.connection_id,
            request_id: ev.request_id,
            correlation_id: ev.correlation_id,
            invocation_id: ev.invocation_id,
            rpc_id: ev.rpc_id,
          },
        });
        attachEvent(invEntity, ev);
      }
    } else if (ev.transport === 'websocket') {
      let parentId = protoId;
      if (ev.connection_id) {
        const connEntityId = `connection:${ev.connection_id}`;
        const connEntity = ensureEntity(connEntityId, {
          id: connEntityId,
          entityKind: 'connection',
          transport: 'websocket',
          label: 'WS connection',
          shortId: truncateId(ev.connection_id),
          fullId: ev.connection_id,
          idField: 'connection_id',
          parentId: protoId,
          outcome: 'ok',
          role: 'carrier',
          typedIds: { connection_id: ev.connection_id, session_id: ev.session_id },
        });
        attachEvent(connEntity, ev);
        parentId = connEntityId;
      }

      if (ev.transport_session_id) {
        const sessEntityId = `transport_session:${ev.transport_session_id}`;
        const isPub = ev.transport_session_id.includes('pub');
        const isSub = ev.transport_session_id.includes('sub');
        const sessEntity = ensureEntity(sessEntityId, {
          id: sessEntityId,
          entityKind: 'transport_session',
          transport: 'websocket',
          label: isPub ? 'WS publisher session' : isSub ? 'WS subscriber session' : 'WS transport session',
          shortId: truncateId(ev.transport_session_id),
          fullId: ev.transport_session_id,
          idField: 'transport_session_id',
          parentId,
          outcome: 'ok',
          role: 'carrier',
          typedIds: {
            connection_id: ev.connection_id,
            transport_session_id: ev.transport_session_id,
            session_id: ev.session_id,
          },
        });
        attachEvent(sessEntity, ev);
        parentId = sessEntityId;
      }

      if (ev.invocation_id) {
        const invEntityId = `invocation:${ev.invocation_id}`;
        const invEntity = ensureEntity(invEntityId, {
          id: invEntityId,
          entityKind: 'invocation',
          transport: 'websocket',
          label: ev.metadata?.rpc_method ? `WS ${ev.metadata.rpc_method}` : 'WS invocation',
          shortId: truncateId(ev.invocation_id),
          fullId: ev.invocation_id,
          idField: 'invocation_id',
          parentId,
          outcome: ev.outcome ?? 'unknown',
          role: 'invocation',
          typedIds: {
            session_id: ev.session_id,
            connection_id: ev.connection_id,
            transport_session_id: ev.transport_session_id,
            correlation_id: ev.correlation_id,
            invocation_id: ev.invocation_id,
            rpc_id: ev.rpc_id,
            publication_id: ev.publication_id,
          },
        });
        attachEvent(invEntity, ev);
      }

      // Logical subscription lane (retains logical ID across attachment generations)
      if (ev.subscription_id) {
        const subEntityId = `subscription:${ev.subscription_id}`;
        const subEntity = ensureEntity(subEntityId, {
          id: subEntityId,
          entityKind: 'subscription',
          transport: 'websocket',
          label: 'Subscription lane',
          shortId: truncateId(ev.subscription_id),
          fullId: ev.subscription_id,
          idField: 'subscription_id',
          parentId: protoId,
          outcome: ev.outcome ?? 'ok',
          role: 'invocation',
          typedIds: {
            subscription_id: ev.subscription_id,
            lease_id: ev.lease_id,
            transport_session_id: ev.transport_session_id,
          },
        });
        attachEvent(subEntity, ev);

        if (ev.attachment_generation !== undefined) {
          subEntity.attachmentGenerations = subEntity.attachmentGenerations ?? [];
          const already = subEntity.attachmentGenerations.find(
            (g) => g.generation === ev.attachment_generation && g.sequence === ev.sequence
          );
          if (!already) {
            subEntity.attachmentGenerations.push({
              generation: ev.attachment_generation,
              transport_session_id: ev.transport_session_id,
              lease_id: ev.lease_id,
              at: ev.at,
              sequence: ev.sequence,
              status: ev.displayLabel,
            });
          }
        }

        if (ev.origin_invocation_id) {
          const retained = retainedInvocations.has(ev.origin_invocation_id);
          addLink(subEntity, {
            targetType: 'invocation',
            targetId: `invocation:${ev.origin_invocation_id}`,
            label: `Publisher ${truncateId(ev.origin_invocation_id)}`,
            relationship: ev.delivery_id ? `delivery (${ev.delivery_id})` : 'origin_publication',
            unretained: !retained,
            evidenceSequences: [ev.sequence],
          });
          if (retained) {
            const originEntity = entities.get(`invocation:${ev.origin_invocation_id}`);
            if (originEntity) {
              addLink(originEntity, {
                targetType: 'subscription',
                targetId: subEntityId,
                label: `Recipient ${truncateId(ev.subscription_id)}`,
                relationship: ev.delivery_id ? `delivered (${ev.delivery_id})` : 'notifies',
                evidenceSequences: [ev.sequence],
              });
            }
          }
        }
      }
    } else if (ev.transport === 'webtransport') {
      const connKey = ev.connection_id || 'quic_unscoped';
      const connEntityId = `connection:${connKey}`;
      const connEntity = ensureEntity(connEntityId, {
        id: connEntityId,
        entityKind: 'connection',
        transport: 'webtransport',
        label: 'QUIC connection',
        shortId: truncateId(connKey),
        fullId: connKey,
        idField: 'connection_id',
        parentId: protoId,
        outcome: 'ok',
        role: 'carrier',
        typedIds: { connection_id: ev.connection_id },
      });
      attachEvent(connEntity, ev);

      if (ev.transport_session_id) {
        const sessEntityId = `transport_session:${ev.transport_session_id}`;
        const isA = ev.transport_session_id.includes('_a');
        const isB = ev.transport_session_id.includes('_b');
        const sessEntity = ensureEntity(sessEntityId, {
          id: sessEntityId,
          entityKind: 'transport_session',
          transport: 'webtransport',
          label: isA ? 'WT session A' : isB ? 'WT session B' : 'WT session',
          shortId: truncateId(ev.correlation_id || ev.transport_session_id),
          fullId: ev.transport_session_id,
          idField: 'transport_session_id',
          parentId: connEntityId,
          outcome: 'ok',
          role: 'carrier',
          extraCaption: ev.correlation_id ? `corr ${truncateId(ev.correlation_id, 14)}` : undefined,
          typedIds: {
            connection_id: ev.connection_id,
            transport_session_id: ev.transport_session_id,
            correlation_id: ev.correlation_id,
            session_id: ev.session_id,
          },
        });
        attachEvent(sessEntity, ev);

        if (ev.datagram_id || ev.kind.startsWith('wt.datagram')) {
          const dgLaneId = `datagrams:${ev.transport_session_id}`;
          const dgLane = ensureEntity(dgLaneId, {
            id: dgLaneId,
            entityKind: 'datagrams',
            transport: 'webtransport',
            label: 'Datagrams',
            shortId: truncateId(ev.transport_session_id, 12),
            fullId: ev.transport_session_id,
            idField: 'transport_session_id',
            parentId: sessEntityId,
            outcome: 'ok',
            role: 'neutral',
            typedIds: {
              connection_id: ev.connection_id,
              transport_session_id: ev.transport_session_id,
              correlation_id: ev.correlation_id,
            },
          });
          attachEvent(dgLane, ev);
        } else if (ev.scopedStreamKey && ev.stream_id) {
          const streamEntityId = `stream:${ev.scopedStreamKey}`;
          const dirLabel = ev.direction === 'unidirectional' ? 'Uni' : 'Bidi';
          const streamEntity = ensureEntity(streamEntityId, {
            id: streamEntityId,
            entityKind: 'stream',
            transport: 'webtransport',
            label: `${dirLabel} stream #${ev.stream_id}`,
            shortId: ev.stream_correlation_id
              ? truncateId(ev.stream_correlation_id, 14)
              : `#${ev.stream_id}`,
            fullId: ev.scopedStreamKey,
            idField: 'stream_id',
            parentId: sessEntityId,
            outcome: ev.outcome ?? 'unknown',
            role: 'carrier',
            typedIds: {
              connection_id: ev.connection_id,
              transport_session_id: ev.transport_session_id,
              correlation_id: ev.correlation_id,
              stream_id: ev.stream_id,
              stream_correlation_id: ev.stream_correlation_id,
            },
          });
          attachEvent(streamEntity, ev);

          if (ev.invocation_id) {
            const invEntityId = `invocation:${ev.invocation_id}`;
            const invEntity = ensureEntity(invEntityId, {
              id: invEntityId,
              entityKind: 'invocation',
              transport: 'webtransport',
              label: ev.metadata?.rpc_method ? `Framed ${ev.metadata.rpc_method}` : 'Framed invocation',
              shortId: truncateId(ev.invocation_id),
              fullId: ev.invocation_id,
              idField: 'invocation_id',
              parentId: streamEntityId,
              outcome: ev.outcome ?? 'unknown',
              role: 'invocation',
              typedIds: {
                connection_id: ev.connection_id,
                transport_session_id: ev.transport_session_id,
                correlation_id: ev.correlation_id,
                stream_id: ev.stream_id,
                stream_correlation_id: ev.stream_correlation_id,
                invocation_id: ev.invocation_id,
                rpc_id: ev.rpc_id,
              },
            });
            attachEvent(invEntity, ev);
          }
        }
      }
    } else if (ev.transport === 'database') {
      const engKey = ev.engine_session_id || 'eng_unscoped';
      const engEntityId = `engine_session:${engKey}`;
      const engEntity = ensureEntity(engEntityId, {
        id: engEntityId,
        entityKind: 'engine_session',
        transport: 'database',
        label: 'Engine session',
        shortId: truncateId(engKey),
        fullId: engKey,
        idField: 'engine_session_id',
        parentId: protoId,
        outcome: 'ok',
        role: 'invocation',
        typedIds: { engine_session_id: ev.engine_session_id },
      });
      attachEvent(engEntity, ev);

      if (ev.scopedTransactionKey && ev.transaction_id) {
        const txEntityId = `transaction:${ev.scopedTransactionKey}`;
        const txEntity = ensureEntity(txEntityId, {
          id: txEntityId,
          entityKind: 'transaction',
          transport: 'database',
          label: 'DB transaction',
          shortId: truncateId(ev.transaction_id),
          fullId: ev.scopedTransactionKey,
          idField: 'transaction_id',
          parentId: engEntityId,
          outcome: ev.outcome ?? 'open',
          role: 'invocation',
          typedIds: {
            engine_session_id: ev.engine_session_id,
            transaction_id: ev.transaction_id,
            correlation_id: ev.correlation_id,
          },
        });
        attachEvent(txEntity, ev);

        txEntity.txLifecycle = txEntity.txLifecycle ?? {
          engine_session_id: engKey,
          transaction_id: ev.transaction_id,
          terminalOutcome: 'open',
          participantInvocationIds: [],
        };
        if (ev.kind === 'db.tx.begin') {
          txEntity.txLifecycle.beginSequence = ev.sequence;
        }
        if (ev.kind === 'db.tx.commit' || ev.kind === 'db.tx.rollback') {
          txEntity.txLifecycle.terminalSequence = ev.sequence;
          txEntity.txLifecycle.terminalOutcome = ev.outcome ?? 'unknown';
          if (ev.duration_ms !== undefined) txEntity.txLifecycle.durationMs = ev.duration_ms;
        }
        if (
          ev.invocation_id &&
          !txEntity.txLifecycle.participantInvocationIds.includes(ev.invocation_id)
        ) {
          txEntity.txLifecycle.participantInvocationIds.push(ev.invocation_id);
        }
      }
    }
  }

  // Wire bidirectional links: Invocation <-> DB Transaction (many-to-many)
  for (const [invId, txIds] of invocationToTxIds.entries()) {
    const invEntity = entities.get(invId);
    for (const txId of txIds) {
      const txEntity = entities.get(txId);
      if (invEntity && txEntity) {
        addLink(invEntity, {
          targetType: 'transaction',
          targetId: txId,
          label: `TX ${txEntity.shortId}`,
          relationship: 'database_transaction',
          evidenceSequences: txEntity.eventSequences.slice(0, 2),
        });
        addLink(txEntity, {
          targetType: 'invocation',
          targetId: invId,
          label: `${invEntity.label} (${invEntity.shortId})`,
          relationship: 'participating_invocation',
          evidenceSequences: invEntity.eventSequences.slice(0, 2),
        });
      }
    }
  }

  // Wire scenario-level shared note links (e.g. REST write -> HTTP JSON-RPC read)
  for (const [noteId, invSet] of noteToInvocationIds.entries()) {
    const invArr = Array.from(invSet);
    if (invArr.length < 2) continue;
    for (const a of invArr) {
      const entA = entities.get(`invocation:${a}`);
      if (!entA) continue;
      for (const b of invArr) {
        if (a === b) continue;
        const entB = entities.get(`invocation:${b}`);
        if (!entB || entA.transport === entB.transport) continue;
        addLink(entA, {
          targetType: 'invocation',
          targetId: entB.id,
          label: `${PROTOCOL_LABELS[entB.transport]} ${entB.shortId}`,
          relationship: `shared_note (${noteId})`,
          evidenceSequences: entB.eventSequences.slice(0, 1),
        });
      }
    }
  }

  // Detect still-open / partial entities (missing terminal close/commit/complete)
  for (const entity of entities.values()) {
    if (entity.entityKind === 'transaction' && entity.txLifecycle) {
      entity.isOpen = entity.txLifecycle.terminalSequence === undefined;
      if (entity.isOpen) {
        entity.outcome = 'open';
        entity.role = 'partial';
      } else if (entity.txLifecycle.terminalOutcome === 'committed') {
        entity.outcome = 'committed';
        entity.role = 'success';
      } else if (entity.txLifecycle.terminalOutcome === 'rolled_back') {
        entity.outcome = 'rolled_back';
        entity.role = 'rejected';
      }
    } else if (entity.entityKind === 'stream' || entity.entityKind === 'transport_session') {
      const evs = entity.eventSequences
        .map((s) => eventBySequence.get(s))
        .filter((e): e is NormalizedEvent => Boolean(e));
      const hasClose = evs.some(
        (e) =>
          e.kind.endsWith('.closed') ||
          e.kind.endsWith('.rejected') ||
          e.outcome === 'rejected'
      );
      const hasOpen = evs.some((e) => e.kind.endsWith('.opened'));
      if (hasOpen && !hasClose) {
        entity.isOpen = true;
      }
    }
  }

  // Ensure deterministic protocol ordering: REST, HTTP JSON-RPC, WebSocket, WebTransport, Database
  const order: TransportProtocol[] = ['rest', 'http_jsonrpc', 'websocket', 'webtransport', 'database'];
  rootIds.sort((a, b) => {
    const pA = a.replace('protocol:', '') as TransportProtocol;
    const pB = b.replace('protocol:', '') as TransportProtocol;
    return order.indexOf(pA) - order.indexOf(pB);
  });

  if (!Number.isFinite(minMs)) {
    minMs = 0;
    maxMs = 1000;
  } else if (minMs === maxMs) {
    maxMs = minMs + 100;
  }

  return {
    entities,
    rootIds,
    eventToEntityIds,
    eventById,
    eventBySequence,
    invocationToTxIds,
    txToInvocationIds,
    noteToInvocationIds,
    minMs,
    maxMs,
  };
}

export function eventMatchesSearch(ev: NormalizedEvent, rawQuery: string): boolean {
  const correlation = /^(?:corr|correlation_id):\s*(.*)$/i.exec(rawQuery.trim());
  if (correlation) {
    const id = correlation[1];
    return Boolean(id) && (ev.correlation_id === id || ev.origin_correlation_id === id);
  }
  const q = rawQuery.trim().toLowerCase();
  if (!q) return true;
  if (String(ev.sequence) === q) return true;
  if (ev.kind.toLowerCase().includes(q)) return true;
  if (ev.displayLabel.toLowerCase().includes(q)) return true;
  if (ev.note_id && ev.note_id.toLowerCase().includes(q)) return true;
  if (ev.origin_correlation_id?.toLowerCase().includes(q)) return true;

  for (const { key } of TYPED_ID_KEYS) {
    const val = ev[key];
    if (val && val.toLowerCase().includes(q)) return true;
  }
  return false;
}

export function filterEvents(
  events: NormalizedEvent[],
  filters: FilterState,
  graph: EntityGraph
): NormalizedEvent[] {
  const hasProtocolFilter = filters.protocols.length > 0;
  const protoSet = new Set<string>(filters.protocols);
  const cohortSet = filters.cohortEventIds ? new Set(filters.cohortEventIds) : null;

  // If protocol filters are active and includeDatabase is true, also include DB events linked to matching invocations
  const matchingInvocations = new Set<string>();
  if (hasProtocolFilter && filters.includeDatabase) {
    for (const ev of events) {
      if (ev.transport !== 'database' && protoSet.has(ev.transport) && ev.invocation_id) {
        matchingInvocations.add(ev.invocation_id);
      }
    }
  }

  return events.filter((ev) => {
    if (filters.fromMs !== null && ev.atMs < filters.fromMs) return false;
    if (filters.toMs !== null && ev.atMs > filters.toMs) return false;

    if (hasProtocolFilter) {
      if (ev.transport === 'database') {
        if (!filters.includeDatabase) return false;
        if (ev.invocation_id && !matchingInvocations.has(ev.invocation_id)) {
          // Check via txToInvocationIds
          if (ev.scopedTransactionKey) {
            const linked = graph.txToInvocationIds.get(`transaction:${ev.scopedTransactionKey}`);
            const anyMatch = linked
              ? Array.from(linked).some((id) =>
                  matchingInvocations.has(id.replace('invocation:', ''))
                )
              : false;
            if (!anyMatch) return false;
          } else {
            return false;
          }
        }
      } else if (!protoSet.has(ev.transport)) {
        return false;
      }
    }

    if (filters.kind && filters.kind !== 'all' && ev.kind !== filters.kind) return false;
    if (filters.outcome && filters.outcome !== 'all' && (ev.outcome ?? 'unknown') !== filters.outcome) {
      return false;
    }
    if (filters.source && filters.source !== 'all' && ev.source !== filters.source) return false;

    if (filters.searchQuery && !eventMatchesSearch(ev, filters.searchQuery)) return false;

    if (cohortSet && !cohortSet.has(ev.id)) return false;

    if (filters.bucketFilter) {
      if (ev.atMs < filters.bucketFilter.startMs || ev.atMs > filters.bucketFilter.endMs) {
        return false;
      }
      const rowEntityIds = graph.eventToEntityIds.get(ev.id) ?? [];
      if (!rowEntityIds.includes(filters.bucketFilter.rowId)) return false;
    }

    return true;
  });
}

export function buildKaryogramRows(
  graph: EntityGraph,
  filteredEvents: NormalizedEvent[],
  expandedIds: Set<string>
): KaryogramRow[] {
  const filteredSet = new Set(filteredEvents.map((e) => e.sequence));
  const rows: KaryogramRow[] = [];

  const collectEntityEvents = (entity: TypedEntity): NormalizedEvent[] =>
    entity.eventSequences
      .filter((s) => filteredSet.has(s))
      .map((s) => graph.eventBySequence.get(s))
      .filter((e): e is NormalizedEvent => Boolean(e));

  const formatLaneTotal = (entity: TypedEntity, evs: NormalizedEvent[]): string => {
    if (entity.entityKind === 'connection' && entity.transport === 'webtransport') {
      const sessCount = entity.childrenIds.length;
      return `${sessCount} ${sessCount === 1 ? 'session' : 'sessions'}`;
    }
    if (entity.entityKind === 'transport_session' && entity.transport === 'webtransport') {
      const streamCount = entity.childrenIds.filter((c) => c.startsWith('stream:')).length;
      return `${streamCount} ${streamCount === 1 ? 'stream' : 'streams'}`;
    }
    if (entity.entityKind === 'datagrams') {
      return `${evs.length} ${evs.length === 1 ? 'datagram' : 'datagrams'}`;
    }
    if (entity.entityKind === 'transaction' && entity.txLifecycle) {
      return formatOutcomeLabel(entity.txLifecycle.terminalOutcome);
    }
    return `${evs.length} ${evs.length === 1 ? 'event' : 'events'}`;
  };

  const visit = (entityId: string, depth: number) => {
    const entity = graph.entities.get(entityId);
    if (!entity) return;

    const visibleEvents = collectEntityEvents(entity);
    // Keep entity visible if it or any child has visible events
    const visibleChildren = entity.childrenIds.filter((cid) => {
      const child = graph.entities.get(cid);
      return child ? child.eventSequences.some((s) => filteredSet.has(s)) : false;
    });

    if (visibleEvents.length === 0 && visibleChildren.length === 0) return;

    const isExpanded = expandedIds.has(entityId);
    const measuredValues = visibleEvents
      .map((e) => e.observation?.value ?? e.duration_ms)
      .filter((v): v is number => typeof v === 'number' && Number.isFinite(v));
    const medianMs =
      measuredValues.length > 0 ? computeNearestRankPercentile(measuredValues, 50) : null;

    let startMs: number | null = null;
    let endMs: number | null = null;
    for (const ev of visibleEvents) {
      if (startMs === null || ev.atMs < startMs) startMs = ev.atMs;
      if (endMs === null || ev.atMs > endMs) endMs = ev.atMs;
    }

    rows.push({
      rowId: entity.id,
      entityId: entity.id,
      entityKind: entity.entityKind,
      transport: entity.transport,
      depth,
      label: entity.label,
      shortId: entity.shortId,
      hasChildren: visibleChildren.length > 0,
      isExpanded,
      events: visibleEvents,
      startMs,
      endMs,
      isOpen: entity.isOpen,
      role: entity.role,
      countLabel: formatLaneTotal(entity, visibleEvents),
      measuredLatencyMedianMs: medianMs,
      isGroupBoundary: depth === 0,
    });

    if (isExpanded) {
      for (const cid of visibleChildren) {
        visit(cid, depth + 1);
      }
    }
  };

  for (const rootId of graph.rootIds) {
    visit(rootId, 0);
  }

  return rows;
}

export function computeRelationshipArcs(
  selection: SelectionState | null,
  graph: EntityGraph,
  rows: KaryogramRow[]
): RelationshipArc[] {
  if (!selection) return [];

  const rowMap = new Map<string, KaryogramRow>();
  for (const r of rows) rowMap.set(r.entityId, r);

  // Resolve visible row for an entity (walking up parent chain if collapsed)
  const findVisibleRow = (entityId: string): KaryogramRow | null => {
    let cur: string | null = entityId;
    while (cur) {
      const r = rowMap.get(cur);
      if (r) return r;
      cur = graph.entities.get(cur)?.parentId ?? null;
    }
    return null;
  };

  const arcs: RelationshipArc[] = [];
  let sourceEntity: TypedEntity | undefined;
  let sourceMs: number | null = null;

  if (selection.type === 'entity') {
    sourceEntity = graph.entities.get(selection.id);
    sourceMs = sourceEntity?.startMs ?? null;
  } else {
    const ev = graph.eventById.get(selection.id);
    if (ev) {
      sourceMs = ev.atMs;
      const eids = graph.eventToEntityIds.get(ev.id) ?? [];
      // Prefer most specific entity
      for (let i = eids.length - 1; i >= 0; i--) {
        const candidate = graph.entities.get(eids[i]);
        if (candidate && candidate.links.length > 0) {
          sourceEntity = candidate;
          break;
        }
      }
      if (!sourceEntity && eids.length > 0) {
        sourceEntity = graph.entities.get(eids[eids.length - 1]);
      }

      // Direct event-level delivery -> origin invocation arc
      if (ev.origin_invocation_id) {
        const fromRow = findVisibleRow(`invocation:${ev.origin_invocation_id}`);
        const toRow =
          (ev.subscription_id && findVisibleRow(`subscription:${ev.subscription_id}`)) ||
          (ev.transport_session_id &&
            findVisibleRow(`transport_session:${ev.transport_session_id}`));
        const originEntity = graph.entities.get(`invocation:${ev.origin_invocation_id}`);
        if (fromRow && toRow && originEntity?.startMs != null) {
          arcs.push({
            id: `arc-deliv-${ev.id}`,
            fromRowId: fromRow.rowId,
            fromMs: originEntity.startMs,
            toRowId: toRow.rowId,
            toMs: ev.atMs,
            label: ev.delivery_id ? `Delivery ${truncateId(ev.delivery_id, 12)}` : 'Delivery',
            role: ev.role,
            dashed: false,
          });
        }
      }
    }
  }

  if (sourceEntity && sourceMs !== null) {
    const fromRow = findVisibleRow(sourceEntity.id);
    if (fromRow) {
      for (const link of sourceEntity.links.slice(0, 6)) {
        const targetEntity = graph.entities.get(link.targetId);
        const toRow = findVisibleRow(link.targetId);
        if (!toRow || toRow.rowId === fromRow.rowId) continue;
        const toMs = targetEntity?.startMs ?? toRow.startMs ?? sourceMs;
        arcs.push({
          id: `arc-${sourceEntity.id}-${link.targetId}-${link.relationship}`,
          fromRowId: fromRow.rowId,
          fromMs: sourceMs,
          toRowId: toRow.rowId,
          toMs,
          label: link.relationship,
          role: link.relationship.includes('transaction') ? 'invocation' : 'carrier',
          dashed: Boolean(link.unretained),
        });
      }
    }
  }

  return arcs;
}

export interface WorkspaceMetrics {
  connections: number;
  transportSessions: number;
  invocations: number;
  transactions: number;
  transactionsCommitted: number;
  transactionsRolledBack: number;
  transactionsOpen: number;
  deliveries: number;
  publications: number;
  sparklines: {
    connections: number[];
    sessions: number[];
    invocations: number[];
    transactions: number[];
    deliveries: number[];
  };
  protocolSummary: Record<
    PrimaryProtocol,
    {
      events: number;
      connections: number;
      sessions: number;
      invocations: number;
      errors: number;
      highlight: string;
    }
  >;
}

export function computeWorkspaceMetrics(filteredEvents: NormalizedEvent[]): WorkspaceMetrics {
  const connections = new Set<string>();
  const sessions = new Set<string>();
  const invocations = new Set<string>();
  const publications = new Set<string>();
  const deliveries = new Set<string>();
  const txOutcomes = new Map<string, EventOutcome>();

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
  const pEvents: Record<PrimaryProtocol, number> = {
    rest: 0,
    http_jsonrpc: 0,
    websocket: 0,
    webtransport: 0,
  };
  const pErrors: Record<PrimaryProtocol, number> = {
    rest: 0,
    http_jsonrpc: 0,
    websocket: 0,
    webtransport: 0,
  };

  let wtRebinds = 0;
  let wtDatagrams = 0;
  let wsSubs = new Set<string>();

  for (const ev of filteredEvents) {
    if (ev.connection_id) connections.add(ev.connection_id);
    if (ev.transport_session_id) sessions.add(ev.transport_session_id);
    if (ev.invocation_id) invocations.add(ev.invocation_id);
    if (ev.publication_id) publications.add(ev.publication_id);
    if (ev.delivery_id) deliveries.add(ev.delivery_id);
    if (ev.subscription_id) wsSubs.add(ev.subscription_id);

    if (ev.scopedTransactionKey) {
      const prev = txOutcomes.get(ev.scopedTransactionKey);
      if (ev.kind === 'db.tx.commit') {
        txOutcomes.set(ev.scopedTransactionKey, 'committed');
      } else if (ev.kind === 'db.tx.rollback') {
        txOutcomes.set(ev.scopedTransactionKey, 'rolled_back');
      } else if (!prev) {
        txOutcomes.set(ev.scopedTransactionKey, 'open');
      }
    }

    if (ev.transport !== 'database') {
      const p = ev.transport;
      pEvents[p] += 1;
      if (ev.connection_id) pConns[p].add(ev.connection_id);
      if (ev.transport_session_id) pSess[p].add(ev.transport_session_id);
      if (ev.invocation_id) pInv[p].add(ev.invocation_id);
      if (ev.outcome === 'rejected' || ev.outcome === 'failed' || ev.outcome === 'rolled_back') {
        pErrors[p] += 1;
      }
      if (ev.kind === 'wt.connection.rebind') wtRebinds += 1;
      if (ev.kind.startsWith('wt.datagram')) wtDatagrams += 1;
    }
  }

  let transactionsCommitted = 0;
  let transactionsRolledBack = 0;
  let transactionsOpen = 0;
  for (const outcome of txOutcomes.values()) {
    if (outcome === 'committed') transactionsCommitted += 1;
    else if (outcome === 'rolled_back') transactionsRolledBack += 1;
    else transactionsOpen += 1;
  }

  // 12-bucket sparklines across filtered window
  const bins = 12;
  const spark = {
    connections: new Array<number>(bins).fill(0),
    sessions: new Array<number>(bins).fill(0),
    invocations: new Array<number>(bins).fill(0),
    transactions: new Array<number>(bins).fill(0),
    deliveries: new Array<number>(bins).fill(0),
  };

  if (filteredEvents.length > 0) {
    const minT = filteredEvents[0].atMs;
    const maxT = filteredEvents[filteredEvents.length - 1].atMs;
    const span = Math.max(1, maxT - minT);
    for (const ev of filteredEvents) {
      const idx = Math.min(bins - 1, Math.floor(((ev.atMs - minT) / span) * bins));
      if (ev.connection_id) spark.connections[idx] += 1;
      if (ev.transport_session_id) spark.sessions[idx] += 1;
      if (ev.invocation_id) spark.invocations[idx] += 1;
      if (ev.scopedTransactionKey) spark.transactions[idx] += 1;
      if (ev.delivery_id) spark.deliveries[idx] += 1;
    }
  }

  return {
    connections: connections.size,
    transportSessions: sessions.size,
    invocations: invocations.size,
    transactions: txOutcomes.size,
    transactionsCommitted,
    transactionsRolledBack,
    transactionsOpen,
    deliveries: deliveries.size,
    publications: publications.size,
    sparklines: spark,
    protocolSummary: {
      rest: {
        events: pEvents.rest,
        connections: pConns.rest.size,
        sessions: pSess.rest.size,
        invocations: pInv.rest.size,
        errors: pErrors.rest,
        highlight:
          pEvents.rest === 0
            ? 'No observations yet'
            : `${pInv.rest.size} ${pInv.rest.size === 1 ? 'op' : 'ops'} · ${pConns.rest.size} conn`,
      },
      http_jsonrpc: {
        events: pEvents.http_jsonrpc,
        connections: pConns.http_jsonrpc.size,
        sessions: pSess.http_jsonrpc.size,
        invocations: pInv.http_jsonrpc.size,
        errors: pErrors.http_jsonrpc,
        highlight:
          pEvents.http_jsonrpc === 0
            ? 'No observations yet'
            : `${pInv.http_jsonrpc.size} RPC ${pInv.http_jsonrpc.size === 1 ? 'item' : 'items'}`,
      },
      websocket: {
        events: pEvents.websocket,
        connections: pConns.websocket.size,
        sessions: pSess.websocket.size,
        invocations: pInv.websocket.size,
        errors: pErrors.websocket,
        highlight:
          pEvents.websocket === 0
            ? 'No observations yet'
            : `${pSess.websocket.size} sockets · ${wsSubs.size} sub · ${deliveries.size} deliv`,
      },
      webtransport: {
        events: pEvents.webtransport,
        connections: pConns.webtransport.size,
        sessions: pSess.webtransport.size,
        invocations: pInv.webtransport.size,
        errors: pErrors.webtransport,
        highlight:
          pEvents.webtransport === 0
            ? 'No observations yet'
            : `${pConns.webtransport.size} QUIC · ${pSess.webtransport.size} sess · ${wtDatagrams} dg${wtRebinds > 0 ? ' · rebind' : ''}`,
      },
    },
  };
}

// Nearest-rank percentile convention (shared across all lanes)
export function computeNearestRankPercentile(values: number[], percentile: number): number | null {
  if (values.length === 0) return null;
  const sorted = [...values].sort((a, b) => a - b);
  const rank = Math.ceil((percentile / 100) * sorted.length);
  const idx = Math.min(sorted.length - 1, Math.max(0, rank - 1));
  return sorted[idx];
}

// Exact proposed display thresholds: p50 n>=1, p90 n>=10, p95 n>=20, p99 n>=100
export function computeQuantileSummary(values: number[]): QuantileSummary {
  const n = values.length;
  if (n === 0) {
    return { n: 0, p50: null, p90: null, p95: null, p99: null, max: null, limitedSample: true };
  }
  const sorted = [...values].sort((a, b) => a - b);
  const pick = (p: number) => sorted[Math.min(n - 1, Math.max(0, Math.ceil((p / 100) * n) - 1))];
  return {
    n,
    p50: pick(50),
    p90: n >= 10 ? pick(90) : null,
    p95: n >= 20 ? pick(95) : null,
    p99: n >= 100 ? pick(99) : null,
    max: sorted[n - 1],
    limitedSample: n < 10,
  };
}

export function computeLatencyDistributions(
  filteredEvents: NormalizedEvent[],
  measure: 'invocation_latency' | 'transaction_latency' | 'delivery_latency',
  binCount = 12
): {
  lanes: DistributionLaneResult[];
  sharedMin: number;
  sharedMax: number;
  unit: string;
} {
  const laneDefs: Array<{ key: string; label: string; protocol: TransportProtocol }> =
    measure === 'invocation_latency'
      ? [
          { key: 'rest', label: 'REST', protocol: 'rest' },
          { key: 'http_jsonrpc', label: 'HTTP JSON-RPC', protocol: 'http_jsonrpc' },
          { key: 'websocket', label: 'WebSocket', protocol: 'websocket' },
          { key: 'webtransport', label: 'WebTransport', protocol: 'webtransport' },
        ]
      : measure === 'transaction_latency'
        ? [{ key: 'database', label: 'Database transactions', protocol: 'database' }]
        : [{ key: 'websocket', label: 'WebSocket broker deliveries', protocol: 'websocket' }];

  const rawByLane = new Map<
    string,
    {
      eligible: Array<{
        eventId: string;
        sequence: number;
        atMs: number;
        value: number;
        label: string;
        outcome: EventOutcome;
        role: EventRole;
      }>;
      excludedReasons: Record<string, number>;
      excludedCount: number;
      timingBoundary: string;
    }
  >();

  let globalMin = Number.POSITIVE_INFINITY;
  let globalMax = Number.NEGATIVE_INFINITY;

  for (const def of laneDefs) {
    const eligible: Array<{
      eventId: string;
      sequence: number;
      atMs: number;
      value: number;
      label: string;
      outcome: EventOutcome;
      role: EventRole;
    }> = [];
    const excludedReasons: Record<string, number> = {};
    let excludedCount = 0;
    let timingBoundary =
      measure === 'invocation_latency'
        ? 'invocation.started -> invocation.completed'
        : measure === 'transaction_latency'
          ? 'db.tx.begin -> db.tx.commit/rollback'
          : 'broker.publication.created -> broker.delivery.dispatched';

    for (const ev of filteredEvents) {
      if (ev.transport !== def.protocol) continue;

      const isCandidate =
        measure === 'invocation_latency'
          ? ev.kind === 'invocation.completed' || ev.kind === 'invocation.failed'
          : measure === 'transaction_latency'
            ? ev.kind === 'db.tx.commit' || ev.kind === 'db.tx.rollback' || ev.kind === 'db.tx.begin'
            : ev.kind === 'broker.delivery.dispatched' || ev.kind === 'broker.delivery.rejected';

      if (!isCandidate) continue;

      if (measure === 'transaction_latency' && ev.kind === 'db.tx.begin') {
        continue; // Do not double-count begin when terminal records represent transactions
      }

      const obs = ev.observation;
      if (obs && obs.measure === measure && typeof obs.value === 'number' && Number.isFinite(obs.value)) {
        timingBoundary = obs.timing_boundary;
        eligible.push({
          eventId: ev.id,
          sequence: ev.sequence,
          atMs: ev.atMs,
          value: obs.value,
          label: ev.displayLabel,
          outcome: ev.outcome ?? 'unknown',
          role: ev.role,
        });
        if (obs.value < globalMin) globalMin = obs.value;
        if (obs.value > globalMax) globalMax = obs.value;
      } else {
        excludedCount += 1;
        const reason =
          ev.outcome === 'rejected'
            ? 'Rejected before terminal measurement'
            : 'Sink timestamp only (no producer duration)';
        excludedReasons[reason] = (excludedReasons[reason] ?? 0) + 1;
      }
    }

    rawByLane.set(def.key, { eligible, excludedReasons, excludedCount, timingBoundary });
  }

  if (!Number.isFinite(globalMin)) {
    globalMin = 0;
    globalMax = 20;
  } else {
    globalMin = Math.max(0, Math.floor(globalMin));
    globalMax = Math.ceil(globalMax * 1.05);
    if (globalMax <= globalMin) globalMax = globalMin + 5;
  }

  const binWidth = (globalMax - globalMin) / binCount;

  const lanes: DistributionLaneResult[] = laneDefs.map((def) => {
    const data = rawByLane.get(def.key)!;
    const n = data.eligible.length;
    const bins: DistributionBin[] = [];

    for (let i = 0; i < binCount; i++) {
      const low = Number((globalMin + i * binWidth).toFixed(2));
      const high = Number((globalMin + (i + 1) * binWidth).toFixed(2));
      bins.push({
        index: i,
        low,
        high,
        inclusiveUpper: i === binCount - 1,
        count: 0,
        probability: 0,
        cumulativeProbability: 0,
        eventIds: [],
      });
    }

    for (const obs of data.eligible) {
      let idx = Math.floor((obs.value - globalMin) / binWidth);
      if (idx < 0) idx = 0;
      if (idx >= binCount) idx = binCount - 1;
      bins[idx].count += 1;
      bins[idx].eventIds.push(obs.eventId);
    }

    let running = 0;
    for (const b of bins) {
      running += b.count;
      b.probability = n > 0 ? b.count / n : 0;
      b.cumulativeProbability = n > 0 ? running / n : 0;
    }

    return {
      key: def.key,
      label: def.label,
      protocol: def.protocol,
      unit: 'ms',
      timingBoundary: data.timingBoundary,
      scope: `${def.label} · ${measure.replace('_', ' ')}`,
      eligibleCount: n,
      excludedCount: data.excludedCount,
      excludedReasons: data.excludedReasons,
      bins,
      quantiles: computeQuantileSummary(data.eligible.map((o) => o.value)),
      observations: data.eligible,
    };
  });

  return {
    lanes,
    sharedMin: globalMin,
    sharedMax: globalMax,
    unit: 'ms',
  };
}

export interface OutcomeBreakdownRow {
  protocol: TransportProtocol;
  label: string;
  total: number;
  knownDenominator: number;
  counts: Record<'ok' | 'committed' | 'delivered' | 'rejected' | 'failed' | 'rolled_back' | 'open' | 'unknown', number>;
}

export function computeOutcomeBreakdown(filteredEvents: NormalizedEvent[]): OutcomeBreakdownRow[] {
  const protos: TransportProtocol[] = ['rest', 'http_jsonrpc', 'websocket', 'webtransport', 'database'];
  return protos.map((protocol) => {
    const counts = {
      ok: 0,
      committed: 0,
      delivered: 0,
      rejected: 0,
      failed: 0,
      rolled_back: 0,
      open: 0,
      unknown: 0,
    };
    let total = 0;
    for (const ev of filteredEvents) {
      if (ev.transport !== protocol) continue;
      total += 1;
      const o = ev.outcome ?? 'unknown';
      if (o === 'partial') counts.open += 1;
      else if (o in counts) counts[o as keyof typeof counts] += 1;
      else counts.unknown += 1;
    }
    const knownDenominator = total - counts.unknown;
    return {
      protocol,
      label: PROTOCOL_LABELS[protocol],
      total,
      knownDenominator,
      counts,
    };
  });
}

export interface WtLaneMixSummary {
  sessionId: string;
  correlationId?: string;
  correlationSequence?: number;
  streamOpenedBidi: number;
  streamOpenedUni: number;
  streamRejected: number;
  datagramsInbound: number;
  datagramsOutbound: number;
  distinctDatagramIds: number;
  rebinds: number;
}

export function computeWtLaneMix(filteredEvents: NormalizedEvent[]): WtLaneMixSummary[] {
  const map = new Map<string, WtLaneMixSummary & { dgSet: Set<string> }>();
  for (const ev of filteredEvents) {
    if (ev.transport !== 'webtransport' || !ev.transport_session_id) continue;
    const sid = ev.transport_session_id;
    let row = map.get(sid);
    if (!row) {
      row = {
        sessionId: sid,
        correlationId: ev.correlation_id,
        correlationSequence: ev.correlation_id ? ev.sequence : undefined,
        streamOpenedBidi: 0,
        streamOpenedUni: 0,
        streamRejected: 0,
        datagramsInbound: 0,
        datagramsOutbound: 0,
        distinctDatagramIds: 0,
        rebinds: 0,
        dgSet: new Set(),
      };
      map.set(sid, row);
    }
    if (ev.kind === 'wt.stream.opened') {
      if (ev.direction === 'unidirectional') row.streamOpenedUni += 1;
      else row.streamOpenedBidi += 1;
    }
    if (ev.kind === 'wt.stream.rejected') row.streamRejected += 1;
    if (ev.kind === 'wt.datagram.received') row.datagramsInbound += 1;
    if (ev.kind === 'wt.datagram.sent') row.datagramsOutbound += 1;
    if (ev.datagram_id) row.dgSet.add(ev.datagram_id);
    if (ev.kind === 'wt.connection.rebind') row.rebinds += 1;
  }

  return Array.from(map.values()).map(({ dgSet, ...rest }) => ({
    ...rest,
    distinctDatagramIds: dgSet.size,
  }));
}
