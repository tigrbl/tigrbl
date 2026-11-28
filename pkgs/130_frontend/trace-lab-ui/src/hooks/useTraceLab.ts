import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  COLLECTOR_PAGE_SIZE, collectorQuery, correlationLookup, timelineSearch, toCollectorSnapshot,
} from '../adapter/collectorSnapshot';
import {
  buildEntityGraph,
  buildKaryogramRows,
  computeRelationshipArcs,
  computeWorkspaceMetrics,
  filterEvents,
  normalizeSnapshotEvents,
} from '../adapter/traceAdapter';
import { getRecordedSnapshot } from '../data/recordedSamples';
import { THEMES } from '../theme/tokens';
import { useTraceTheme } from '../theme/TraceTheme';
import type { CaptureStatus } from '../components/CaptureBar';
import {
  DatasetMode,
  ExploreViewMode,
  FilterState,
  PrimaryProtocol,
  RecordedDatasetId,
  RouteId,
  ScenarioRunSummary,
  SelectionState,
  TraceSnapshot,
} from '../types/trace';

function getInitialRoute(): RouteId {
  return window.location.pathname === '/distributions' ? 'distributions' : 'explore';
}

function parseInitialUrlState(): {
  mode: DatasetMode;
  sampleId: RecordedDatasetId;
  view: ExploreViewMode;
  filters: FilterState;
  selection: SelectionState | null;
} {
  const params = new URLSearchParams(window.location.search);
  const modeParam = params.get('mode');
  const mode: DatasetMode = modeParam === 'recorded' ? 'recorded' : 'live';
  const sampleParam = params.get('sample');
  const sampleId: RecordedDatasetId =
    sampleParam === 'recorded-stress-10k' ? 'recorded-stress-10k' : 'recorded-v1.2-synthetic';
  const view: ExploreViewMode = params.get('view') === 'event-table' ? 'event-table' : 'karyogram';

  const transportParam = params.get('transport');
  const allowedProtos: PrimaryProtocol[] = ['rest', 'http_jsonrpc', 'websocket', 'webtransport'];
  const protocols = transportParam
    ? (transportParam
        .split(',')
        .filter((p): p is PrimaryProtocol =>
          allowedProtos.includes(p as PrimaryProtocol)
        ))
    : [];

  const fromNum = params.get('from') ? Number(params.get('from')) : null;
  const toNum = params.get('to') ? Number(params.get('to')) : null;

  const entityParam = params.get('entity');
  let selection: SelectionState | null = null;
  if (entityParam) {
    if (entityParam.startsWith('event:')) {
      selection = { type: 'event', id: entityParam.slice(6) };
    } else {
      selection = { type: 'entity', id: entityParam };
    }
  }

  return {
    mode,
    sampleId,
    view,
    filters: {
      protocols,
      includeDatabase: true,
      kind: params.get('kind') || 'all',
      outcome: params.get('outcome') || 'all',
      source: params.get('source') || 'all',
      searchQuery: timelineSearch(params),
      fromMs: fromNum !== null && Number.isFinite(fromNum) ? fromNum : null,
      toMs: toNum !== null && Number.isFinite(toNum) ? toNum : null,
      cohortEventIds: null,
      cohortLabel: null,
      bucketFilter: null,
    },
    selection,
  };
}

export interface LiveStatusInfo {
  connectionState: 'loading' | 'connected' | 'stale' | 'paused';
  lastGoodAt: string | null;
  error: string | null;
  restartNotice: string | null;
  autoFollow: boolean;
}

