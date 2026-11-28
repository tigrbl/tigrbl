import React, { useMemo, useState } from 'react';
import { ArrowUpRight, Play, Table2, X } from 'lucide-react';
import {
  computeLatencyDistributions,
  computeOutcomeBreakdown,
  computeWtLaneMix,
  formatUtcTime,
} from '../adapter/traceAdapter';
import { ThemePalette } from '../theme/tokens';
import {
  DensityId,
  DistributionChartMode,
  DistributionLaneResult,
  DistributionMeasure,
  DistributionYMode,
  NormalizedEvent,
  PrimaryProtocol,
  SelectionState,
} from '../types/trace';
import { EventTable } from './EventTable';
import { CorrelationLink } from './CorrelationLink';

interface DistributionViewProps {
  events: NormalizedEvent[];
  density: DensityId;
  themePalette: ThemePalette;
  selection: SelectionState | null;
  onSelect: (sel: SelectionState) => void;
  onFollowCorrelation?: (href: string) => void;
  onJumpToExplore: (eventIds: string[], label: string, protocol?: PrimaryProtocol) => void;
  isEmptyCapture: boolean;
  onRunAll?: () => void;
  onOpenRecordedSample: () => void;
}

export const DistributionView: React.FC<DistributionViewProps> = ({
  events,
  density,
  themePalette,
  selection,
  onSelect,
  onFollowCorrelation,
  onJumpToExplore,
  isEmptyCapture,
  onRunAll,
  onOpenRecordedSample,
}) => {
  const [measure, setMeasure] = useState<DistributionMeasure>('invocation_latency');
  const [chartMode, setChartMode] = useState<DistributionChartMode>('histogram');
  const [yMode, setYMode] = useState<DistributionYMode>('count');
  const [selectedBin, setSelectedBin] = useState<{
    laneKey: string;
    laneLabel: string;
    protocol: DistributionLaneResult['protocol'];
    binIndex: number;
    low: number;
    high: number;
    inclusiveUpper: boolean;
    eventIds: string[];
  } | null>(null);
  const [showTable, setShowTable] = useState(true);

  const isLatencyMeasure =
    measure === 'invocation_latency' ||
    measure === 'transaction_latency' ||
    measure === 'delivery_latency';

  const latencyResult = useMemo(() => {
    if (!isLatencyMeasure) return null;
    return computeLatencyDistributions(events, measure, 12);
  }, [events, isLatencyMeasure, measure]);

  const outcomeRows = useMemo(() => computeOutcomeBreakdown(events), [events]);
  const wtMixRows = useMemo(() => computeWtLaneMix(events), [events]);

  const cohortEvents = useMemo(() => {
    if (!selectedBin) return events;
    const set = new Set(selectedBin.eventIds);
    return events.filter((e) => set.has(e.id));
  }, [events, selectedBin]);

  const handleMeasureChange = (next: DistributionMeasure) => {
    setMeasure(next);
    setSelectedBin(null);
  };

  if (isEmptyCapture) {
    return (
      <section
        aria-label="Empty distribution view"
        className="rounded-[5px] border px-6 py-12 flex flex-col items-center text-center gap-4"
        style={{ backgroundColor: 'var(--panel)', borderColor: 'var(--border)' }}
      >
        <div className="max-w-lg space-y-2">
          <h2 className="text-[16px] font-semibold" style={{ color: 'var(--text-primary)' }}>
            No observations available for distributions
          </h2>
          <p className="text-[13px]" style={{ color: 'var(--text-muted)' }}>
            {onRunAll
              ? 'Run the live scenario or open a recorded sample to explore distributions.'
              : 'Generate traffic in a monitored app or open a recorded sample to explore distributions.'}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2.5">
          {onRunAll && <button
            type="button"
            onClick={onRunAll}
            className="h-9 px-4 text-[14px] font-medium rounded-[5px] inline-flex items-center gap-2 cursor-pointer"
            style={{ backgroundColor: 'var(--accent)', color: 'var(--accent-contrast)' }}
          >
            <Play size={14} aria-hidden="true" />
            Run all transports
          </button>}
          <button
            type="button"
            onClick={onOpenRecordedSample}
            className="h-9 px-4 text-[14px] font-medium rounded-[5px] border cursor-pointer"
            style={{
              backgroundColor: 'var(--canvas)',
              borderColor: 'var(--border)',
              color: 'var(--text-primary)',
            }}
          >
            Open recorded sample
          </button>
        </div>
      </section>
    );
  }

  // Time span for observation strips
  const minT = events.length > 0 ? events[0].atMs : 0;
  const maxT = events.length > 0 ? Math.max(minT + 1, events[events.length - 1].atMs) : 1;

  return (
    <div className="space-y-4">
      {/* Measure & Display Mode Toolbar */}
      <section
        aria-label="Distribution controls"
        className="rounded-[5px] border px-3.5 py-2.5 flex flex-wrap items-center justify-between gap-3"
        style={{ backgroundColor: 'var(--panel)', borderColor: 'var(--border)' }}
      >
        <div className="flex flex-wrap items-center gap-2">
          <label htmlFor="dist-measure-select" className="text-[12px] font-medium" style={{ color: 'var(--text-muted)' }}>
            Measure
          </label>
          <select
            id="dist-measure-select"
            value={measure}
            onChange={(e) => handleMeasureChange(e.target.value as DistributionMeasure)}
            className="h-8 px-2.5 text-[13px] rounded-[4px] border cursor-pointer"
            style={{
              backgroundColor: 'var(--canvas)',
              color: 'var(--text-primary)',
              borderColor: 'var(--border)',
            }}
          >
            <option value="invocation_latency">Invocation latency (ms)</option>
            <option value="transaction_latency">Database transaction latency (ms)</option>
            <option value="delivery_latency">Broker delivery latency (ms)</option>
            <option value="outcome_breakdown">Outcome breakdown by protocol</option>
            <option value="wt_lane_mix">WebTransport stream &amp; datagram mix</option>
          </select>

          {isLatencyMeasure && (
            <>
              {/* Histogram vs Empirical CDF */}
              <div
                className="inline-flex rounded-[4px] border overflow-hidden"
                style={{ borderColor: 'var(--border)' }}
                role="group"
                aria-label="Distribution curve type"
              >
                <button
                  type="button"
                  onClick={() => setChartMode('histogram')}
                  aria-pressed={chartMode === 'histogram'}
                  className="h-8 px-2.5 text-[12px] font-medium cursor-pointer"
                  style={{
                    backgroundColor:
                      chartMode === 'histogram' ? 'var(--selected-bg)' : 'var(--canvas)',
                    color:
                      chartMode === 'histogram' ? 'var(--text-primary)' : 'var(--text-muted)',
                  }}
                >
                  Histogram
                </button>
                <button
                  type="button"
                  onClick={() => setChartMode('cdf')}
                  aria-pressed={chartMode === 'cdf'}
                  className="h-8 px-2.5 text-[12px] font-medium border-l cursor-pointer"
                  style={{
                    borderColor: 'var(--border)',
                    backgroundColor: chartMode === 'cdf' ? 'var(--selected-bg)' : 'var(--canvas)',
                    color: chartMode === 'cdf' ? 'var(--text-primary)' : 'var(--text-muted)',
                  }}
                >
                  Empirical CDF
                </button>
              </div>

              {/* Count vs Empirical probability */}
              {chartMode === 'histogram' && (
                <div
                  className="inline-flex rounded-[4px] border overflow-hidden"
                  style={{ borderColor: 'var(--border)' }}
                  role="group"
                  aria-label="Vertical axis scale"
                >
                  <button
                    type="button"
                    onClick={() => setYMode('count')}
                    aria-pressed={yMode === 'count'}
                    className="h-8 px-2.5 text-[12px] font-medium cursor-pointer"
                    style={{
                      backgroundColor: yMode === 'count' ? 'var(--selected-bg)' : 'var(--canvas)',
                      color: yMode === 'count' ? 'var(--text-primary)' : 'var(--text-muted)',
                    }}
                  >
                    Count
                  </button>
                  <button
                    type="button"
                    onClick={() => setYMode('probability')}
                    aria-pressed={yMode === 'probability'}
                    className="h-8 px-2.5 text-[12px] font-medium border-l cursor-pointer"
                    style={{
                      borderColor: 'var(--border)',
                      backgroundColor:
                        yMode === 'probability' ? 'var(--selected-bg)' : 'var(--canvas)',
                      color: yMode === 'probability' ? 'var(--text-primary)' : 'var(--text-muted)',
                    }}
                  >
                    Empirical probability
                  </button>
                </div>
              )}
            </>
          )}
        </div>

        <div className="flex items-center gap-2 text-[12px]">
          {isLatencyMeasure && (
            <span className="font-mono-data hidden md:inline" style={{ color: 'var(--text-muted)' }}>
              Bins [low, high), final closed · Nearest-rank quantiles
            </span>
          )}
          <button
            type="button"
            onClick={() => setShowTable((v) => !v)}
            className="h-8 px-2.5 rounded-[4px] border inline-flex items-center gap-1.5 cursor-pointer row-hover"
            style={{ borderColor: 'var(--border)', color: 'var(--text-primary)' }}
          >
            <Table2 size={13} aria-hidden="true" />
            {showTable ? 'Hide table' : 'Show table'}
          </button>
        </div>
      </section>

      {/* Selected Bin Cohort Action Bar */}
      {selectedBin && (
        <div
          className="rounded-[5px] border px-3.5 py-2.5 flex flex-wrap items-center justify-between gap-3"
          style={{
            backgroundColor: 'var(--selected-bg)',
            borderColor: 'var(--accent)',
          }}
        >
          <div className="text-[13px]">
            <span className="font-semibold" style={{ color: 'var(--text-primary)' }}>
              Selected bin: {selectedBin.laneLabel}
            </span>{' '}
            <span className="font-mono-data" style={{ color: 'var(--text-primary)' }}>
              [{selectedBin.low}, {selectedBin.high}
              {selectedBin.inclusiveUpper ? ']' : ')'} ms
            </span>{' '}
            <span style={{ color: 'var(--text-muted)' }}>
              · {selectedBin.eventIds.length} matching{' '}
              {selectedBin.eventIds.length === 1 ? 'observation' : 'observations'}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => {
                const label = `${selectedBin.laneLabel} [${selectedBin.low}, ${selectedBin.high}${selectedBin.inclusiveUpper ? ']' : ')'} ms`;
                const proto =
                  selectedBin.protocol !== 'database'
                    ? (selectedBin.protocol as PrimaryProtocol)
                    : undefined;
                onJumpToExplore(selectedBin.eventIds, label, proto);
              }}
              className="h-8 px-3 text-[13px] font-medium rounded-[4px] inline-flex items-center gap-1.5 cursor-pointer"
              style={{ backgroundColor: 'var(--accent)', color: 'var(--accent-contrast)' }}
            >
              <span>Open cohort in Explore</span>
              <ArrowUpRight size={14} aria-hidden="true" />
            </button>
            <button
              type="button"
              onClick={() => setSelectedBin(null)}
              aria-label="Clear bin selection"
              className="h-8 px-2 text-[12px] rounded-[4px] border inline-flex items-center gap-1 cursor-pointer"
              style={{
                backgroundColor: 'var(--panel)',
                borderColor: 'var(--border)',
                color: 'var(--text-primary)',
              }}
            >
              <X size={13} aria-hidden="true" />
              Clear
            </button>
          </div>
        </div>
      )}

      {/* Latency Distribution Karyogram Rows */}
      {isLatencyMeasure && latencyResult && (
        <div className="space-y-3">
          {latencyResult.lanes.map((lane) => {
            const maxBarVal = Math.max(
              0.001,
              ...lane.bins.map((b) => (yMode === 'probability' ? b.probability : b.count))
            );
            const chartW = 460;
            const chartH = 136;
            const padL = 38;
            const padR = 14;
            const padT = 12;
            const padB = 26;
            const innerW = chartW - padL - padR;
            const innerH = chartH - padT - padB;
            const barW = innerW / lane.bins.length;

            const stripW = 340;
            const stripH = 136;
            const valSpan = Math.max(1, latencyResult.sharedMax - latencyResult.sharedMin);

            const selectedSet =
              selectedBin && selectedBin.laneKey === lane.key
                ? new Set(selectedBin.eventIds)
                : null;

            return (
              <section
                key={lane.key}
                aria-label={`${lane.label} ${measure.replace('_', ' ')} distribution`}
                className="rounded-[5px] border overflow-hidden"
                style={{ backgroundColor: 'var(--panel)', borderColor: 'var(--border)' }}
              >
                {/* Lane Header: Title, Unit, Scope, Eligible & Excluded Counts */}
                <div
                  className="px-3.5 py-2 border-b flex flex-wrap items-center justify-between gap-2"
                  style={{ borderColor: 'var(--border)' }}
                >
                  <div className="flex flex-wrap items-baseline gap-x-3 gap-y-0.5">
                    <h3 className="text-[15px] font-semibold" style={{ color: 'var(--text-primary)' }}>
                      {lane.label}
                    </h3>
                    <span className="font-mono-data text-[12px]" style={{ color: 'var(--text-muted)' }}>
                      unit: {lane.unit} · boundary: {lane.timingBoundary}
                    </span>
                  </div>

                  <div className="flex flex-wrap items-center gap-3 text-[12px] font-mono-data">
                    <span style={{ color: 'var(--text-primary)' }}>
                      n = {lane.eligibleCount} eligible
                    </span>
                    {lane.excludedCount > 0 && (
                      <span
                        style={{ color: 'var(--role-partial)' }}
                        title={Object.entries(lane.excludedReasons)
                          .map(([r, c]) => `${c} × ${r}`)
                          .join('; ')}
                      >
                        {lane.excludedCount} excluded (
                        {Object.keys(lane.excludedReasons)[0] || 'missing duration'})
                      </span>
                    )}
                    {lane.quantiles.limitedSample && lane.eligibleCount > 0 && (
                      <span style={{ color: 'var(--role-partial)' }}>
                        Limited sample (n &lt; 10)
                      </span>
                    )}
                  </div>
                </div>

                {/* Aligned Body: Histogram / eCDF on Left + Observation-over-Time Strip on Right */}
                {lane.eligibleCount === 0 ? (
                  <div
                    className="px-4 py-8 text-center text-[13px]"
                    style={{ color: 'var(--text-muted)' }}
                  >
                    No producer-measured observations for {lane.label} in the active window.
                    {lane.excludedCount > 0 &&
                      ` (${lane.excludedCount} records excluded — sink capture timestamps only.)`}
                  </div>
                ) : (
                  <div className="p-3.5 grid grid-cols-1 lg:grid-cols-[minmax(0,1.25fr)_minmax(0,1fr)] gap-4 items-center">
                    {/* Left: Histogram or Empirical CDF */}
                    <div className="overflow-x-auto">
                      <svg
                        viewBox={`0 0 ${chartW} ${chartH}`}
                        className="w-full h-auto max-h-[168px] block"
                        role="img"
                        aria-label={`${lane.label} ${chartMode} from ${latencyResult.sharedMin} to ${latencyResult.sharedMax} ms`}
                      >
                        {/* Horizontal Gridlines */}
                        {[0, 0.5, 1].map((frac) => {
                          const y = padT + innerH * (1 - frac);
                          const label =
                            chartMode === 'cdf'
                              ? `${Math.round(frac * 100)}%`
                              : yMode === 'probability'
                                ? `${Math.round(frac * maxBarVal * 100)}%`
                                : String(Math.round(frac * maxBarVal));
                          return (
                            <g key={frac}>
                              <line
                                x1={padL}
                                y1={y}
                                x2={chartW - padR}
                                y2={y}
                                stroke={themePalette.gridMajor}
                              />
                              <text
                                x={padL - 6}
                                y={y + 3}
                                textAnchor="end"
                                fill={themePalette.textMuted}
                                fontSize={10}
                                fontFamily="IBM Plex Mono, monospace"
                              >
                                {label}
                              </text>
                            </g>
                          );
                        })}

                        {/* Histogram Bars OR Empirical CDF Step Line */}
                        {chartMode === 'histogram' ? (
                          lane.bins.map((bin) => {
                            const val = yMode === 'probability' ? bin.probability : bin.count;
                            const h = bin.count === 0 ? 2 : Math.max(3, (val / maxBarVal) * innerH);
                            const x = padL + bin.index * barW + 1.5;
                            const y = padT + innerH - h;
                            const isBinSelected =
                              selectedBin?.laneKey === lane.key &&
                              selectedBin.binIndex === bin.index;
                            const isEmptyBin = bin.count === 0;

                            return (
                              <g
                                key={bin.index}
                                role="button"
                                tabIndex={bin.count > 0 ? 0 : -1}
                                aria-label={`Bin ${bin.low} to ${bin.high} ms: ${bin.count} observations (${(bin.probability * 100).toFixed(1)}%)`}
                                onClick={() => {
                                  if (bin.count === 0) return;
                                  setSelectedBin(
                                    isBinSelected
                                      ? null
                                      : {
                                          laneKey: lane.key,
                                          laneLabel: lane.label,
                                          protocol: lane.protocol,
                                          binIndex: bin.index,
                                          low: bin.low,
                                          high: bin.high,
                                          inclusiveUpper: bin.inclusiveUpper,
                                          eventIds: bin.eventIds,
                                        }
                                  );
                                }}
                                onKeyDown={(e) => {
                                  if ((e.key === 'Enter' || e.key === ' ') && bin.count > 0) {
                                    e.preventDefault();
                                    setSelectedBin(
                                      isBinSelected
                                        ? null
                                        : {
                                            laneKey: lane.key,
                                            laneLabel: lane.label,
                                            protocol: lane.protocol,
                                            binIndex: bin.index,
                                            low: bin.low,
                                            high: bin.high,
                                            inclusiveUpper: bin.inclusiveUpper,
                                            eventIds: bin.eventIds,
                                          }
                                    );
                                  }
                                }}
                                className={bin.count > 0 ? 'cursor-pointer' : ''}
                              >
                                <rect
                                  x={x}
                                  y={y}
                                  width={Math.max(4, barW - 3)}
                                  height={h}
                                  rx={1.5}
                                  fill={
                                    isEmptyBin
                                      ? themePalette.border
                                      : isBinSelected
                                        ? themePalette.accent
                                        : themePalette.roles.carrier
                                  }
                                  opacity={isEmptyBin ? 0.35 : isBinSelected ? 1 : 0.82}
                                  stroke={isBinSelected ? themePalette.textPrimary : 'none'}
                                  strokeWidth={isBinSelected ? 1.2 : 0}
                                >
                                  <title>
                                    [{bin.low}, {bin.high}
                                    {bin.inclusiveUpper ? ']' : ')'} ms: {bin.count} (
                                    {(bin.probability * 100).toFixed(1)}%)
                                  </title>
                                </rect>
                              </g>
                            );
                          })
                        ) : (
                          <>
                            <polyline
                              fill="none"
                              stroke={themePalette.accent}
                              strokeWidth={2}
                              points={lane.bins
                                .map((b) => {
                                  const x = padL + (b.index + 1) * barW;
                                  const y = padT + innerH * (1 - b.cumulativeProbability);
                                  return `${x},${y}`;
                                })
                                .join(' ')}
                            />
                            {lane.bins.map((b) => {
                              const x = padL + (b.index + 1) * barW;
                              const y = padT + innerH * (1 - b.cumulativeProbability);
                              const isBinSelected =
                                selectedBin?.laneKey === lane.key &&
                                selectedBin.binIndex === b.index;
                              return (
                                <circle
                                  key={b.index}
                                  cx={x}
                                  cy={y}
                                  r={isBinSelected ? 5 : 3}
                                  fill={
                                    b.count > 0 ? themePalette.accent : themePalette.panel
                                  }
                                  stroke={themePalette.accent}
                                  strokeWidth={1.5}
                                  className={b.count > 0 ? 'cursor-pointer' : ''}
                                  onClick={() => {
                                    if (b.count === 0) return;
                                    setSelectedBin(
                                      isBinSelected
                                        ? null
                                        : {
                                            laneKey: lane.key,
                                            laneLabel: lane.label,
                                            protocol: lane.protocol,
                                            binIndex: b.index,
                                            low: b.low,
                                            high: b.high,
                                            inclusiveUpper: b.inclusiveUpper,
                                            eventIds: b.eventIds,
                                          }
                                    );
                                  }}
                                >
                                  <title>
                                    ≤ {b.high} ms: {(b.cumulativeProbability * 100).toFixed(1)}% (bin
                                    n={b.count})
                                  </title>
                                </circle>
                              );
                            })}
                          </>
                        )}

                        {/* Shared X-Axis Labels */}
                        {[0, 0.25, 0.5, 0.75, 1].map((frac) => {
                          const x = padL + frac * innerW;
                          const val = latencyResult.sharedMin + frac * valSpan;
                          return (
                            <text
                              key={frac}
                              x={x}
                              y={chartH - 6}
                              textAnchor={frac === 0 ? 'start' : frac === 1 ? 'end' : 'middle'}
                              fill={themePalette.textMuted}
                              fontSize={10}
                              fontFamily="IBM Plex Mono, monospace"
                            >
                              {val.toFixed(1)} ms
                            </text>
                          );
                        })}
                      </svg>
                    </div>

                    {/* Right: Aligned Observation-over-Time Strip */}
                    <div className="overflow-x-auto">
                      <svg
                        viewBox={`0 0 ${stripW} ${stripH}`}
                        className="w-full h-auto max-h-[168px] block"
                        role="img"
                        aria-label={`${lane.label} individual observations over time`}
                      >
                        <rect
                          x={34}
                          y={padT}
                          width={stripW - 46}
                          height={innerH}
                          fill={themePalette.canvas}
                          stroke={themePalette.border}
                          strokeWidth={0.75}
                          rx={3}
                        />
                        {[0, 0.5, 1].map((frac) => {
                          const y = padT + innerH * (1 - frac);
                          const v = latencyResult.sharedMin + frac * valSpan;
                          return (
                            <g key={frac}>
                              <line
                                x1={34}
                                y1={y}
                                x2={stripW - 12}
                                y2={y}
                                stroke={themePalette.gridMinor}
                              />
                              <text
                                x={30}
                                y={y + 3}
                                textAnchor="end"
                                fill={themePalette.textMuted}
                                fontSize={9.5}
                                fontFamily="IBM Plex Mono, monospace"
                              >
                                {v.toFixed(0)}
                              </text>
                            </g>
                          );
                        })}

                        {lane.observations.map((obs) => {
                          const nx = (obs.atMs - minT) / Math.max(1, maxT - minT);
                          const ny = (obs.value - latencyResult.sharedMin) / valSpan;
                          const cx = 38 + nx * (stripW - 54);
                          const cy = padT + innerH - ny * innerH;
                          const isHighlighted = selectedSet ? selectedSet.has(obs.eventId) : true;
                          const isSelectedEv =
                            selection?.type === 'event' && selection.id === obs.eventId;

                          return (
                            <circle
                              key={obs.eventId}
                              cx={cx}
                              cy={cy}
                              r={isSelectedEv ? 4.8 : isHighlighted ? 3.2 : 2.3}
                              fill={
                                obs.role === 'rejected'
                                  ? themePalette.roles.rejected
                                  : isHighlighted
                                    ? themePalette.accent
                                    : themePalette.textMuted
                              }
                              opacity={isHighlighted ? 0.92 : 0.25}
                              stroke={isSelectedEv ? themePalette.textPrimary : 'none'}
                              strokeWidth={1.5}
                              className="cursor-pointer"
                              onClick={() => onSelect({ type: 'event', id: obs.eventId })}
                            >
                              <title>
                                {obs.label}: {obs.value} ms at {formatUtcTime(obs.atMs)}
                              </title>
                            </circle>
                          );
                        })}

                        <text
                          x={34}
                          y={stripH - 6}
                          fill={themePalette.textMuted}
                          fontSize={9.5}
                          fontFamily="IBM Plex Mono, monospace"
                        >
                          {formatUtcTime(minT, false)}
                        </text>
                        <text
                          x={stripW - 12}
                          y={stripH - 6}
                          textAnchor="end"
                          fill={themePalette.textMuted}
                          fontSize={9.5}
                          fontFamily="IBM Plex Mono, monospace"
                        >
                          {formatUtcTime(maxT, false)}
                        </text>
                      </svg>
                    </div>
                  </div>
                )}

                {/* Quantile Strip obeying exact minimum display thresholds */}
                <div
                  className="px-3.5 py-2 border-t flex flex-wrap items-center gap-x-5 gap-y-1 text-[12px] font-mono-data"
                  style={{
                    borderColor: 'var(--border)',
                    backgroundColor: 'var(--canvas)',
                    color: 'var(--text-muted)',
                  }}
                >
                  <span>
                    p50:{' '}
                    <strong style={{ color: 'var(--text-primary)' }}>
                      {lane.quantiles.p50 !== null ? `${lane.quantiles.p50.toFixed(2)} ms` : '—'}
                    </strong>
                  </span>
                  <span title="Requires n >= 10 eligible observations">
                    p90:{' '}
                    <strong style={{ color: 'var(--text-primary)' }}>
                      {lane.quantiles.p90 !== null
                        ? `${lane.quantiles.p90.toFixed(2)} ms`
                        : 'n < 10'}
                    </strong>
                  </span>
                  <span title="Requires n >= 20 eligible observations">
                    p95:{' '}
                    <strong style={{ color: 'var(--text-primary)' }}>
                      {lane.quantiles.p95 !== null
                        ? `${lane.quantiles.p95.toFixed(2)} ms`
                        : 'n < 20'}
                    </strong>
                  </span>
                  <span title="Requires n >= 100 eligible observations">
                    p99:{' '}
                    <strong style={{ color: 'var(--text-primary)' }}>
                      {lane.quantiles.p99 !== null
                        ? `${lane.quantiles.p99.toFixed(2)} ms`
                        : 'n < 100'}
                    </strong>
                  </span>
                  <span>
                    max:{' '}
                    <strong style={{ color: 'var(--text-primary)' }}>
                      {lane.quantiles.max !== null ? `${lane.quantiles.max.toFixed(2)} ms` : '—'}
                    </strong>
                  </span>
                </div>
              </section>
            );
          })}
        </div>
      )}

      {/* Outcome Breakdown View */}
      {measure === 'outcome_breakdown' && (
        <section
          aria-label="Protocol outcome breakdown"
          className="rounded-[5px] border overflow-hidden"
          style={{ backgroundColor: 'var(--panel)', borderColor: 'var(--border)' }}
        >
          <div
            className="px-3.5 py-2.5 border-b flex items-baseline justify-between gap-2"
            style={{ borderColor: 'var(--border)' }}
          >
            <h3 className="text-[15px] font-semibold" style={{ color: 'var(--text-primary)' }}>
              Outcome counts &amp; known-outcome denominators
            </h3>
            <span className="font-mono-data text-[12px]" style={{ color: 'var(--text-muted)' }}>
              Unknown outcomes preserved separately
            </span>
          </div>

          <div className="divide-y" style={{ borderColor: 'var(--border)' }}>
            {outcomeRows.map((row) => {
              const okTotal = row.counts.ok + row.counts.committed + row.counts.delivered;
              const errTotal = row.counts.rejected + row.counts.failed + row.counts.rolled_back;
              const openTotal = row.counts.open;
              const unkTotal = row.counts.unknown;
              const denom = Math.max(1, row.total);

              return (
                <div key={row.protocol} className="px-3.5 py-3 space-y-2">
                  <div className="flex flex-wrap items-center justify-between gap-2 text-[13px]">
                    <span className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                      {row.label}
                    </span>
                    <span className="font-mono-data text-[12px]" style={{ color: 'var(--text-muted)' }}>
                      {row.total} total · {row.knownDenominator} known denominator · {okTotal} ok ·{' '}
                      {errTotal} rejected/failed · {openTotal} open · {unkTotal} unknown
                    </span>
                  </div>

                  <div
                    className="h-4 rounded-[3px] overflow-hidden flex"
                    style={{ backgroundColor: 'var(--surface-alt)' }}
                    role="img"
                    aria-label={`${row.label}: ${okTotal} successful, ${errTotal} rejected or failed, ${openTotal} open, ${unkTotal} unknown`}
                  >
                    {okTotal > 0 && (
                      <div
                        style={{
                          width: `${(okTotal / denom) * 100}%`,
                          backgroundColor: 'var(--role-success)',
                        }}
                      />
                    )}
                    {openTotal > 0 && (
                      <div
                        style={{
                          width: `${(openTotal / denom) * 100}%`,
                          backgroundColor: 'var(--role-partial)',
                        }}
                      />
                    )}
                    {errTotal > 0 && (
                      <div
                        style={{
                          width: `${(errTotal / denom) * 100}%`,
                          backgroundColor: 'var(--role-rejected)',
                        }}
                      />
                    )}
                    {unkTotal > 0 && (
                      <div
                        style={{
                          width: `${(unkTotal / denom) * 100}%`,
                          backgroundColor: 'var(--role-neutral)',
                        }}
                      />
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* WebTransport Lane Mix View */}
      {measure === 'wt_lane_mix' && (
        <section
          aria-label="WebTransport stream and datagram lane mix"
          className="rounded-[5px] border overflow-hidden"
          style={{ backgroundColor: 'var(--panel)', borderColor: 'var(--border)' }}
        >
          <div
            className="px-3.5 py-2.5 border-b flex items-baseline justify-between gap-2"
            style={{ borderColor: 'var(--border)' }}
          >
            <h3 className="text-[15px] font-semibold" style={{ color: 'var(--text-primary)' }}>
              WebTransport session stream &amp; datagram mix
            </h3>
            <span className="font-mono-data text-[12px]" style={{ color: 'var(--text-muted)' }}>
              Direction, rejections, rebinds &amp; distinct datagram IDs
            </span>
          </div>

          {wtMixRows.length === 0 ? (
            <div className="px-4 py-8 text-center text-[13px]" style={{ color: 'var(--text-muted)' }}>
              No WebTransport session events observed in the active window.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-[13px]">
                <thead>
                  <tr
                    className="border-b text-[12px]"
                    style={{
                      backgroundColor: 'var(--surface-alt)',
                      borderColor: 'var(--border)',
                      color: 'var(--text-muted)',
                    }}
                  >
                    <th className="py-2 px-3.5 font-medium">Transport session</th>
                    <th className="py-2 px-3.5 font-medium">Session correlation</th>
                    <th className="py-2 px-3.5 font-medium text-right">Bidi streams</th>
                    <th className="py-2 px-3.5 font-medium text-right">Uni streams</th>
                    <th className="py-2 px-3.5 font-medium text-right">Rejections</th>
                    <th className="py-2 px-3.5 font-medium text-right">Datagrams (in / out)</th>
                    <th className="py-2 px-3.5 font-medium text-right">Distinct dg IDs</th>
                    <th className="py-2 px-3.5 font-medium text-right">UDP rebinds</th>
                  </tr>
                </thead>
                <tbody className="divide-y font-mono-data text-[12px]" style={{ borderColor: 'var(--border)' }}>
                  {wtMixRows.map((row) => (
                    <tr key={row.sessionId} className="row-hover">
                      <td className="py-2.5 px-3.5">
                        <button
                          type="button"
                          onClick={() =>
                            onSelect({ type: 'entity', id: `transport_session:${row.sessionId}` })
                          }
                          className="hover:underline cursor-pointer"
                          style={{ color: 'var(--accent)' }}
                        >
                          {row.sessionId}
                        </button>
                      </td>
                      <td className="py-2.5 px-3.5" style={{ color: 'var(--text-muted)' }}>
                        {row.correlationId && onFollowCorrelation ? (
                          <CorrelationLink id={row.correlationId} sequence={row.correlationSequence} onFollowCorrelation={onFollowCorrelation} />
                        ) : row.correlationId ?? '—'}
                      </td>
                      <td className="py-2.5 px-3.5 text-right">{row.streamOpenedBidi}</td>
                      <td className="py-2.5 px-3.5 text-right">{row.streamOpenedUni}</td>
                      <td
                        className="py-2.5 px-3.5 text-right font-semibold"
                        style={{
                          color:
                            row.streamRejected > 0 ? 'var(--role-rejected)' : 'var(--text-muted)',
                        }}
                      >
                        {row.streamRejected}
                      </td>
                      <td className="py-2.5 px-3.5 text-right">
                        {row.datagramsInbound} / {row.datagramsOutbound}
                      </td>
                      <td className="py-2.5 px-3.5 text-right">{row.distinctDatagramIds}</td>
                      <td
                        className="py-2.5 px-3.5 text-right"
                        style={{
                          color: row.rebinds > 0 ? 'var(--accent)' : 'var(--text-muted)',
                        }}
                      >
                        {row.rebinds}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}

      {/* Synchronized Accessible Event Table */}
      {showTable && (
        <EventTable
          events={cohortEvents}
          onFollowCorrelation={onFollowCorrelation}
          density={density}
          selection={selection}
          onSelect={onSelect}
          bucketFilter={null}
          onClearBucketFilter={() => {}}
          title={
            selectedBin
              ? `Matching observations in [${selectedBin.low}, ${selectedBin.high}${selectedBin.inclusiveUpper ? ']' : ')'} ms`
              : 'Observations in active window'
          }
          compact
        />
      )}
    </div>
  );
};
