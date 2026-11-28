import { Activity, Table2 } from 'lucide-react';
import { CollectorControls } from './components/CollectorControls';
import { DistributionView } from './components/DistributionView';
import { EventKaryogram } from './components/EventKaryogram';
import { EventTable } from './components/EventTable';
import { FilterToolbar } from './components/FilterToolbar';
import { Header } from './components/Header';
import { InspectorPanel } from './components/InspectorPanel';
import { MetricStrip } from './components/MetricStrip';
import { ProtocolSummaryRow } from './components/ProtocolSummaryRow';
import { useTraceLab } from './hooks/useTraceLab';
import type { DatasetMode, DensityId, RecordedDatasetId } from './types/trace';
import type { CaptureStatus } from './components/CaptureBar';

export default function App({ collector, density, onRouteChange, onFollowCorrelation, onDatasetChange, pausedAt, onCaptureStatus }: {
  collector: boolean;
  density: DensityId;
  onRouteChange: () => void;
  onFollowCorrelation: (href: string) => void;
  onDatasetChange: (mode: DatasetMode, sample?: RecordedDatasetId) => void;
  pausedAt: number | null;
  onCaptureStatus: (status: CaptureStatus) => void;
}) {
  const lab = useTraceLab(collector, onRouteChange, pausedAt, onCaptureStatus);
  const runScenario = collector ? undefined : lab.runAllTransports;
  const followCorrelation = collector && lab.mode === 'live' ? onFollowCorrelation : undefined;

  const hasData = lab.allEvents.length > 0;
  const domainMinMs = lab.filters.fromMs ?? lab.graph.minMs;
  const domainMaxMs = lab.filters.toMs ?? lab.graph.maxMs;

  const handleFocusMetric = (
    metricKey: 'connections' | 'sessions' | 'invocations' | 'transactions' | 'deliveries'
  ) => {
    if (!hasData) return;
    if (metricKey === 'transactions') {
      lab.setFilters((prev) => ({
        ...prev,
        protocols: [],
        kind: 'all',
        source: 'database',
        bucketFilter: null,
      }));
      lab.toggleExpand('protocol:database');
    } else if (metricKey === 'deliveries') {
      lab.setFilters((prev) => ({
        ...prev,
        protocols: ['websocket'],
        kind: 'broker.delivery.dispatched',
        source: 'all',
        bucketFilter: null,
      }));
    } else if (metricKey === 'sessions') {
      lab.setFilters((prev) => ({
        ...prev,
        protocols: ['websocket', 'webtransport'],
        kind: 'all',
        source: 'all',
        bucketFilter: null,
      }));
    } else if (metricKey === 'invocations') {
      lab.setFilters((prev) => ({
        ...prev,
        kind: 'invocation.completed',
        source: 'all',
        bucketFilter: null,
      }));
    } else {
      lab.expandAllVisible();
    }
  };

  return (
    <div
      className="flex min-h-0 flex-1 flex-col overflow-y-auto"
      style={{ backgroundColor: 'var(--canvas)', color: 'var(--text-primary)' }}
    >
      <Header
        route={lab.route}
        mode={lab.mode}
        liveStatus={lab.liveStatus}
        isRunning={lab.isRunningScenario}
        runElapsedMs={lab.runElapsedMs}
        onRunAll={runScenario}
        onRetryFetch={lab.retryFetch}
        runNotice={lab.runNotice}
        onDismissRunNotice={lab.dismissRunNotice}
        onDismissRestartNotice={lab.dismissRestartNotice}
        liveAnnouncement={lab.liveAnnouncement}
        datasetLabel={lab.activeSnapshot?.dataset_label}
      />

      {collector && lab.mode === 'live' && (
        <CollectorControls nextBefore={lab.activeSnapshot?.next_before ?? null} />
      )}

      <FilterToolbar
        mode={lab.mode}
        filters={lab.filters}
        onChangeFilters={lab.setFilters}
        onClearFilters={lab.clearFilters}
        onSetTimeWindow={lab.setTimeWindow}
        availableKinds={lab.availableKinds}
        availableOutcomes={lab.availableOutcomes}
        availableSources={lab.availableSources}
        domainMinMs={lab.graph.minMs}
        domainMaxMs={lab.graph.maxMs}
        isPaused={lab.isPaused}
        liveStatus={lab.liveStatus}
        snapshot={lab.activeSnapshot}
        replayCursorSeq={lab.replayCursorSeq}
        onChangeReplayCursor={lab.setReplayCursorSeq}
      />
      {lab.lookupError && (
        <p role="alert" className="px-4 py-2 text-sm" style={{ color: 'var(--role-rejected)' }}>
          Collector ID lookup failed ({lab.lookupError}).
        </p>
      )}

      <main className="flex-1 px-4 py-4 space-y-4 max-w-[1680px] w-full mx-auto">
        {/* Four protocol summaries above the plot (click toggles protocol filter) */}
        <ProtocolSummaryRow
          metrics={lab.protocolMetrics}
          activeProtocols={lab.filters.protocols}
          hasData={hasData}
          onToggleProtocol={lab.toggleProtocol}
        />

        {lab.route === 'explore' ? (
          <>
            {/* Interactive Metric Strip */}
            <MetricStrip
              metrics={lab.metrics}
              hasData={hasData}
              windowMinMs={domainMinMs}
              windowMaxMs={domainMaxMs}
              snapshot={lab.activeSnapshot}
                paginated={collector && lab.mode === 'live'}
              onFocusMetric={handleFocusMetric}
            />

            {/* Permanent View Toggle beside Karyogram */}
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div
                className="inline-flex rounded-[5px] border overflow-hidden"
                style={{ borderColor: 'var(--border)', backgroundColor: 'var(--panel)' }}
                role="tablist"
                aria-label="Explore visualization view"
              >
                <button
                  type="button"
                  role="tab"
                  aria-selected={lab.exploreView === 'karyogram'}
                  onClick={() => lab.setExploreView('karyogram')}
                  className="h-8 px-3 text-[13px] font-medium inline-flex items-center gap-1.5 cursor-pointer lab-transition"
                  style={{
                    backgroundColor:
                      lab.exploreView === 'karyogram' ? 'var(--selected-bg)' : 'transparent',
                    color:
                      lab.exploreView === 'karyogram'
                        ? 'var(--text-primary)'
                        : 'var(--text-muted)',
                  }}
                >
                  <Activity size={14} strokeWidth={1.75} aria-hidden="true" />
                  <span>Event karyogram</span>
                </button>
                <button
                  type="button"
                  role="tab"
                  aria-selected={lab.exploreView === 'event-table'}
                  onClick={() => lab.setExploreView('event-table')}
                  className="h-8 px-3 text-[13px] font-medium border-l inline-flex items-center gap-1.5 cursor-pointer lab-transition"
                  style={{
                    borderColor: 'var(--border)',
                    backgroundColor:
                      lab.exploreView === 'event-table' ? 'var(--selected-bg)' : 'transparent',
                    color:
                      lab.exploreView === 'event-table'
                        ? 'var(--text-primary)'
                        : 'var(--text-muted)',
                  }}
                >
                  <Table2 size={14} strokeWidth={1.75} aria-hidden="true" />
                  <span>Event table</span>
                  {hasData && (
                    <span className="font-mono-data text-[11px] opacity-80">
                      ({lab.filteredEvents.length.toLocaleString()})
                    </span>
                  )}
                </button>
              </div>

              <div className="text-[12px]" style={{ color: 'var(--text-muted)' }}>
                Click any glyph, lane, or table row to inspect typed IDs, transactions, and
                relationships
              </div>
            </div>

            {/* Plot / Table + Optional Side Inspector */}
            <div className="flex flex-col xl:flex-row items-start gap-4">
              <div className="flex-1 min-w-0 w-full">
                {lab.exploreView === 'karyogram' ? (
                  <EventKaryogram
                    rows={lab.karyogramRows}
                    arcs={lab.relationshipArcs}
                    domainMinMs={domainMinMs}
                    domainMaxMs={domainMaxMs}
                    fullMinMs={lab.graph.minMs}
                    fullMaxMs={lab.graph.maxMs}
                    density={density}
                    themePalette={lab.themePalette}
                    selection={lab.selection}
                    onSelect={(sel) => lab.selectItem(sel)}
                    onToggleExpand={lab.toggleExpand}
                    onExpandAll={lab.expandAllVisible}
                    onCollapseAll={lab.collapseAllVisible}
                    onSetTimeWindow={lab.setTimeWindow}
                    onSelectBucket={(bucket) => {
                      lab.setFilters((prev) => ({ ...prev, bucketFilter: bucket }));
                      lab.setExploreView('event-table');
                    }}
                    onOpenTable={() => lab.setExploreView('event-table')}
                    isLoading={lab.initialLoading && lab.mode === 'live'}
                    isEmptyCapture={!hasData}
                    onRunAll={runScenario}
                    onOpenRecordedSample={() => onDatasetChange('recorded', 'recorded-v1.2-synthetic')}
                    onClearFilters={lab.clearFilters}
                  />
                ) : (
                  <EventTable
                    events={lab.filteredEvents}
                    onFollowCorrelation={followCorrelation}
                    density={density}
                    selection={lab.selection}
                    onSelect={(sel) => lab.selectItem(sel)}
                    bucketFilter={lab.filters.bucketFilter}
                    onClearBucketFilter={() =>
                      lab.setFilters((prev) => ({ ...prev, bucketFilter: null }))
                    }
                  />
                )}
              </div>

              <InspectorPanel
                selection={lab.selection}
                onFollowCorrelation={followCorrelation}
                selectionStatus={lab.selectionStatus}
                graph={lab.graph}
                onSelect={(sel) => lab.selectItem(sel)}
                onClose={() => lab.selectItem(null)}
              />
            </div>
          </>
        ) : (
          /* Distributions Screen + Side Inspector */
          <div className="flex flex-col xl:flex-row items-start gap-4">
            <div className="flex-1 min-w-0 w-full">
              <DistributionView
                events={lab.filteredEvents}
                onFollowCorrelation={followCorrelation}
                density={density}
                themePalette={lab.themePalette}
                selection={lab.selection}
                onSelect={(sel) => lab.selectItem(sel)}
                onJumpToExplore={lab.jumpToExploreCohort}
                isEmptyCapture={!hasData}
                onRunAll={runScenario}
                onOpenRecordedSample={() => onDatasetChange('recorded', 'recorded-v1.2-synthetic')}
              />
            </div>

            <InspectorPanel
              selection={lab.selection}
              onFollowCorrelation={followCorrelation}
              selectionStatus={lab.selectionStatus}
              graph={lab.graph}
              onSelect={(sel) => lab.selectItem(sel)}
              onClose={() => lab.selectItem(null)}
            />
          </div>
        )}
      </main>
    </div>
  );
}
