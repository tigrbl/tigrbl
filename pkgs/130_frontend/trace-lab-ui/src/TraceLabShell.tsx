import { lazy, Suspense, useCallback, useEffect, useRef, useState, type MouseEvent } from 'react';
import { version as frontendVersion } from '../package.json';
import { CaptureBar, type CaptureStatus } from './components/CaptureBar';
import { correlationLookup, timelineSearch } from './adapter/collectorSnapshot';
import { groupLookup, LIVE_CAPTURE_ID } from './correlations/core/liveFeed';
import { parseRoute } from './correlations/core/urlState';
import { THEME_ORDER, THEMES } from './theme/tokens';
import { useTraceTheme } from './theme/TraceTheme';
import type { DatasetMode, DensityId, RecordedDatasetId, ThemeId } from './types/trace';

const Correlations = lazy(() => import('./correlations/App'));
const Explorer = lazy(() => import('./App'));

const tabs = [
  { id: 'events', label: 'Events', path: '/explore', workspace: 'explorer' },
  { id: 'distributions', label: 'Distributions', path: '/distributions', workspace: 'explorer' },
  { id: 'index', label: 'Correlations', path: '/correlations', workspace: 'correlations' },
  { id: 'compare', label: 'Compare', path: '/correlations/compare', workspace: 'correlations' },
  { id: 'unassigned', label: 'Unassigned', path: '/correlations?unassigned=1', workspace: 'correlations' },
] as const;
type Tab = (typeof tabs)[number];
type Workspace = Tab['workspace'];
const SPACING_KEY = 'tigrbl.tracelab.density';
const EMPTY_STATUS: CaptureStatus = { connection: 'loading', at: null, sequence: 0 };

function writeDataset(url: URL, workspace: Workspace, mode: DatasetMode, sample: RecordedDatasetId) {
  url.searchParams.delete('sample');
  url.searchParams.delete('fixture');
  if (mode === 'live') {
    url.searchParams.delete('mode');
  } else {
    url.searchParams.set('mode', mode);
    if (workspace === 'explorer') url.searchParams.set('sample', sample);
    else url.searchParams.set('fixture', sample === 'recorded-stress-10k' ? 'scale-10k' : 'edge-cases');
  }
}

function activeTab(url: URL, collector: boolean): Tab['id'] {
  if (url.pathname === '/distributions') return 'distributions';
  if (!collector || url.pathname === '/explore') return 'events';
  const route = parseRoute(url.pathname);
  if (route.name === 'compare') return 'compare';
  return route.name === 'index' && url.searchParams.get('unassigned') === '1' ? 'unassigned' : 'index';
}

function activeCorrelation(url: URL): string | undefined {
  const route = parseRoute(url.pathname);
  if (route.name === 'detail' && route.groupKey.startsWith(`${LIVE_CAPTURE_ID}|`)) {
    return groupLookup(route.groupKey)?.value;
  }
  if (url.pathname === '/explore' || url.pathname === '/distributions') {
    const lookup = correlationLookup(timelineSearch(url.searchParams));
    return lookup?.exact ? lookup.id : undefined;
  }
  return url.searchParams.get('correlation_id') || undefined;
}

function getInitialSpacing(): DensityId {
  try {
    const saved = localStorage.getItem(SPACING_KEY);
    if (saved === 'dense' || saved === 'compact' || saved === 'comfortable') return saved;
  } catch {
    // The spacing control still works when storage is unavailable.
  }
  return window.innerWidth < 768 ? 'comfortable' : 'compact';
}

