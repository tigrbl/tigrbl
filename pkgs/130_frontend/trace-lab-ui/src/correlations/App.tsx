import React, { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react';
import type { CaptureStatus } from '../components/CaptureBar';
import { buildCorrelationIndex } from './core/correlationEngine';
import { applyCorrelationTheme } from './core/themes';
import { useTraceTheme } from '../theme/TraceTheme';
import type {
  CorrelationIndex,
  DatasetMode,
  SearchIdType,
  TraceSnapshotInput,
  TransportProtocol,
} from './core/types';
import {
  parseQueryState,
  parseRoute,
  serializeUrl,
  type AppRoute,
  type NavigationHistorySnapshot,
} from './core/urlState';
import type { RecordedFixtureId } from './data/fixtures';
import { groupLookup, loadLiveSnapshot, parseTraceLookup } from './core/liveFeed';
import './index.css';
import { CompareView } from './views/CompareView';
import { CorrelationDetailView } from './views/CorrelationDetailView';
import { CorrelationIndexView } from './views/CorrelationIndexView';

function readCorrelationLink() {
  const params = new URLSearchParams(window.location.search);
  const id = params.get('correlation_id');
  if (!id) return null;
  const sequence = Number(params.get('correlation_event'));
  return { id, sequence: Number.isSafeInteger(sequence) && sequence > 0 ? sequence : undefined };
}

export default function App({ onRouteChange, pausedAt, onCaptureStatus }: {
  onRouteChange: () => void;
  pausedAt: number | null;
  onCaptureStatus: (status: CaptureStatus) => void;
}) {
  // Parse initial URL
  const initialRoute = parseRoute(window.location.pathname);
  const initialQuery = parseQueryState(window.location.search);

  const [route, setRoute] = useState<AppRoute>(initialRoute);
  const [mode, setMode] = useState<DatasetMode>(initialQuery.mode);
  const [fixtureId, setFixtureId] = useState<RecordedFixtureId>(
    initialQuery.fixture === 'scale-10k' ? 'scale-10k' : 'edge-cases'
  );
  const { theme } = useTraceTheme();
  const surface = useRef<HTMLDivElement>(null);

  // Filter / search / detail states encoded in URL
  const correlationLink = useRef(readCorrelationLink());
  const [searchQuery, setSearchQuery] = useState<string>(initialQuery.q ?? correlationLink.current?.id ?? '');
  const [idType, setIdType] = useState<SearchIdType>(initialQuery.idType ?? 'correlation_id');
  const [protocolFilter, setProtocolFilter] = useState<TransportProtocol | 'all'>(
    initialQuery.proto ?? 'all'
  );
  const [showUnassigned, setShowUnassigned] = useState<boolean>(
    Boolean(initialQuery.unassigned)
  );
  const [detailViewMode, setDetailViewMode] = useState<'waterfall' | 'events'>(
    initialQuery.view ?? 'waterfall'
  );
  const [showLinkedContext, setShowLinkedContext] = useState<boolean>(
    Boolean(initialQuery.linked)
  );
  const [selectedItem, setSelectedItem] = useState<{
    type: 'mark' | 'edge';
    id: string;
  } | null>(
    initialQuery.select
      ? { type: initialQuery.selectType ?? 'mark', id: initialQuery.select }
      : null
  );
  const [zoomWindow, setZoomWindow] = useState<{
    startMs: number;
    endMs: number;
  } | null>(
    initialQuery.winStart !== undefined && initialQuery.winEnd !== undefined
      ? { startMs: initialQuery.winStart, endMs: initialQuery.winEnd }
      : null
  );
  const [pinnedKeys, setPinnedKeys] = useState<Set<string>>(
    () => new Set(initialQuery.pinned ?? [])
  );

  // Data feed state
  const [rawSnapshot, setRawSnapshot] = useState<TraceSnapshotInput | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const pausedAtRef = useRef(pausedAt);
  const [refresh, setRefresh] = useState(0);
  const [captureStatus, setCaptureStatus] = useState<CaptureStatus>({ connection: 'loading', at: null, sequence: 0 });

  useEffect(() => {
    if (pausedAtRef.current !== null && pausedAt === null) {
      setRefresh((revision) => revision + 1);
    }
    pausedAtRef.current = pausedAt;
  }, [pausedAt]);

  useEffect(() => {
    if (mode === 'live') onCaptureStatus(captureStatus);
  }, [mode, captureStatus, onCaptureStatus]);

  // Explicit history stack for Back restoration (selection, zoom, filters, scroll)
  const navStackRef = useRef<NavigationHistorySnapshot[]>([]);

  useLayoutEffect(() => {
    if (surface.current) applyCorrelationTheme(surface.current, theme);
  }, [theme]);

  // Build CorrelationIndex deterministically from active snapshot
  const index = useMemo<CorrelationIndex | null>(() => {
    if (!rawSnapshot) return null;
    return buildCorrelationIndex(rawSnapshot);
  }, [rawSnapshot]);

  // Sync URL address bar cleanly without clobbering history entries
  const syncUrl = useCallback(
    (
      nextRoute: AppRoute,
      overrides?: Partial<{
        mode: DatasetMode;
        fixture: RecordedFixtureId;
        select: string;
        selectType: 'mark' | 'edge';
        winStart: number;
        winEnd: number;
        proto: TransportProtocol | 'all';
        view: 'waterfall' | 'events';
        linked: boolean;
        q: string;
        idType: SearchIdType;
        unassigned: boolean;
        pinned: string[];
      }>,
      push = false
    ) => {
      const m = overrides?.mode ?? mode;
      const url = serializeUrl(nextRoute, {
        mode: m,
        fixture: m === 'recorded' ? overrides?.fixture ?? fixtureId : undefined,
        select:
          nextRoute.name === 'detail'
            ? overrides && 'select' in overrides
              ? overrides.select
              : selectedItem?.id
            : undefined,
        selectType:
          nextRoute.name === 'detail'
            ? overrides && 'selectType' in overrides
              ? overrides.selectType
              : selectedItem?.type
            : undefined,
        winStart:
          nextRoute.name === 'detail'
            ? overrides && 'winStart' in overrides
              ? overrides.winStart
              : zoomWindow?.startMs
            : undefined,
        winEnd:
          nextRoute.name === 'detail'
            ? overrides && 'winEnd' in overrides
              ? overrides.winEnd
              : zoomWindow?.endMs
            : undefined,
        proto: overrides?.proto ?? protocolFilter,
        view: nextRoute.name === 'detail' ? overrides?.view ?? detailViewMode : undefined,
        linked: nextRoute.name === 'detail' ? overrides?.linked ?? showLinkedContext : undefined,
        q: nextRoute.name === 'index' ? overrides?.q ?? searchQuery : undefined,
        idType: nextRoute.name === 'index' ? overrides?.idType ?? idType : undefined,
        unassigned: nextRoute.name === 'index' ? overrides?.unassigned ?? showUnassigned : undefined,
        pinned: overrides?.pinned ?? Array.from(pinnedKeys),
      });

      if (push) {
        window.history.pushState({ url }, '', url);
      } else {
        window.history.replaceState({ url }, '', url);
      }
      onRouteChange();
    },
    [
      mode,
      fixtureId,
      selectedItem,
      zoomWindow,
      protocolFilter,
      detailViewMode,
      showLinkedContext,
      searchQuery,
      idType,
      showUnassigned,
      pinnedKeys,
      onRouteChange,
    ]
  );

  // Handle browser Back/Forward
  useEffect(() => {
    const onPopState = () => {
      const parsedRoute = parseRoute(window.location.pathname);
      const parsedQuery = parseQueryState(window.location.search);
      correlationLink.current = readCorrelationLink();
      setRoute(parsedRoute);
      setMode(parsedQuery.mode);
      setFixtureId(parsedQuery.fixture === 'scale-10k' ? 'scale-10k' : 'edge-cases');
      setSearchQuery(parsedQuery.q ?? correlationLink.current?.id ?? '');
      setIdType(parsedQuery.idType ?? 'correlation_id');
      setProtocolFilter(parsedQuery.proto ?? 'all');
      setShowUnassigned(Boolean(parsedQuery.unassigned));
      setPinnedKeys(new Set(parsedQuery.pinned ?? []));
      setDetailViewMode(parsedQuery.view ?? 'waterfall');
      setShowLinkedContext(Boolean(parsedQuery.linked));
      setSelectedItem(
        parsedQuery.select
          ? { type: parsedQuery.selectType ?? 'mark', id: parsedQuery.select }
          : null
      );
      setZoomWindow(
        parsedQuery.winStart !== undefined && parsedQuery.winEnd !== undefined
          ? { startMs: parsedQuery.winStart, endMs: parsedQuery.winEnd }
          : null
      );
    };
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, []);

  const detailKey = route.name === 'detail' ? route.groupKey : null;
  const pinSelection = route.name === 'compare' ? [...pinnedKeys].sort().join(',') : '';
  const lookup = route.name === 'index' ? searchQuery : '';

  useEffect(() => {
    const controller = new AbortController();
    let timer: number;
    const detail = detailKey ? groupLookup(detailKey) : undefined;
    const search = correlationLink.current?.id === lookup
      ? { value: lookup, field: 'correlation_id' as const }
      : parseTraceLookup(lookup, idType);
    const pins = pinSelection ? pinSelection.split(',').map(groupLookup).filter((pin) => pin !== undefined) : [];
    const lookups = detail ? [detail] : search ? [search] : pins;
    const deduplicated = [...new Map(lookups.map((item) => [item.field + ':' + item.value, item])).values()];
    setLoading(true);

    async function poll(first = false) {
      try {
        const snapshot = mode === 'recorded'
          ? (await import('./data/fixtures')).getRecordedFixture(fixtureId)
          : await loadLiveSnapshot(deduplicated, Boolean(search), controller.signal, Boolean(detail), Boolean(pinSelection));
        if (controller.signal.aborted) return;
        setErrorMessage(null);
        if (mode === 'live') {
          setCaptureStatus({ connection: 'connected', at: snapshot.generated_at, sequence: snapshot.sequence_ceiling });
        }
        const ceiling = mode === 'live' ? pausedAtRef.current : null;
        if (ceiling === null) {
          setRawSnapshot(snapshot);
        } else if (first) {
          const events = snapshot.events.filter((event) => event.seq <= ceiling);
          setRawSnapshot({
            ...snapshot,
            events,
            sequence_floor: events[0]?.seq ?? 0,
            sequence_ceiling: events.at(-1)?.seq ?? 0,
            retained_count: events.length,
          });
        }
      } catch (error) {
        if (controller.signal.aborted) return;
        setErrorMessage(error instanceof Error ? error.message : 'Unable to reach trace feed');
        if (mode === 'live') setCaptureStatus((current) => ({ ...current, connection: 'stale' }));
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
          if (mode === 'live') timer = window.setTimeout(() => void poll(), 3000);
        }
      }
    }

    timer = window.setTimeout(() => void poll(true), lookup ? 200 : 0);
    return () => {
      controller.abort();
      window.clearTimeout(timer);
    };
  }, [mode, fixtureId, detailKey, lookup, idType, pinSelection, refresh]);

  const activeDetailGroup = detailKey ? index?.groupsByKey.get(detailKey) : undefined;

  useEffect(() => {
    const link = correlationLink.current;
    if (!link || !index || loading || errorMessage || lookup !== link.id) return;
    correlationLink.current = null;
    const candidates = index.groups.filter((group) => group.scopeIdentity === link.id);
    const matches = link.sequence !== undefined
      ? candidates.filter((group) => group.events.some(({ event }) => event.seq === link.sequence))
      : candidates;
    if (matches.length === 1) {
      const nextRoute: AppRoute = { name: 'detail', groupKey: matches[0].groupKey };
      setRoute(nextRoute);
      syncUrl(nextRoute);
    }
  }, [index, loading, errorMessage, lookup, syncUrl]);

  // Navigation helpers preserving selection, zoom, filters, and scroll for Back restoration
  const pushCurrentSnapshot = () => {
    const scrollContainer = document.querySelector('[data-testid="waterfall-scroll-container"]');
    navStackRef.current.push({
      url: window.location.pathname + window.location.search,
      scrollY: scrollContainer ? scrollContainer.scrollTop : window.scrollY,
      scrollX: scrollContainer ? scrollContainer.scrollLeft : window.scrollX,
      selectedId: selectedItem?.id,
      selectedType: selectedItem?.type,
      winStart: zoomWindow?.startMs,
      winEnd: zoomWindow?.endMs,
      view: detailViewMode,
      linked: showLinkedContext,
    });
  };

  const navigateToGroup = (groupKey: string) => {
    pushCurrentSnapshot();
    const nextRoute: AppRoute = { name: 'detail', groupKey };
    setRoute(nextRoute);
    setSelectedItem(null);
    setZoomWindow(null);
    setDetailViewMode('waterfall');
    syncUrl(
      nextRoute,
      {
        select: undefined,
        selectType: undefined,
        winStart: undefined,
        winEnd: undefined,
        view: 'waterfall',
      },
      true
    );
  };

  const handleBack = () => {
    const prev = navStackRef.current.pop();
    if (prev) {
      const u = new URL(prev.url, window.location.origin);
      const parsedRoute = parseRoute(u.pathname);
      const parsedQuery = parseQueryState(u.search);
      setRoute(parsedRoute);
      setSelectedItem(
        prev.selectedId
          ? { type: prev.selectedType ?? 'mark', id: prev.selectedId }
          : parsedQuery.select
          ? { type: parsedQuery.selectType ?? 'mark', id: parsedQuery.select }
          : null
      );
      setZoomWindow(
        prev.winStart !== undefined && prev.winEnd !== undefined
          ? { startMs: prev.winStart, endMs: prev.winEnd }
          : parsedQuery.winStart !== undefined && parsedQuery.winEnd !== undefined
          ? { startMs: parsedQuery.winStart, endMs: parsedQuery.winEnd }
          : null
      );
      setDetailViewMode(prev.view ?? parsedQuery.view ?? 'waterfall');
      setShowLinkedContext(prev.linked ?? Boolean(parsedQuery.linked));
      setShowUnassigned(Boolean(parsedQuery.unassigned));
      window.history.replaceState({ url: prev.url }, '', prev.url);
      onRouteChange();

      requestAnimationFrame(() => {
        const sc = document.querySelector('[data-testid="waterfall-scroll-container"]');
        if (sc) {
          sc.scrollTop = prev.scrollY;
          sc.scrollLeft = prev.scrollX;
        } else {
          window.scrollTo(prev.scrollX, prev.scrollY);
        }
      });
      return;
    }

    const nextRoute: AppRoute = { name: 'index' };
    setRoute(nextRoute);
    syncUrl(nextRoute, undefined, true);
  };

  const navigateToCompare = () => {
    pushCurrentSnapshot();
    const nextRoute: AppRoute = { name: 'compare' };
    setRoute(nextRoute);
    syncUrl(nextRoute, undefined, true);
  };

  const handleTogglePin = (groupKey: string) => {
    setPinnedKeys((prev) => {
      const next = new Set(prev);
      if (next.has(groupKey)) next.delete(groupKey);
      else next.add(groupKey);
      syncUrl(route, { pinned: Array.from(next) }, false);
      return next;
    });
  };

  return (
    <div
      ref={surface}
      className="correlations-surface flex flex-1 min-h-0 flex-col overflow-hidden"
      style={{
        backgroundColor: 'var(--bg-canvas)',
        color: 'var(--text-primary)',
      }}
    >
      {/* Route Views */}
      {route.name !== 'index' && errorMessage && (route.name === 'compare' || activeDetailGroup) && (
        <p role="alert" className="px-4 py-2 text-sm" style={{ color: 'var(--status-err)' }}>{errorMessage}</p>
      )}
      {route.name === 'index' && (
        <CorrelationIndexView
          index={index}
          loading={loading}
          errorMessage={errorMessage}
          query={searchQuery}
          idType={idType}
          protocolFilter={protocolFilter}
          showUnassigned={showUnassigned}
          pinnedKeys={pinnedKeys}
          rowHeight={32}
          onQueryChange={(q) => {
            setSearchQuery(q);
            syncUrl(route, { q }, false);
          }}
          onIdTypeChange={(t) => {
            setIdType(t);
            syncUrl(route, { idType: t }, false);
          }}
          onProtocolFilterChange={(p) => {
            setProtocolFilter(p);
            syncUrl(route, { proto: p }, false);
          }}
          onToggleUnassigned={(show) => {
            setShowUnassigned(show);
            syncUrl(route, { unassigned: show }, false);
          }}
          onOpenGroup={navigateToGroup}
          onTogglePin={handleTogglePin}
          onOpenCompare={navigateToCompare}
        />
      )}

      {route.name === 'detail' && !activeDetailGroup && (
        <main className="p-6" aria-live="polite">
          <p>{errorMessage ?? (loading ? 'Loading correlation…' : 'This correlation is outside the available evidence.')}</p>
          <button type="button" className="underline mt-3" onClick={handleBack}>Back to correlations</button>
        </main>
      )}

      {route.name === 'detail' && index && activeDetailGroup && (
        <CorrelationDetailView
          index={index}
          group={activeDetailGroup}
          viewMode={detailViewMode}
          showLinkedContext={showLinkedContext}
          selectedItem={selectedItem}
          zoomWindow={zoomWindow}
          isPinned={pinnedKeys.has(activeDetailGroup.groupKey)}
          rowHeight={32}
          onBack={handleBack}
          onViewModeChange={(vm) => {
            setDetailViewMode(vm);
            syncUrl(route, { view: vm }, false);
          }}
          onToggleLinkedContext={(show) => {
            setShowLinkedContext(show);
            syncUrl(route, { linked: show }, false);
          }}
          onSelectItem={(item) => {
            setSelectedItem(item);
            syncUrl(
              route,
              { select: item?.id, selectType: item?.type },
              false
            );
          }}
          onZoomChange={(win) => {
            setZoomWindow(win);
            syncUrl(
              route,
              { winStart: win?.startMs, winEnd: win?.endMs },
              false
            );
          }}
          onFollowRelated={navigateToGroup}
          onTogglePin={handleTogglePin}
        />
      )}

      {route.name === 'compare' && (
        <CompareView
          index={index}
          pinnedKeys={pinnedKeys}
          onOpenGroup={navigateToGroup}
          onClearPins={() => {
            setPinnedKeys(new Set());
            syncUrl(route, { pinned: [] }, false);
          }}
        />
      )}
    </div>
  );
}
