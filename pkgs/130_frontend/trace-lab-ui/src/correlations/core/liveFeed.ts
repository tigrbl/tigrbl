import type { RawTraceEvent } from '../../types/trace';
import type { RawTraceEventInput, SearchIdType, TraceSnapshotInput, TransportProtocol } from './types';

export const LIVE_CAPTURE_ID = 'collector';

interface CollectorFeed {
  events: RawTraceEvent[];
  bounded: boolean;
}

const nativeProtocols: Record<string, TransportProtocol> = {
  REST: 'rest',
  'JSON-RPC': 'jsonrpc',
  WebSocket: 'websocket',
  WebTransport: 'webtransport',
};
const displayedProtocols: Record<string, TransportProtocol> = {
  rest: 'rest',
  http_jsonrpc: 'jsonrpc',
  websocket: 'websocket',
  webtransport: 'webtransport',
};
const eventNames: Record<string, string> = {
  'broker.publication.created': 'ws.broker.publish',
  'broker.delivery.dispatched': 'ws.broker.delivery',
  'broker.delivery.rejected': 'ws.broker.delivery',
  'broker.subscription.acknowledged': 'ws.subscription.attached',
  'wt.stream.received': 'wt.stream.frame.received',
  'wt.stream.sent': 'wt.stream.frame.sent',
};
const searchFields: Record<string, SearchIdType> = {
  corr: 'correlation_id', correlation_id: 'correlation_id',
  req: 'request_id', request: 'request_id', request_id: 'request_id',
  rpc: 'rpc_id', rpc_id: 'rpc_id',
  stream: 'stream_correlation_id', stream_correlation_id: 'stream_correlation_id',
  quic: 'quic_connection_id', conn: 'quic_connection_id', quic_connection_id: 'quic_connection_id',
  sess: 'transport_session_id', session: 'transport_session_id', transport_session_id: 'transport_session_id',
  tx: 'transaction_id', transaction: 'transaction_id', transaction_id: 'transaction_id',
  inv: 'invocation_id', invocation: 'invocation_id', invocation_id: 'invocation_id',
};

export interface TraceLookup { value: string; field: SearchIdType }

export function parseTraceLookup(query: string, field: SearchIdType): TraceLookup | undefined {
  const value = query.trim();
  if (!value) return;
  const match = /^([a-z_]+):(.+)$/i.exec(value);
  const matchedField = match && searchFields[match[1].toLowerCase()];
  return matchedField ? { value: match[2].trim(), field: matchedField } : { value, field };
}

export function groupLookup(groupKey: string): TraceLookup | undefined {
  const encodedId = groupKey.split('|')[2];
  if (!encodedId) return;
  try {
    return { value: decodeURIComponent(encodedId), field: 'correlation_id' };
  } catch {
    return;
  }
}

function toEvent(event: RawTraceEvent): RawTraceEventInput {
  const meta = event.metadata ?? {};
  const native = typeof meta.native_transport === 'string' ? meta.native_transport : '';
  const protocol = nativeProtocols[native] ?? displayedProtocols[event.transport] ?? 'unknown';
  const { http_status, sequence, outcome, direction, ...fields } = event;
  return {
    ...fields,
    seq: sequence,
    protocol,
    kind: eventNames[event.kind] ?? event.kind,
    receiving_correlation_id: event.kind.startsWith('broker.delivery.') ? event.correlation_id : undefined,
    quic_connection_id: protocol === 'webtransport' ? event.connection_id : undefined,
    status_code: http_status,
    service: typeof meta.service === 'string' ? meta.service : undefined,
    environment: typeof meta.environment === 'string' ? meta.environment : undefined,
    observer: event.source,
    direction: direction === 'inbound' || direction === 'outbound' ? direction : undefined,
    outcome: ['failed', 'rejected', 'rolled_back'].includes(outcome ?? '') ? 'error'
      : ['ok', 'committed', 'delivered'].includes(outcome ?? '') ? 'ok'
        : outcome === 'partial' ? 'incomplete' : 'unknown',
  };
}

async function readFeed(lookup: TraceLookup | undefined, signal: AbortSignal): Promise<CollectorFeed> {
  const query = new URLSearchParams();
  if (lookup) {
    query.set('id', lookup.value);
    query.set('id_type', lookup.field === 'quic_connection_id' ? 'connection_id' : lookup.field);
  }
  const response = await fetch(`/api/correlations?${query}`, {
    cache: 'no-store',
    headers: { Accept: 'application/json' },
    signal,
  });
  if (!response.ok) throw new Error(`Trace feed returned HTTP ${response.status}`);
  return response.json();
}

export async function loadLiveSnapshot(
  lookups: TraceLookup[],
  fallbackToRecent: boolean,
  signal: AbortSignal,
  expandRelated = false,
  includeRecent = false,
): Promise<TraceSnapshotInput> {
  const feeds = lookups.length
    ? await Promise.all(lookups.map((lookup) => readFeed(lookup, signal)))
    : [await readFeed(undefined, signal)];
  if (includeRecent || (fallbackToRecent && lookups.length === 1 && !feeds[0].events.length)) {
    feeds.push(await readFeed(undefined, signal));
  }
  if (expandRelated && lookups.length === 1) {
    const queries = new Map<string, TraceLookup>();
    for (const event of feeds[0].events) {
      const origin = event.origin_correlation_id;
      const tx = event.engine_session_id && event.transaction_id
        ? `${event.engine_session_id}::${event.transaction_id}` : undefined;
      if (origin && origin !== lookups[0].value) {
        queries.set(`correlation:${origin}`, { value: origin, field: 'correlation_id' });
      }
      if (tx) queries.set(`transaction:${tx}`, { value: tx, field: 'transaction_id' });
      if (event.transport === 'webtransport' && event.connection_id) {
        queries.set(`connection:${event.connection_id}`, { value: event.connection_id, field: 'quic_connection_id' });
      }
    }
    const related = [...queries.values()].slice(0, 8);
    feeds.push(...await Promise.all(related.map((lookup) => readFeed(lookup, signal))));
  }
  const bySequence = new Map<number, RawTraceEvent>();
  for (const feed of feeds) {
    for (const event of feed.events) bySequence.set(event.sequence, event);
  }
  const events = [...bySequence.values()].sort((a, b) => a.sequence - b.sequence).map(toEvent);
  return {
    capture_id: LIVE_CAPTURE_ID,
    mode: 'live',
    sequence_floor: events[0]?.seq ?? 0,
    sequence_ceiling: events.at(-1)?.seq ?? 0,
    retained_count: events.length,
    evicted_count: 0,
    generated_at: new Date().toISOString(),
    bounded: feeds.some((feed) => feed.bounded),
    events,
  };
}