export function TraceLabShell({
  collector, backendVersion, imageVersion,
}: {
  collector: boolean;
  backendVersion?: string;
  imageVersion?: string;
}) {
  const [location, setLocation] = useState(() => window.location.href);
  const url = new URL(location);
  const currentTab = activeTab(url, collector);
  const mode = url.searchParams.get('mode') === 'recorded' ? 'recorded' : 'live';
  const [lastSample, setLastSample] = useState<RecordedDatasetId>('recorded-v1.2-synthetic');
  const sample = mode === 'live' ? lastSample
    : url.searchParams.get('sample') === 'recorded-stress-10k' || url.searchParams.get('fixture') === 'scale-10k'
      ? 'recorded-stress-10k' : 'recorded-v1.2-synthetic';
  const [status, setStatus] = useState(EMPTY_STATUS);
  const [paused, setPaused] = useState<CaptureStatus | null>(null);
  const [spacing, setSpacing] = useState(getInitialSpacing);
  const remembered = useRef<Partial<Record<Workspace, string>>>({});
  const { theme, setTheme } = useTraceTheme();
  const visibleTabs = collector ? tabs : tabs.filter((tab) => tab.workspace === 'explorer');
  const workspace = tabs.find((tab) => tab.id === currentTab)!.workspace;

  const updateActiveTab = useCallback(() => setLocation(window.location.href), []);

  useEffect(() => {
    window.addEventListener('popstate', updateActiveTab);
    return () => window.removeEventListener('popstate', updateActiveTab);
  }, [updateActiveTab]);

  useEffect(() => {
    if (mode === 'recorded') {
      setLastSample(sample);
      setPaused(null);
    }
  }, [mode, sample]);

  useEffect(() => {
    try {
      localStorage.setItem(SPACING_KEY, spacing);
    } catch {
      // The spacing control still works when storage is unavailable.
    }
  }, [spacing]);

  function tabHref(tab: Tab) {
    return !collector && tab.id === 'events' ? '/' : tab.path;
  }

  function pushLocation(target: string | URL) {
    window.history.pushState(null, '', target);
    window.dispatchEvent(new PopStateEvent('popstate'));
  }

  function followCorrelation(href: string) {
    remembered.current.explorer = window.location.pathname + window.location.search;
    pushLocation(href);
  }

  function selectDataset(nextMode: DatasetMode, nextSample = sample) {
    if (mode === nextMode && sample === nextSample) return;
    const target = new URL(window.location.href);
    if (parseRoute(target.pathname).name === 'detail') target.pathname = '/correlations';
    for (const key of ['entity', 'before', 'from', 'to', 'pinned', 'select', 'selectType', 'win', 'linked', 'correlation_id', 'correlation_event', 'q']) {
      target.searchParams.delete(key);
    }
    setPaused(null);
    setStatus(EMPTY_STATUS);
    writeDataset(target, workspace, nextMode, nextSample);
    pushLocation(target);
  }

  function navigate(event: MouseEvent<HTMLAnchorElement>, tab: Tab) {
    if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    const current = new URL(window.location.href);
    if (currentTab === tab.id && parseRoute(current.pathname).name !== 'detail') return;

    const target = new URL(tabHref(tab), current.origin);
    const sameWorkspace = workspace === tab.workspace;
    const saved = sameWorkspace
      ? current
      : new URL(remembered.current[tab.workspace] ?? target, current.origin);
    const correlation = sameWorkspace || mode === 'recorded' ? undefined : activeCorrelation(current);
    const followCorrelation = correlation && (tab.id === 'events' || tab.id === 'index');
    const keys = followCorrelation
      ? []
      : tab.workspace === 'explorer'
        ? saved.searchParams.keys()
        : ['mode', 'fixture', 'pinned', 'proto'];
    for (const key of keys) {
      const value = saved.searchParams.get(key);
      if (value !== null) target.searchParams.set(key, value);
    }
    if (!sameWorkspace) {
      remembered.current[workspace] = current.pathname + current.search;
    }
    if (followCorrelation) {
      target.searchParams.set('correlation_id', correlation);
    }
    writeDataset(target, tab.workspace, mode, sample);
    pushLocation(target);
  }

  const controlStyle = { backgroundColor: 'var(--canvas)', borderColor: 'var(--border)' };
  return (
    <div className="flex h-dvh flex-col overflow-hidden" style={{ backgroundColor: 'var(--canvas)', color: 'var(--text-primary)' }}>
      <header className="shrink-0 border-b px-3 sm:px-4" style={{ backgroundColor: 'var(--panel)', borderColor: 'var(--border)' }}>
        <div className="flex min-h-[48px] flex-wrap items-center gap-x-5 gap-y-1 py-1.5">
          <span className="font-editorial whitespace-nowrap text-[17px] sm:text-[20px]">Transport Trace Lab</span>
          <nav aria-label="Trace Lab views" className="flex flex-wrap items-center gap-1">
            {visibleTabs.map((tab) => {
              const active = currentTab === tab.id;
              return (
                <a
                  key={tab.id}
                  href={tabHref(tab)}
                  onClick={(event) => navigate(event, tab)}
                  aria-current={active ? 'page' : undefined}
                  className="rounded-[4px] px-2.5 py-1.5 text-[13px] font-medium whitespace-nowrap lab-transition"
                  style={{
                    backgroundColor: active ? 'var(--selected-bg)' : 'transparent',
                    boxShadow: active ? 'inset 0 0 0 1px var(--accent)' : 'none',
                    color: active ? 'var(--text-primary)' : 'var(--text-muted)',
                  }}
                >
                  {tab.label}
                </a>
              );
            })}
          </nav>
        </div>
      </header>
      <CaptureBar
        mode={mode}
        sample={sample}
        status={status}
        paused={paused}
        onDatasetChange={selectDataset}
        onTogglePause={() => setPaused(paused ? null : status)}
      />
      <Suspense fallback={<p className="flex-1 p-4" role="status">Loading trace view…</p>}>
        {workspace === 'correlations'
          ? <Correlations onRouteChange={updateActiveTab} pausedAt={paused?.sequence ?? null} onCaptureStatus={setStatus} />
          : <Explorer
              collector={collector}
              density={spacing}
              onRouteChange={updateActiveTab}
              onFollowCorrelation={followCorrelation}
              onDatasetChange={selectDataset}
              pausedAt={paused?.sequence ?? null}
              onCaptureStatus={setStatus}
            />}
      </Suspense>
      <footer className="flex shrink-0 flex-wrap items-center justify-between gap-x-4 gap-y-2 border-t px-3 py-2 text-[12px] sm:px-4" style={{ backgroundColor: 'var(--panel)', borderColor: 'var(--border)' }}>
        <div className="flex flex-wrap items-baseline gap-x-3" style={{ color: 'var(--text-muted)' }}>
          <span>© 2026 Tigrbl – Transport Trace Lab</span>
          <dl aria-label="Deployed versions" className="flex flex-wrap gap-x-3 gap-y-1 tabular-nums">
            <div className="flex gap-1">
              <dt>Backend</dt>
              <dd data-testid="backend-version">{backendVersion ? 'v' + backendVersion : 'Unavailable'}</dd>
            </div>
            <div className="flex gap-1">
              <dt>Frontend</dt>
              <dd data-testid="frontend-version">v{frontendVersion}</dd>
            </div>
            <div className="flex gap-1">
              <dt>Image</dt>
              <dd data-testid="image-version">{imageVersion ? 'v' + imageVersion : 'Unavailable'}</dd>
            </div>
          </dl>
        </div>
        <div className="flex flex-wrap items-center gap-x-3 gap-y-2">
          <label className="flex items-center gap-2">
            <span style={{ color: 'var(--text-muted)' }}>Theme</span>
            <select value={theme} onChange={(event) => setTheme(event.target.value as ThemeId)} className="rounded-sm border px-2 py-1" style={controlStyle}>
              {THEME_ORDER.map((id) => <option key={id} value={id}>{THEMES[id].name}</option>)}
            </select>
          </label>
          <label className="flex items-center gap-2">
            <span style={{ color: 'var(--text-muted)' }}>Explorer spacing</span>
            <select value={spacing} onChange={(event) => setSpacing(event.target.value as DensityId)} className="rounded-sm border px-2 py-1" style={controlStyle}>
              <option value="dense">Dense</option>
              <option value="compact">Compact</option>
              <option value="comfortable">Comfortable</option>
            </select>
          </label>
        </div>
      </footer>
    </div>
  );
}
