import type { RawTraceEvent, TraceSnapshot } from '../types/trace';

export const COLLECTOR_PAGE_SIZE = 100;

export function timelineSearch(params: URLSearchParams): string {
  const legacyId = params.get('correlation_id');
  return params.get('q') ?? (legacyId ? `corr:${legacyId}` : '');
}

export function correlationLookup(search: string): { id: string; exact: boolean } | null {
  const value = search.trim();
  const prefix = /^(?:corr|correlation_id):/i.exec(value);
  const id = prefix ? value.slice(prefix[0].length).trim() : value;
  return id && id.length <= 256 ? { id, exact: Boolean(prefix) } : null;
}

export function collectorQuery(search: string): URLSearchParams {
  const url = new URLSearchParams(search);
  const query = new URLSearchParams();
  const before = url.get('before');
  if (before) query.set('before', before);
  return query;
}

interface TimelinePage {
  events: RawTraceEvent[];
  next_before: number | null;
}

export function toCollectorSnapshot(page: TimelinePage): TraceSnapshot {
  const { events, next_before } = page;
  const lastSequence = events[0]?.sequence ?? 0;
  return {
    revision: lastSequence,
    capture_id: 'timeline',
    captured_at: new Date().toISOString(),
    retention_limit: COLLECTOR_PAGE_SIZE,
    retained_range: {
      min_sequence: events.at(-1)?.sequence ?? 0,
      max_sequence: lastSequence,
      total_emitted: events.length,
      evicted_count: 0,
    },
    running: false,
    active_run_id: null,
    last_run_summary: null,
    events,
    next_before,
  };
}