export function useTraceLab(
  collector: boolean,
  onRouteChange: () => void,
  pausedAt: number | null,
  onCaptureStatus: (status: CaptureStatus) => void,
) {
  const initial = useMemo(() => parseInitialUrlState(), []);

  const [route, setRoute] = useState<RouteId>(() => getInitialRoute());
  const [mode, setMode] = useState<DatasetMode>(initial.mode);
  const [sampleId, setSampleId] = useState<RecordedDatasetId>(initial.sampleId);
  const [exploreView, setExploreView] = useState<ExploreViewMode>(initial.view);
  const { theme } = useTraceTheme();

  const [filters, setFilters] = useState<FilterState>(initial.filters);
  const [selection, setSelection] = useState<SelectionState | null>(initial.selection);
  const [expandedIds, setExpandedIds] = useState<Set<string>>(
    () =>
      new Set([
        'protocol:rest',
        'protocol:http_jsonrpc',
        'protocol:websocket',
        'protocol:webtransport',
        'protocol:database',
      ])
  );

  // Live snapshot state (strictly separated from UI interaction state)
  const [liveSnapshot, setLiveSnapshot] = useState<TraceSnapshot | null>(null);
  const [pausedSnapshot, setPausedSnapshot] = useState<TraceSnapshot | null>(null);
  const isPaused = mode === 'live' && pausedAt !== null;
  const [replayCursorSeq, setReplayCursorSeq] = useState<number | null>(null);
  const [autoFollow, setAutoFollow] = useState(true);
  const [initialLoading, setInitialLoading] = useState(true);
  const [pollError, setPollError] = useState<string | null>(null);
  const [restartNotice, setRestartNotice] = useState<string | null>(null);
  const [lastGoodAt, setLastGoodAt] = useState<string | null>(null);

  // Run scenario state
  const [isRunningScenario, setIsRunningScenario] = useState(false);
  const [runElapsedMs, setRunElapsedMs] = useState(0);
  const [runNotice, setRunNotice] = useState<{
    tone: 'info' | 'success' | 'warning' | 'error';
    message: string;
  } | null>(null);
  const [liveAnnouncement, setLiveAnnouncement] = useState('');

  // Polling refs: single in-flight request + retry backoff
  const inFlightRef = useRef(false);
  const retryDelayRef = useRef(0);
  const lastCaptureRef = useRef<{ captureId: string; maxSeq: number; revision: number } | null>(
    null
  );
  const timerRef = useRef<number | null>(null);
  const runTimerRef = useRef<number | null>(null);

  // Sync URL query parameters and route (never stores hover or payload data)
  const syncUrl = useCallback(
    (
      nextRoute: RouteId,
      nextMode: DatasetMode,
      nextSample: RecordedDatasetId,
      nextView: ExploreViewMode,
      nextFilters: FilterState,
      nextSelection: SelectionState | null,
      pushHistory = false
    ) => {
      const path = nextRoute === 'distributions' ? '/distributions' : collector ? '/explore' : '/';
      const params = collector ? collectorQuery(window.location.search) : new URLSearchParams();
      if (collector && nextFilters.searchQuery.trim() !== timelineSearch(new URLSearchParams(window.location.search))) {
        params.delete('before');
      }
      params.set('mode', nextMode);
      if (nextMode === 'recorded') params.set('sample', nextSample);
      if (nextView !== 'karyogram') params.set('view', nextView);
      if (nextFilters.protocols.length > 0) {
        params.set('transport', nextFilters.protocols.join(','));
      }
      if (nextFilters.fromMs !== null) params.set('from', String(Math.round(nextFilters.fromMs)));
      if (nextFilters.toMs !== null) params.set('to', String(Math.round(nextFilters.toMs)));
      if (nextFilters.kind !== 'all') params.set('kind', nextFilters.kind);
      if (nextFilters.outcome !== 'all') params.set('outcome', nextFilters.outcome);
      if (nextFilters.source !== 'all') params.set('source', nextFilters.source);
      if (nextFilters.searchQuery.trim()) params.set('q', nextFilters.searchQuery.trim());
      if (nextSelection) {
        params.set(
          'entity',
          nextSelection.type === 'event' ? `event:${nextSelection.id}` : nextSelection.id
        );
      }

      const qs = params.toString();
      const targetUrl = qs ? `${path}?${qs}` : path;
      const currentUrl = `${window.location.pathname}${window.location.search}`;
      if (targetUrl !== currentUrl) {
        if (pushHistory) {
          window.history.pushState({ route: nextRoute }, '', targetUrl);
        } else {
          window.history.replaceState({ route: nextRoute }, '', targetUrl);
        }
        onRouteChange();
      }
    },
    [collector, onRouteChange]
  );

  // Sync on state updates
  useEffect(() => {
    syncUrl(route, mode, sampleId, exploreView, filters, selection, false);
  }, [route, mode, sampleId, exploreView, filters, selection, syncUrl]);

  // Support browser Back/Forward without losing scroll position or filters
  useEffect(() => {
    const onPopState = () => {
      const nextRoute = getInitialRoute();
      const parsed = parseInitialUrlState();
      setRoute(nextRoute);
      setMode(parsed.mode);
      setSampleId(parsed.sampleId);
      setExploreView(parsed.view);
      setFilters((prev) => ({
        ...parsed.filters,
        cohortEventIds: prev.cohortEventIds,
        cohortLabel: prev.cohortLabel,
      }));
      setSelection(parsed.selection);
    };
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, []);

  // Poll the active source with one request in flight and retry backoff.
  const fetchLiveSnapshot = useCallback(async () => {
    if (inFlightRef.current) return;
    inFlightRef.current = true;
    try {
      const query = collectorQuery(window.location.search);
      query.set('limit', String(COLLECTOR_PAGE_SIZE));
      const res = await fetch(collector ? `/api/timeline?${query}` : '/demo/trace', {
        method: 'GET',
        headers: { Accept: 'application/json' },
        cache: 'no-store',
      });
      if (!res.ok) {
        throw new Error(`Snapshot HTTP ${res.status}`);
      }
      const payload = await res.json();
      const data = collector ? toCollectorSnapshot(payload) : (payload as TraceSnapshot);

      // Detect server restart / revision rewind / sequence regression
      const prev = lastCaptureRef.current;
      if (
        prev &&
        (data.capture_id !== prev.captureId ||
          data.revision < prev.revision ||
          data.retained_range.max_sequence < prev.maxSeq)
      ) {
        setRestartNotice(
          'Trace capture restarted on the server. Cursor reset; prior selections may no longer be retained.'
        );
        setLiveAnnouncement('Trace capture restarted. Cursor reset.');
      }

      lastCaptureRef.current = {
        captureId: data.capture_id,
        maxSeq: data.retained_range.max_sequence,
        revision: data.revision,
      };

      setLiveSnapshot(data);
      setLastGoodAt(data.captured_at || new Date().toISOString());
      setPollError(null);
      retryDelayRef.current = 0;

      // Auto-expand QUIC connection and key groups when first live events arrive
      if (data.events.length > 0 && (!prev || prev.maxSeq === 0)) {
        const autoOpen = new Set<string>([
          'protocol:rest',
          'protocol:http_jsonrpc',
          'protocol:websocket',
          'protocol:webtransport',
          'protocol:database',
        ]);
        for (const ev of data.events) {
          if (ev.transport === 'webtransport' && ev.connection_id) {
            autoOpen.add(`connection:${ev.connection_id}`);
          }
          if (ev.transport === 'webtransport' && ev.transport_session_id) {
            autoOpen.add(`transport_session:${ev.transport_session_id}`);
          }
        }
        setExpandedIds((curr) => new Set([...curr, ...autoOpen]));
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Unable to reach trace snapshot endpoint';
      setPollError(msg);
      retryDelayRef.current = Math.min(12000, Math.max(2000, retryDelayRef.current * 2));
    } finally {
      inFlightRef.current = false;
      setInitialLoading(false);
    }
  }, [collector]);

  useEffect(() => {
    if (mode !== 'live') {
      setInitialLoading(false);
      return;
    }

    let cancelled = false;

    const scheduleNext = () => {
      if (cancelled) return;
      if (document.hidden) return;
      const baseDelay =
        retryDelayRef.current > 0
          ? retryDelayRef.current
          : isRunningScenario || liveSnapshot?.running
            ? 1000
            : 3000;
      timerRef.current = window.setTimeout(async () => {
        if (!cancelled && !document.hidden) {
          await fetchLiveSnapshot();
          scheduleNext();
        }
      }, baseDelay);
    };

    const onVisibility = () => {
      if (!document.hidden && !cancelled) {
        fetchLiveSnapshot().then(scheduleNext);
      } else if (timerRef.current) {
        window.clearTimeout(timerRef.current);
      }
    };

    document.addEventListener('visibilitychange', onVisibility);
    fetchLiveSnapshot().then(scheduleNext);

    return () => {
      cancelled = true;
      document.removeEventListener('visibilitychange', onVisibility);
      if (timerRef.current) window.clearTimeout(timerRef.current);
    };
  }, [mode, isRunningScenario, liveSnapshot?.running, fetchLiveSnapshot]);

  // Trigger POST /demo/run — never auto-retried, handles 403/409 gracefully
  const runAllTransports = useCallback(async () => {
    if (isRunningScenario) return;
    if (mode !== 'live') {
      setMode('live');
      setPausedSnapshot(null);
      setReplayCursorSeq(null);
    }

    setIsRunningScenario(true);
    setRunElapsedMs(0);
    setRestartNotice(null);
    setRunNotice({
      tone: 'info',
      message: 'Running four-transport scenario (REST, HTTP JSON-RPC, WebSocket, WebTransport)…',
    });
    setLiveAnnouncement('Running all four transports scenario.');

    const startMs = Date.now();
    runTimerRef.current = window.setInterval(() => {
      setRunElapsedMs(Date.now() - startMs);
    }, 100);

    try {
      const res = await fetch('/demo/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify({}),
      });

      const body = await res.json().catch(() => ({}));

      if (res.status === 409) {
        setRunNotice({
          tone: 'warning',
          message:
            body.error ||
            'Another scenario run is already active (HTTP 409). Continuing to follow the live capture.',
        });
        setLiveAnnouncement('A scenario run is already active. Following live capture.');
        await fetchLiveSnapshot();
        return;
      }

      if (res.status === 403) {
        setRunNotice({
          tone: 'error',
          message:
            body.error ||
            'Scenario run rejected (HTTP 403): origin/host check failed on the loopback boundary.',
        });
        setLiveAnnouncement('Scenario run rejected due to origin check.');
        return;
      }

      if (!res.ok) {
        await fetchLiveSnapshot();
        setRunNotice({
          tone: 'error',
          message:
            body.error ||
            `Scenario failed (HTTP ${res.status}). Any partial trace evidence already received remains visible.`,
        });
        setLiveAnnouncement('Scenario run failed. Partial evidence retained.');
        return;
      }

      const summary = body as ScenarioRunSummary;
      await fetchLiveSnapshot();

      // Clear time bounds so the fresh scenario is immediately framed
      setFilters((prev) => ({
        ...prev,
        fromMs: null,
        toMs: null,
        bucketFilter: null,
      }));
      setAutoFollow(true);

      setRunNotice({
        tone: summary.status === 'completed' ? 'success' : 'warning',
        message: `Run ${summary.run_id} ${summary.status} in ${summary.duration_ms} ms (${summary.emitted_events} events · shared note ${summary.note_id}).`,
      });
      setLiveAnnouncement(
        `Scenario run ${summary.status}. ${summary.emitted_events} trace events recorded.`
      );
    } catch (err) {
      await fetchLiveSnapshot();
      setRunNotice({
        tone: 'error',
        message:
          err instanceof Error
            ? `Scenario request failed: ${err.message}. Trace refreshed with any partial results.`
            : 'Scenario request failed. Trace refreshed with any partial results.',
      });
      setLiveAnnouncement('Scenario request failed.');
    } finally {
      if (runTimerRef.current) {
        window.clearInterval(runTimerRef.current);
        runTimerRef.current = null;
      }
      setIsRunningScenario(false);
    }
  }, [isRunningScenario, mode, fetchLiveSnapshot]);

  const pausedCandidate = useMemo(() => {
    if (pausedAt === null || !liveSnapshot) return null;
    const events = liveSnapshot.events.filter((event) => event.sequence <= pausedAt);
    const oldest = collector ? events.at(-1) : events[0];
    const newest = collector ? events[0] : events.at(-1);
    return {
      ...liveSnapshot,
      events,
      retained_range: {
        ...liveSnapshot.retained_range,
        min_sequence: oldest?.sequence ?? 0,
        max_sequence: newest?.sequence ?? 0,
      },
    };
  }, [collector, liveSnapshot, pausedAt]);

  useEffect(() => {
    if (isPaused) setPausedSnapshot((current) => current ?? pausedCandidate);
    else setPausedSnapshot(null);
  }, [isPaused, pausedCandidate]);

  useEffect(() => {
    setReplayCursorSeq(null);
    setFilters((previous) => ({ ...previous, bucketFilter: null, cohortEventIds: null, cohortLabel: null }));
  }, [mode, sampleId]);

  useEffect(() => {
    if (!isPaused && mode === 'live') setReplayCursorSeq(null);
  }, [isPaused, mode]);

  const liveCeiling = liveSnapshot?.retained_range.max_sequence ?? 0;
  const lookup = collector && mode === 'live' ? correlationLookup(filters.searchQuery) : null;
  const lookupId = lookup?.id;
  const exactLookup = lookup?.exact ?? false;
  const locationParams = new URLSearchParams(window.location.search);
  const pageBefore = timelineSearch(locationParams) === filters.searchQuery.trim()
    ? locationParams.get('before') : null;
  const lookupBefore = pausedAt === null ? pageBefore
    : String(Math.min(pageBefore ? Number(pageBefore) : Infinity, pausedAt + 1));
  const lookupKey = lookupId ? JSON.stringify([lookupId, lookupBefore]) : null;
  const [lookupResult, setLookupResult] = useState<{
    key: string;
    snapshot: TraceSnapshot | null;
    error?: string;
  } | null>(null);

  useEffect(() => {
    if (!lookupId || !lookupKey) return;
    const controller = new AbortController();
    const timer = window.setTimeout(async () => {
      const query = new URLSearchParams({ correlation_id: lookupId, limit: String(COLLECTOR_PAGE_SIZE) });
      if (lookupBefore) query.set('before', lookupBefore);
      try {
        const response = await fetch(`/api/timeline?${query}`, {
          headers: { Accept: 'application/json' },
          cache: 'no-store',
          signal: controller.signal,
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const snapshot = toCollectorSnapshot(await response.json());
        if (!controller.signal.aborted) setLookupResult({ key: lookupKey, snapshot });
      } catch (error) {
        if (!controller.signal.aborted) {
          setLookupResult({
            key: lookupKey,
            snapshot: null,
            error: error instanceof Error ? error.message : 'Unable to reach the collector',
          });
        }
      }
    }, 250);
    return () => {
      window.clearTimeout(timer);
      controller.abort();
    };
  }, [lookupBefore, lookupId, lookupKey, liveCeiling]);

  const matchingLookup = lookupResult?.key === lookupKey ? lookupResult : null;
  const matchingSnapshot = matchingLookup?.snapshot;
  const activeSnapshot = mode === 'recorded' ? getRecordedSnapshot(sampleId)
    : matchingSnapshot && (exactLookup || matchingSnapshot.events.length) ? matchingSnapshot
    : isPaused ? pausedSnapshot ?? pausedCandidate : liveSnapshot;

  useEffect(() => {
    if (mode !== 'live') return;
    onCaptureStatus({
      at: lastGoodAt,
      connection: pollError ? 'stale' : initialLoading ? 'loading' : 'connected',
      sequence: liveCeiling,
    });
  }, [mode, lastGoodAt, pollError, initialLoading, liveCeiling, onCaptureStatus]);

  // Normalize events & apply optional replay virtual clock cursor
  const allEvents = useMemo(() => {
    const normalized = normalizeSnapshotEvents(activeSnapshot);
    if (replayCursorSeq !== null) {
      return normalized.filter((e) => e.sequence <= replayCursorSeq);
    }
    return normalized;
  }, [activeSnapshot, replayCursorSeq]);

  const fullEventsCount = useMemo(
    () => (activeSnapshot?.events ? activeSnapshot.events.length : 0),
    [activeSnapshot]
  );

  const graph = useMemo(() => buildEntityGraph(allEvents), [allEvents]);

  const filteredEvents = useMemo(
    () => filterEvents(allEvents, filters, graph),
    [allEvents, filters, graph]
  );

  // Protocol summaries use current time window & non-protocol filters so clicking toggles cleanly
  const protocolContextEvents = useMemo(() => {
    if (filters.protocols.length === 0) return filteredEvents;
    return filterEvents(
      allEvents,
      { ...filters, protocols: [] },
      graph
    );
  }, [allEvents, filters, filteredEvents, graph]);

  const metrics = useMemo(() => computeWorkspaceMetrics(filteredEvents), [filteredEvents]);
  const protocolMetrics = useMemo(
    () => computeWorkspaceMetrics(protocolContextEvents),
    [protocolContextEvents]
  );

  const karyogramRows = useMemo(
    () => buildKaryogramRows(graph, filteredEvents, expandedIds),
    [graph, filteredEvents, expandedIds]
  );

  const relationshipArcs = useMemo(
    () => computeRelationshipArcs(selection, graph, karyogramRows),
    [selection, graph, karyogramRows]
  );

  const availableKinds = useMemo(() => {
    const set = new Set<string>();
    for (const ev of allEvents) set.add(ev.kind);
    return Array.from(set).sort();
  }, [allEvents]);

  const availableOutcomes = useMemo(() => {
    const set = new Set<string>();
    for (const ev of allEvents) set.add(ev.outcome ?? 'unknown');
    return Array.from(set).sort();
  }, [allEvents]);

  const availableSources = useMemo(() => {
    const set = new Set<string>();
    for (const ev of allEvents) set.add(ev.source);
    return Array.from(set).sort();
  }, [allEvents]);

  const selectItem = useCallback(
    (next: SelectionState | null, pushHistory = true) => {
      setSelection(next);
      syncUrl(route, mode, sampleId, exploreView, filters, next, pushHistory);
      if (next && next.type === 'entity') {
        // Ensure ancestor chain is expanded so the entity is visible in the karyogram
        const ancestors: string[] = [];
        let cur = graph.entities.get(next.id)?.parentId ?? null;
        while (cur) {
          ancestors.push(cur);
          cur = graph.entities.get(cur)?.parentId ?? null;
        }
        if (ancestors.length > 0) {
          setExpandedIds((prev) => new Set([...prev, ...ancestors]));
        }
      }
    },
    [route, mode, sampleId, exploreView, filters, graph.entities, syncUrl]
  );

  const toggleProtocol = useCallback((protocol: PrimaryProtocol) => {
    setFilters((prev) => {
      const exists = prev.protocols.includes(protocol);
      return {
        ...prev,
        protocols: exists
          ? prev.protocols.filter((p) => p !== protocol)
          : [...prev.protocols, protocol],
        bucketFilter: null,
      };
    });
  }, []);

  const clearFilters = useCallback(() => {
    setFilters({
      protocols: [],
      includeDatabase: true,
      kind: 'all',
      outcome: 'all',
      source: 'all',
      searchQuery: '',
      fromMs: null,
      toMs: null,
      cohortEventIds: null,
      cohortLabel: null,
      bucketFilter: null,
    });
    setAutoFollow(true);
  }, []);

  const setTimeWindow = useCallback((fromMs: number | null, toMs: number | null) => {
    setFilters((prev) => ({
      ...prev,
      fromMs,
      toMs,
      bucketFilter: null,
    }));
    if (fromMs !== null || toMs !== null) {
      setAutoFollow(false);
    } else {
      setAutoFollow(true);
    }
  }, []);

  const toggleExpand = useCallback((entityId: string) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);
      if (next.has(entityId)) next.delete(entityId);
      else next.add(entityId);
      return next;
    });
  }, []);

  const expandAllVisible = useCallback(() => {
    const all = new Set<string>();
    for (const [id, entity] of graph.entities.entries()) {
      if (entity.childrenIds.length > 0) all.add(id);
    }
    setExpandedIds(all);
  }, [graph.entities]);

  const collapseAllVisible = useCallback(() => {
    setExpandedIds(new Set());
  }, []);

  const jumpToExploreCohort = useCallback(
    (eventIds: string[], cohortLabel: string, protocol?: PrimaryProtocol) => {
      const nextFilters: FilterState = {
        ...filters,
        protocols: protocol ? [protocol] : filters.protocols,
        cohortEventIds: eventIds,
        cohortLabel,
        bucketFilter: null,
      };
      setFilters(nextFilters);
      setRoute('explore');
      if (eventIds.length > 0) {
        const firstSel: SelectionState = { type: 'event', id: eventIds[0] };
        setSelection(firstSel);
        syncUrl('explore', mode, sampleId, exploreView, nextFilters, firstSel, true);
      } else {
        syncUrl('explore', mode, sampleId, exploreView, nextFilters, selection, true);
      }
      setLiveAnnouncement(`Opened ${eventIds.length} cohort observations in Explore.`);
    },
    [filters, mode, sampleId, exploreView, selection, syncUrl]
  );

  // Check whether current selection was evicted or absent
  const selectionStatus = useMemo(() => {
    if (!selection) return { state: 'none' as const };
    if (selection.type === 'event') {
      const found = graph.eventById.get(selection.id);
      if (found) return { state: 'found' as const, event: found };
      return { state: 'evicted' as const, id: selection.id };
    }
    const ent = graph.entities.get(selection.id);
    if (ent) return { state: 'found' as const, entity: ent };
    return { state: 'evicted' as const, id: selection.id };
  }, [selection, graph]);

  const liveStatus: LiveStatusInfo = {
    connectionState:
      mode === 'recorded'
        ? 'paused'
        : initialLoading
          ? 'loading'
          : pollError
            ? 'stale'
            : isPaused
              ? 'paused'
              : 'connected',
    lastGoodAt,
    error: pollError,
    restartNotice,
    autoFollow,
  };

  return {
    route,
    mode,
    exploreView,
    setExploreView,
    themePalette: THEMES[theme],
    filters,
    setFilters,
    toggleProtocol,
    clearFilters,
    setTimeWindow,
    selection,
    selectionStatus,
    selectItem,
    expandedIds,
    toggleExpand,
    expandAllVisible,
    collapseAllVisible,
    activeSnapshot,
    allEvents,
    fullEventsCount,
    filteredEvents,
    graph,
    karyogramRows,
    relationshipArcs,
    metrics,
    protocolMetrics,
    availableKinds,
    availableOutcomes,
    availableSources,
    lookupError: matchingLookup?.error,
    isPaused,
    replayCursorSeq,
    setReplayCursorSeq,
    liveStatus,
    initialLoading,
    retryFetch: fetchLiveSnapshot,
    isRunningScenario,
    runElapsedMs,
    runNotice,
    dismissRunNotice: () => setRunNotice(null),
    dismissRestartNotice: () => setRestartNotice(null),
    runAllTransports,
    liveAnnouncement,
    jumpToExploreCohort,
  };
}
