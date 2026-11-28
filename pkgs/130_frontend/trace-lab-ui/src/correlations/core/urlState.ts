import type { DatasetMode, SearchIdType, TransportProtocol } from './types';

export type AppRoute =
  | { name: 'index' }
  | { name: 'compare' }
  | { name: 'detail'; groupKey: string };

export interface UrlQueryState {
  mode: DatasetMode;
  fixture?: string;
  select?: string;
  selectType?: 'mark' | 'edge';
  winStart?: number;
  winEnd?: number;
  proto?: TransportProtocol | 'all';
  view?: 'waterfall' | 'events';
  linked?: boolean;
  q?: string;
  idType?: SearchIdType;
  unassigned?: boolean;
  pinned?: string[];
}

export interface NavigationHistorySnapshot {
  url: string;
  scrollY: number;
  scrollX: number;
  selectedId?: string;
  selectedType?: 'mark' | 'edge';
  winStart?: number;
  winEnd?: number;
  view?: 'waterfall' | 'events';
  linked?: boolean;
}

const VALID_PROTOCOLS = new Set<string>(['rest', 'jsonrpc', 'websocket', 'webtransport', 'all']);
const VALID_ID_TYPES = new Set<string>([
  'correlation_id',
  'request_id',
  'rpc_id',
  'stream_correlation_id',
  'quic_connection_id',
  'transport_session_id',
  'transaction_id',
  'invocation_id',
]);

/**
 * Parses routes reserving static `/correlations/compare` BEFORE dynamic `/correlations/:groupKey`.
 */
export function parseRoute(pathname: string): AppRoute {
  const clean = pathname.replace(/\/+$/, '') || '/';
  if (clean === '/' || clean === '/correlations') {
    return { name: 'index' };
  }
  if (clean === '/correlations/compare') {
    return { name: 'compare' };
  }
  if (clean.startsWith('/correlations/')) {
    const rawKey = clean.slice('/correlations/'.length);
    try {
      const decoded = decodeURIComponent(rawKey);
      if (decoded && decoded !== 'compare') {
        return { name: 'detail', groupKey: decoded };
      }
    } catch {
      // fall through to index on malformed encoding
    }
  }
  return { name: 'index' };
}

export function buildRoutePath(route: AppRoute): string {
  if (route.name === 'compare') return '/correlations/compare';
  if (route.name === 'detail') return `/correlations/${encodeURIComponent(route.groupKey)}`;
  return '/correlations';
}

export function parseQueryState(search: string): UrlQueryState {
  const params = new URLSearchParams(search);
  const modeRaw = params.get('mode');
  const mode: DatasetMode = modeRaw === 'recorded' ? 'recorded' : 'live';

  const fixture = params.get('fixture') || undefined;
  const select = params.get('select') || undefined;
  const selectTypeRaw = params.get('selectType');
  const selectType =
    selectTypeRaw === 'edge' ? 'edge' : selectTypeRaw === 'mark' ? 'mark' : undefined;

  const winRaw = params.get('win');
  let winStart: number | undefined;
  let winEnd: number | undefined;
  if (winRaw && winRaw.includes('..')) {
    const [a, b] = winRaw.split('..').map(Number);
    if (Number.isFinite(a) && Number.isFinite(b) && b > a) {
      winStart = a;
      winEnd = b;
    }
  }

  const protoRaw = params.get('proto');
  const proto = (
    protoRaw && VALID_PROTOCOLS.has(protoRaw) ? protoRaw : 'all'
  ) as TransportProtocol | 'all';

  const viewRaw = params.get('view');
  const view: 'waterfall' | 'events' = viewRaw === 'events' ? 'events' : 'waterfall';

  const linked = params.get('linked') === '1';
  const unassigned = params.get('unassigned') === '1';
  const q = params.get('q') || undefined;

  const idTypeRaw = params.get('idType');
  const idType = (
    idTypeRaw && VALID_ID_TYPES.has(idTypeRaw) ? idTypeRaw : 'correlation_id'
  ) as SearchIdType;

  const pinnedRaw = params.get('pinned');
  const pinned = pinnedRaw
    ? pinnedRaw
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean)
        .slice(0, 24)
    : undefined;

  return {
    mode,
    fixture,
    select,
    selectType,
    winStart,
    winEnd,
    proto,
    view,
    linked,
    q,
    idType,
    unassigned,
    pinned,
  };
}

export function serializeUrl(route: AppRoute, query: Partial<UrlQueryState>): string {
  const path = buildRoutePath(route);
  const params = new URLSearchParams();

  if (query.mode && query.mode !== 'live') params.set('mode', query.mode);
  if (query.fixture) params.set('fixture', query.fixture);
  if (query.select) params.set('select', query.select);
  if (query.selectType && query.select) params.set('selectType', query.selectType);
  if (
    typeof query.winStart === 'number' &&
    typeof query.winEnd === 'number' &&
    query.winEnd > query.winStart
  ) {
    params.set('win', `${query.winStart.toFixed(3)}..${query.winEnd.toFixed(3)}`);
  }
  if (query.proto && query.proto !== 'all') params.set('proto', query.proto);
  if (query.view && query.view !== 'waterfall') params.set('view', query.view);
  if (query.linked) params.set('linked', '1');
  if (query.unassigned) params.set('unassigned', '1');
  if (query.q && query.q.trim()) params.set('q', query.q.trim());
  if (query.idType && query.idType !== 'correlation_id') params.set('idType', query.idType);
  if (query.pinned && query.pinned.length > 0) {
    params.set('pinned', query.pinned.slice(0, 24).join(','));
  }

  const qs = params.toString();
  return qs ? `${path}?${qs}` : path;
}
