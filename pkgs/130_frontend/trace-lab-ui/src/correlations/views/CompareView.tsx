import React, { useMemo, useState } from 'react';
import { ArrowUpRight, Pin, X } from 'lucide-react';
import {
  COMPARE_MEASURES,
  computeCohortDistributions,
} from '../core/analytics';
import { protocolLabel } from '../core/correlationEngine';
import type {
  CohortDistribution,
  CompareMeasureId,
  CorrelationIndex,
  HistogramBin,
  TransportProtocol,
} from '../core/types';
import { ProtocolTag, protocolColorVar } from '../components/StatusIndicator';

interface CompareViewProps {
  index: CorrelationIndex | null;
  pinnedKeys: Set<string>;
  onOpenGroup: (groupKey: string) => void;
  onClearPins: () => void;
}

const CHART_WIDTH = 680;
const CHART_HEIGHT = 148;
const STRIP_HEIGHT = 24;

export function CompareView({
  index,
  pinnedKeys,
  onOpenGroup,
  onClearPins,
}: CompareViewProps) {
  const [cohortMode, setCohortMode] = useState<'all' | 'pinned'>(
    pinnedKeys.size > 0 ? 'pinned' : 'all'
  );
  const [measureId, setMeasureId] = useState<CompareMeasureId>('measured_request_latency');
  const [chartType, setChartType] = useState<'histogram' | 'ecdf'>('histogram');
  const [binCount, setBinCount] = useState<number>(12);
  const [selectedBin, setSelectedBin] = useState<{
    protocol: TransportProtocol;
    bin: HistogramBin;
  } | null>(null);

  const cohortGroups = useMemo(() => {
    if (!index) return [];
    if (cohortMode === 'pinned' && pinnedKeys.size > 0) {
      return index.groups.filter((g) => pinnedKeys.has(g.groupKey));
    }
    return index.groups;
  }, [index, cohortMode, pinnedKeys]);

  const distributions = useMemo<CohortDistribution[]>(() => {
    if (!index || cohortGroups.length === 0) return [];
    return computeCohortDistributions(index, cohortGroups, measureId, binCount);
  }, [index, cohortGroups, measureId, binCount]);

  // Shared x-axis domain across transport lanes so cohorts compare visually on the same scale
  const globalDomain = useMemo(() => {
    const mins: number[] = [];
    const maxs: number[] = [];
    for (const d of distributions) {
      if (d.minMs !== null) mins.push(d.minMs);
      if (d.maxMs !== null) maxs.push(d.maxMs);
    }
    if (mins.length === 0) return { minMs: 0, maxMs: 100 };
    const min = Math.min(...mins);
    const max = Math.max(...maxs);
    return { minMs: Math.max(0, Math.floor(min * 0.9)), maxMs: Math.max(min + 1, Math.ceil(max * 1.05)) };
  }, [distributions]);

  const measureMeta = COMPARE_MEASURES[measureId];

  const valToX = (ms: number) => {
    const span = Math.max(1, globalDomain.maxMs - globalDomain.minMs);
    const pct = Math.max(0, Math.min(1, (ms - globalDomain.minMs) / span));
    return 36 + pct * (CHART_WIDTH - 56);
  };

  return (
    <main className="flex-1 overflow-y-auto px-4 sm:px-6 py-5 max-w-[1600px] w-full mx-auto space-y-5">
      {/* Header & Synthetic Dataset Disclosure */}
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="font-display text-[32px] leading-[1.15] tracking-[-0.01em]">
            Cohort comparison
          </h1>
          <div
            className="mt-1 flex flex-wrap items-center gap-x-2.5 gap-y-1 text-[12.5px]"
            style={{ color: 'var(--text-secondary)' }}
          >
            <span>{measureMeta.label}</span>
            <span aria-hidden="true">·</span>
            <span className="font-mono-tabular">boundary: {measureMeta.timingBoundary}</span>
            <span aria-hidden="true">·</span>
            <span className="font-mono-tabular">
              input cohort: {cohortGroups.length.toLocaleString()} correlations
            </span>
            {index?.syntheticLabel && (
              <>
                <span aria-hidden="true">·</span>
                <span className="font-medium" style={{ color: 'var(--accent)' }}>
                  {index.syntheticLabel}
                </span>
              </>
            )}
          </div>
        </div>

        {/* Chart & Measure Controls */}
        <div className="flex flex-wrap items-center gap-2">
          <div
            className="inline-flex p-0.5 rounded-[5px] border"
            style={{
              backgroundColor: 'var(--bg-panel)',
              borderColor: 'var(--border-rule)',
            }}
            role="group"
            aria-label="Input cohort selection"
          >
            <button
              type="button"
              onClick={() => {
                setCohortMode('all');
                setSelectedBin(null);
              }}
              aria-pressed={cohortMode === 'all' || pinnedKeys.size === 0}
              className="px-2.5 py-1 text-[12px] font-medium rounded-[4px] cursor-pointer whitespace-nowrap"
              style={{
                backgroundColor:
                  cohortMode === 'all' || pinnedKeys.size === 0 ? 'var(--accent)' : 'transparent',
                color:
                  cohortMode === 'all' || pinnedKeys.size === 0
                    ? 'var(--accent-text)'
                    : 'var(--text-secondary)',
              }}
            >
              {index?.mode === 'live' ? 'Loaded correlations' : 'Active capture'} ({index?.groups.length.toLocaleString() ?? 0})
            </button>
            <button
              type="button"
              disabled={pinnedKeys.size === 0}
              onClick={() => {
                setCohortMode('pinned');
                setSelectedBin(null);
              }}
              aria-pressed={cohortMode === 'pinned' && pinnedKeys.size > 0}
              className="inline-flex items-center gap-1 px-2.5 py-1 text-[12px] font-medium rounded-[4px] disabled:opacity-40 enabled:cursor-pointer whitespace-nowrap"
              style={{
                backgroundColor:
                  cohortMode === 'pinned' && pinnedKeys.size > 0 ? 'var(--accent)' : 'transparent',
                color:
                  cohortMode === 'pinned' && pinnedKeys.size > 0
                    ? 'var(--accent-text)'
                    : 'var(--text-secondary)',
              }}
            >
              <Pin className="w-3 h-3" />
              <span>Pinned ({pinnedKeys.size})</span>
            </button>
          </div>

          {pinnedKeys.size > 0 && (
            <button
              type="button"
              onClick={() => {
                onClearPins();
                setCohortMode('all');
              }}
              className="px-2 py-1 text-[11.5px] border rounded-[4px] cursor-pointer"
              style={{ borderColor: 'var(--border-rule)', color: 'var(--text-muted)' }}
            >
              Clear pins
            </button>
          )}
        </div>
      </div>

      {/* Measure, Distribution Type & Bin Count Strip */}
      <div
        className="flex flex-wrap items-center justify-between gap-3 px-4 py-2.5 rounded-[6px] border"
        style={{
          backgroundColor: 'var(--bg-panel)',
          borderColor: 'var(--border-rule)',
        }}
      >
        <div className="flex flex-wrap items-center gap-3">
          <label className="text-[12px] font-medium" htmlFor="compare-measure-select">
            Measure
          </label>
          <select
            id="compare-measure-select"
            value={measureId}
            onChange={(e) => {
              setMeasureId(e.target.value as CompareMeasureId);
              setSelectedBin(null);
            }}
            className="px-2.5 py-1.5 text-[12.5px] rounded-[4px] border cursor-pointer"
            style={{
              backgroundColor: 'var(--bg-canvas)',
              borderColor: 'var(--border-strong)',
              color: 'var(--text-primary)',
            }}
          >
            {Object.entries(COMPARE_MEASURES).map(([id, m]) => (
              <option key={id} value={id}>
                {m.label}
              </option>
            ))}
          </select>

          <div
            className="inline-flex p-0.5 rounded-[4px] border"
            style={{
              backgroundColor: 'var(--bg-canvas)',
              borderColor: 'var(--border-rule)',
            }}
            role="tablist"
            aria-label="Distribution view type"
          >
            <button
              type="button"
              role="tab"
              aria-selected={chartType === 'histogram'}
              onClick={() => setChartType('histogram')}
              className="px-2.5 py-1 text-[12px] font-medium rounded-[3px] cursor-pointer"
              style={{
                backgroundColor: chartType === 'histogram' ? 'var(--accent)' : 'transparent',
                color: chartType === 'histogram' ? 'var(--accent-text)' : 'var(--text-secondary)',
              }}
            >
              Histogram
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={chartType === 'ecdf'}
              onClick={() => setChartType('ecdf')}
              className="px-2.5 py-1 text-[12px] font-medium rounded-[3px] cursor-pointer"
              style={{
                backgroundColor: chartType === 'ecdf' ? 'var(--accent)' : 'transparent',
                color: chartType === 'ecdf' ? 'var(--accent-text)' : 'var(--text-secondary)',
              }}
            >
              Empirical CDF
            </button>
          </div>
        </div>

        <div className="flex items-center gap-2 text-[12px]">
          <span style={{ color: 'var(--text-muted)' }}>Bins:</span>
          {[8, 12, 16].map((b) => (
            <button
              key={b}
              type="button"
              onClick={() => {
                setBinCount(b);
                setSelectedBin(null);
              }}
              aria-pressed={binCount === b}
              className="px-2 py-0.5 font-mono-tabular rounded-[3px] border cursor-pointer"
              style={{
                borderColor: binCount === b ? 'var(--accent)' : 'var(--border-rule)',
                color: binCount === b ? 'var(--accent)' : 'var(--text-secondary)',
              }}
            >
              {b}
            </button>
          ))}
        </div>
      </div>

      {/* Main Split: Transport Cohort Lanes + Bin Contributors Inspector */}
      <div className="grid grid-cols-1 xl:grid-cols-[1fr_360px] gap-5 items-start">
        <div className="space-y-4">
          {distributions.length === 0 ? (
            <div
              className="p-8 rounded-[6px] border text-center text-[13px]"
              style={{
                backgroundColor: 'var(--bg-panel)',
                borderColor: 'var(--border-rule)',
                color: 'var(--text-secondary)',
              }}
            >
              No observations available in the current capture for comparison.
            </div>
          ) : (
            distributions.map((dist) => {
              const color = protocolColorVar(dist.protocol);
              const maxProb = Math.max(
                0.15,
                ...dist.bins.map((b) => b.empiricalProbability)
              );

              return (
                <section
                  key={dist.protocol}
                  aria-label={`${protocolLabel(dist.protocol)} distribution lane`}
                  className="rounded-[6px] border overflow-hidden"
                  style={{
                    backgroundColor: 'var(--bg-panel)',
                    borderColor: 'var(--border-rule)',
                  }}
                >
                  {/* Cohort Lane Header & Statistical Summary */}
                  <div
                    className="px-4 py-3 border-b flex flex-wrap items-center justify-between gap-3"
                    style={{ borderColor: 'var(--border-rule)' }}
                  >
                    <div className="space-y-0.5">
                      <div className="flex flex-wrap items-center gap-2.5">
                        <ProtocolTag protocol={dist.protocol} />
                        <span className="font-mono-tabular text-[12px]">
                          n = {dist.eligibleCount} eligible
                        </span>
                        {dist.excludedCount > 0 && (
                          <span
                            className="font-mono-tabular text-[11.5px]"
                            style={{ color: 'var(--status-warn)' }}
                          >
                            · {dist.excludedCount} excluded
                          </span>
                        )}
                      </div>
                      <div
                        className="font-mono-tabular text-[11px]"
                        style={{ color: 'var(--text-muted)' }}
                      >
                        Units: {dist.units} · Boundary: {dist.timingBoundary} · Clock: {dist.clockSource}
                        {index?.syntheticLabel ? ' · Synthetic/Recorded dataset' : ''}
                      </div>
                    </div>

                    <div className="flex flex-wrap items-center gap-4 font-mono-tabular text-[12px]">
                      <div>
                        <span style={{ color: 'var(--text-muted)' }}>p50 </span>
                        <strong>{dist.medianMs !== null ? `${dist.medianMs.toFixed(1)} ms` : '—'}</strong>
                      </div>
                      <div>
                        <span style={{ color: 'var(--text-muted)' }}>p95 </span>
                        {dist.p95Ms !== null ? (
                          <strong>{dist.p95Ms.toFixed(1)} ms</strong>
                        ) : (
                          <span
                            className="text-[11px]"
                            style={{ color: 'var(--text-muted)' }}
                            title={dist.p95SuppressedReason}
                          >
                            Suppressed (n&lt;20)
                          </span>
                        )}
                      </div>
                      <div>
                        <span style={{ color: 'var(--text-muted)' }}>p99 </span>
                        {dist.p99Ms !== null ? (
                          <strong>{dist.p99Ms.toFixed(1)} ms</strong>
                        ) : (
                          <span
                            className="text-[11px]"
                            style={{ color: 'var(--text-muted)' }}
                            title={dist.p99SuppressedReason}
                          >
                            Suppressed (n&lt;100)
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Chart + Synchronized Observation Strip */}
                  <div className="px-4 py-3">
                    {dist.eligibleCount === 0 ? (
                      <div
                        className="py-6 text-center text-[12.5px] rounded-[4px] border border-dashed"
                        style={{
                          borderColor: 'var(--border-rule)',
                          color: 'var(--text-muted)',
                        }}
                      >
                        Unsupported timing for this measure — no eligible monotonic samples in cohort.
                      </div>
                    ) : (
                      <div className="overflow-x-auto">
                        <svg
                          viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT + STRIP_HEIGHT + 24}`}
                          className="w-full min-w-[480px] block"
                          role="img"
                          aria-label={`${protocolLabel(dist.protocol)} ${
                            chartType === 'histogram' ? 'histogram' : 'empirical CDF'
                          } with synchronized observation strip`}
                        >
                          {/* Horizontal reference gridlines */}
                          {[0, 0.25, 0.5, 0.75, 1].map((t) => {
                            const y = CHART_HEIGHT - 8 - t * (CHART_HEIGHT - 20);
                            const yLabel =
                              chartType === 'histogram'
                                ? `${Math.round(t * maxProb * 100)}%`
                                : `${Math.round(t * 100)}%`;
                            return (
                              <g key={t}>
                                <line
                                  x1={36}
                                  y1={y}
                                  x2={CHART_WIDTH - 20}
                                  y2={y}
                                  stroke="var(--grid-line)"
                                  strokeWidth={1}
                                />
                                <text
                                  x={32}
                                  y={y + 3}
                                  textAnchor="end"
                                  fontSize="9.5"
                                  fontFamily="var(--font-mono)"
                                  fill="var(--text-muted)"
                                >
                                  {yLabel}
                                </text>
                              </g>
                            );
                          })}

                          {/* Histogram Bars */}
                          {chartType === 'histogram' &&
                            dist.bins.map((bin) => {
                              const x1 = valToX(bin.startMs);
                              const x2 = valToX(bin.endMs);
                              const w = Math.max(4, x2 - x1 - 2);
                              const h =
                                (bin.empiricalProbability / maxProb) * (CHART_HEIGHT - 22);
                              const y = CHART_HEIGHT - 8 - h;
                              const isSelected =
                                selectedBin?.protocol === dist.protocol &&
                                selectedBin.bin.binIndex === bin.binIndex;

                              return (
                                <g
                                  key={bin.binIndex}
                                  role="button"
                                  tabIndex={bin.count > 0 ? 0 : -1}
                                  aria-label={`${protocolLabel(dist.protocol)} bin ${bin.startMs.toFixed(
                                    1
                                  )} to ${bin.endMs.toFixed(1)} ms: ${bin.count} observations (${(
                                    bin.empiricalProbability * 100
                                  ).toFixed(1)}%)`}
                                  onClick={() => {
                                    if (bin.count > 0) {
                                      setSelectedBin({ protocol: dist.protocol, bin });
                                    }
                                  }}
                                  onKeyDown={(e) => {
                                    if ((e.key === 'Enter' || e.key === ' ') && bin.count > 0) {
                                      e.preventDefault();
                                      setSelectedBin({ protocol: dist.protocol, bin });
                                    }
                                  }}
                                  className={bin.count > 0 ? 'cursor-pointer' : ''}
                                >
                                  <rect
                                    x={x1 + 1}
                                    y={bin.count > 0 ? Math.min(y, CHART_HEIGHT - 12) : CHART_HEIGHT - 8}
                                    width={w}
                                    height={bin.count > 0 ? Math.max(4, h) : 0}
                                    rx={2}
                                    fill={isSelected ? 'var(--accent)' : color}
                                    opacity={isSelected ? 1 : 0.78}
                                    stroke={isSelected ? 'var(--text-primary)' : 'none'}
                                    strokeWidth={isSelected ? 1.2 : 0}
                                  />
                                  {bin.count > 0 && w >= 18 && (
                                    <text
                                      x={x1 + 1 + w / 2}
                                      y={Math.max(10, y - 3)}
                                      textAnchor="middle"
                                      fontSize="9.5"
                                      fontFamily="var(--font-mono)"
                                      fill="var(--text-secondary)"
                                    >
                                      {bin.count}
                                    </text>
                                  )}
                                </g>
                              );
                            })}

                          {/* Empirical CDF Step Curve */}
                          {chartType === 'ecdf' && dist.ecdf.length > 0 && (
                            <g>
                              <path
                                d={dist.ecdf
                                  .map((pt, idx) => {
                                    const x = valToX(pt.valueMs);
                                    const y =
                                      CHART_HEIGHT -
                                      8 -
                                      pt.cumulativeProbability * (CHART_HEIGHT - 20);
                                    if (idx === 0) {
                                      return `M ${valToX(globalDomain.minMs)} ${CHART_HEIGHT - 8} L ${x} ${CHART_HEIGHT - 8} L ${x} ${y}`;
                                    }
                                    const prevY =
                                      CHART_HEIGHT -
                                      8 -
                                      dist.ecdf[idx - 1].cumulativeProbability *
                                        (CHART_HEIGHT - 20);
                                    return `L ${x} ${prevY} L ${x} ${y}`;
                                  })
                                  .join(' ')}
                                fill="none"
                                stroke={color}
                                strokeWidth={2}
                              />
                              {/* Clickable bin regions in ECDF mode too */}
                              {dist.bins.map((bin) => {
                                if (bin.count === 0) return null;
                                const x1 = valToX(bin.startMs);
                                const x2 = valToX(bin.endMs);
                                const isSelected =
                                  selectedBin?.protocol === dist.protocol &&
                                  selectedBin.bin.binIndex === bin.binIndex;
                                return (
                                  <rect
                                    key={bin.binIndex}
                                    x={x1}
                                    y={12}
                                    width={Math.max(4, x2 - x1)}
                                    height={CHART_HEIGHT - 20}
                                    fill={isSelected ? 'var(--accent-muted)' : 'transparent'}
                                    className="cursor-pointer"
                                    onClick={() =>
                                      setSelectedBin({ protocol: dist.protocol, bin })
                                    }
                                  />
                                );
                              })}
                            </g>
                          )}

                          {/* Synchronized Observation Strip directly aligned with x-axis */}
                          <line
                            x1={36}
                            y1={CHART_HEIGHT - 8}
                            x2={CHART_WIDTH - 20}
                            y2={CHART_HEIGHT - 8}
                            stroke="var(--border-strong)"
                            strokeWidth={1}
                          />
                          <rect
                            x={36}
                            y={CHART_HEIGHT - 2}
                            width={CHART_WIDTH - 56}
                            height={STRIP_HEIGHT - 4}
                            fill="var(--bg-canvas)"
                            rx={2}
                          />
                          {dist.observations.slice(0, 400).map((obs) => {
                            const cx = valToX(obs.valueMs);
                            const cy = CHART_HEIGHT + 8;
                            const inSelected =
                              selectedBin?.protocol === dist.protocol &&
                              selectedBin.bin.contributors.some((c) => c.id === obs.id);
                            return (
                              <line
                                key={obs.id}
                                x1={cx}
                                y1={cy - 5}
                                x2={cx}
                                y2={cy + 5}
                                stroke={inSelected ? 'var(--accent)' : color}
                                strokeWidth={inSelected ? 2.2 : 1.2}
                                opacity={inSelected ? 1 : 0.7}
                              />
                            );
                          })}

                          {/* X-axis tick labels */}
                          {[0, 0.25, 0.5, 0.75, 1].map((t) => {
                            const val =
                              globalDomain.minMs +
                              t * (globalDomain.maxMs - globalDomain.minMs);
                            const x = valToX(val);
                            return (
                              <text
                                key={t}
                                x={x}
                                y={CHART_HEIGHT + STRIP_HEIGHT + 12}
                                textAnchor={t === 0 ? 'start' : t === 1 ? 'end' : 'middle'}
                                fontSize="10"
                                fontFamily="var(--font-mono)"
                                fill="var(--text-muted)"
                              >
                                {val.toFixed(0)} ms
                              </text>
                            );
                          })}
                        </svg>
                      </div>
                    )}

                    {/* Excluded Timing Reasons */}
                    {dist.excludedCount > 0 && (
                      <div
                        className="mt-2 pt-2 border-t flex flex-wrap items-center gap-x-3 gap-y-1 text-[11.5px]"
                        style={{ borderColor: 'var(--border-rule)', color: 'var(--text-muted)' }}
                      >
                        <span className="font-medium" style={{ color: 'var(--text-secondary)' }}>
                          Excluded from measure:
                        </span>
                        {Object.entries(dist.excludedReasons).map(([reason, count]) => (
                          <span key={reason} className="font-mono-tabular">
                            {reason} ({count})
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </section>
              );
            })
          )}
        </div>

        {/* Right Panel: Selected Bin Contributors Drilldown */}
        <aside
          aria-label="Selected bin contributors"
          className="rounded-[6px] border overflow-hidden xl:sticky xl:top-4"
          style={{
            backgroundColor: 'var(--bg-panel)',
            borderColor: 'var(--border-rule)',
          }}
        >
          <div
            className="px-4 py-3 border-b flex items-center justify-between gap-2"
            style={{ borderColor: 'var(--border-rule)' }}
          >
            <h2 className="text-[13.5px] font-semibold">Bin contributors</h2>
            {selectedBin && (
              <button
                type="button"
                onClick={() => setSelectedBin(null)}
                aria-label="Clear selected bin"
                className="p-1 rounded-[4px] cursor-pointer"
                style={{ color: 'var(--text-muted)' }}
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          {!selectedBin ? (
            <div className="p-4 text-[12.5px] space-y-2" style={{ color: 'var(--text-secondary)' }}>
              <p>
                Click any histogram bar or ECDF band to inspect the exact contributing observations and jump directly to an owning correlation waterfall.
              </p>
              <p className="font-mono-tabular text-[11.5px]" style={{ color: 'var(--text-muted)' }}>
                Empirical probability = bin count / eligible samples. Tail percentiles suppress p95 below 20 and p99 below 100 eligible observations.
              </p>
            </div>
          ) : (
            <div className="divide-y max-h-[560px] overflow-y-auto" style={{ borderColor: 'var(--border-rule)' }}>
              <div className="px-4 py-2.5 text-[12px] font-mono-tabular" style={{ backgroundColor: 'var(--bg-canvas)' }}>
                <div className="flex items-center justify-between">
                  <ProtocolTag protocol={selectedBin.protocol} />
                  <span>
                    {selectedBin.bin.startMs.toFixed(1)}–{selectedBin.bin.endMs.toFixed(1)} ms
                  </span>
                </div>
                <div className="mt-1" style={{ color: 'var(--text-muted)' }}>
                  {selectedBin.bin.count} contributor{selectedBin.bin.count === 1 ? '' : 's'} · empirical P ={' '}
                  {(selectedBin.bin.empiricalProbability * 100).toFixed(1)}%
                </div>
              </div>

              {selectedBin.bin.contributors.map((obs) => (
                <div
                  key={obs.id}
                  className="px-4 py-2.5 flex items-center justify-between gap-2 hover:bg-[var(--bg-panel-hover)]"
                >
                  <div className="min-w-0">
                    <div className="font-mono-tabular text-[12.5px] font-medium truncate">
                      {obs.label}
                    </div>
                    <div className="font-mono-tabular text-[11px]" style={{ color: 'var(--text-muted)' }}>
                      {obs.valueMs.toFixed(1)} ms · {obs.clockSource}
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => onOpenGroup(obs.groupKey)}
                    aria-label={`Open correlation ${obs.groupShortId}`}
                    className="inline-flex items-center gap-1 px-2 py-1 text-[11.5px] font-medium rounded-[4px] border shrink-0 cursor-pointer"
                    style={{
                      borderColor: 'var(--accent)',
                      color: 'var(--accent)',
                    }}
                  >
                    <span>Open</span>
                    <ArrowUpRight className="w-3 h-3" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </aside>
      </div>
    </main>
  );
}
