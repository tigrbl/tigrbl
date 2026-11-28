import React from 'react';
import {
  RotateCcw,
  Search,
  SkipBack,
  SkipForward,
  X,
} from 'lucide-react';
import { formatUtcTime } from '../adapter/traceAdapter';
import { PROTOCOL_LABELS } from '../theme/tokens';
import {
  DatasetMode,
  FilterState,
  PrimaryProtocol,
  TraceSnapshot,
} from '../types/trace';
import { LiveStatusInfo } from '../hooks/useTraceLab';

interface FilterToolbarProps {
  mode: DatasetMode;
  filters: FilterState;
  onChangeFilters: React.Dispatch<React.SetStateAction<FilterState>>;
  onClearFilters: () => void;
  onSetTimeWindow: (fromMs: number | null, toMs: number | null) => void;
  availableKinds: string[];
  availableOutcomes: string[];
  availableSources: string[];
  domainMinMs: number;
  domainMaxMs: number;
  isPaused: boolean;
  liveStatus: LiveStatusInfo;
  snapshot: TraceSnapshot | null;
  replayCursorSeq: number | null;
  onChangeReplayCursor: (seq: number | null) => void;
}

export const FilterToolbar: React.FC<FilterToolbarProps> = ({
  mode,
  filters,
  onChangeFilters,
  onClearFilters,
  onSetTimeWindow,
  availableKinds,
  availableOutcomes,
  availableSources,
  domainMinMs,
  domainMaxMs,
  isPaused,
  liveStatus,
  snapshot,
  replayCursorSeq,
  onChangeReplayCursor,
}) => {
  const hasFilters =
    filters.protocols.length > 0 ||
    filters.kind !== 'all' ||
    filters.outcome !== 'all' ||
    filters.source !== 'all' ||
    filters.searchQuery.trim() !== '' ||
    filters.fromMs !== null ||
    filters.toMs !== null ||
    filters.cohortEventIds !== null ||
    filters.bucketFilter !== null;

  const minSeq = snapshot?.retained_range.min_sequence ?? 0;
  const maxSeq = snapshot?.retained_range.max_sequence ?? 0;
  const canStepReplay = (mode === 'recorded' || isPaused) && maxSeq > minSeq;

  const applyTimePreset = (preset: string) => {
    if (preset === 'all' || domainMaxMs <= domainMinMs) {
      onSetTimeWindow(null, null);
      return;
    }
    const span = domainMaxMs - domainMinMs;
    if (preset === 'first-half') {
      onSetTimeWindow(domainMinMs, domainMinMs + span * 0.5);
    } else if (preset === 'second-half') {
      onSetTimeWindow(domainMinMs + span * 0.5, domainMaxMs);
    } else if (preset === 'last-25') {
      onSetTimeWindow(domainMinMs + span * 0.75, domainMaxMs);
    }
  };

  const currentRangePreset =
    filters.fromMs === null && filters.toMs === null ? 'all' : 'custom';

  const stepReplay = (delta: number) => {
    if (!canStepReplay) return;
    const current = replayCursorSeq ?? maxSeq;
    const next = Math.max(minSeq, Math.min(maxSeq, current + delta));
    onChangeReplayCursor(next === maxSeq ? null : next);
  };

  return (
    <section
      aria-label="Trace filters and capture controls"
      className="border-b px-4 py-2 flex flex-col gap-2"
      style={{ backgroundColor: 'var(--panel)', borderColor: 'var(--border)' }}
    >
      {/* Primary 40px toolbar row */}
      <div className="min-h-[40px] flex flex-wrap items-center gap-2">
        {/* Time range selector */}
        <div className="flex items-center gap-1.5">
          <label htmlFor="time-range-select" className="sr-only">
            Time range
          </label>
          <select
            id="time-range-select"
            aria-label="Time range"
            value={currentRangePreset}
            onChange={(e) => applyTimePreset(e.target.value)}
            className="h-8 px-2 text-[13px] rounded-[4px] border cursor-pointer"
            style={{
              backgroundColor: 'var(--canvas)',
              color: 'var(--text-primary)',
              borderColor: 'var(--border)',
            }}
          >
            <option value="all">Full capture window</option>
            <option value="first-half">First 50% of window</option>
            <option value="second-half">Last 50% of window</option>
            <option value="last-25">Last 25% of window</option>
            {currentRangePreset === 'custom' && (
              <option value="custom">Custom zoomed range</option>
            )}
          </select>
        </div>

        {/* Protocol quick dropdown */}
        <div>
          <label htmlFor="protocol-filter-select" className="sr-only">
            Protocol filter
          </label>
          <select
            id="protocol-filter-select"
            aria-label="Protocol filter"
            value={filters.protocols.length === 1 ? filters.protocols[0] : filters.protocols.length > 1 ? 'multi' : 'all'}
            onChange={(e) => {
              const v = e.target.value;
              onChangeFilters((prev) => ({
                ...prev,
                protocols: v === 'all' ? [] : [v as PrimaryProtocol],
                bucketFilter: null,
              }));
            }}
            className="h-8 px-2 text-[13px] rounded-[4px] border cursor-pointer"
            style={{
              backgroundColor: 'var(--canvas)',
              color: 'var(--text-primary)',
              borderColor: 'var(--border)',
            }}
          >
            <option value="all">All protocols</option>
            <option value="rest">REST</option>
            <option value="http_jsonrpc">HTTP JSON-RPC</option>
            <option value="websocket">WebSocket</option>
            <option value="webtransport">WebTransport</option>
            {filters.protocols.length > 1 && (
              <option value="multi">{filters.protocols.length} protocols selected</option>
            )}
          </select>
        </div>

        {/* Event kind dropdown */}
        <div>
          <label htmlFor="kind-filter-select" className="sr-only">
            Event kind
          </label>
          <select
            id="kind-filter-select"
            aria-label="Event kind"
            value={filters.kind}
            onChange={(e) =>
              onChangeFilters((prev) => ({ ...prev, kind: e.target.value, bucketFilter: null }))
            }
            className="h-8 px-2 text-[13px] rounded-[4px] border max-w-[190px] cursor-pointer"
            style={{
              backgroundColor: 'var(--canvas)',
              color: 'var(--text-primary)',
              borderColor: 'var(--border)',
            }}
          >
            <option value="all">All event kinds</option>
            {availableKinds.map((k) => (
              <option key={k} value={k}>
                {k}
              </option>
            ))}
          </select>
        </div>

        {/* Outcome dropdown */}
        <div>
          <label htmlFor="outcome-filter-select" className="sr-only">
            Outcome filter
          </label>
          <select
            id="outcome-filter-select"
            aria-label="Outcome"
            value={filters.outcome}
            onChange={(e) =>
              onChangeFilters((prev) => ({ ...prev, outcome: e.target.value, bucketFilter: null }))
            }
            className="h-8 px-2 text-[13px] rounded-[4px] border cursor-pointer"
            style={{
              backgroundColor: 'var(--canvas)',
              color: 'var(--text-primary)',
              borderColor: 'var(--border)',
            }}
          >
            <option value="all">All outcomes</option>
            {availableOutcomes.map((o) => (
              <option key={o} value={o}>
                {o.replace('_', ' ')}
              </option>
            ))}
          </select>
        </div>

        {/* Source dropdown */}
        <div>
          <label htmlFor="source-filter-select" className="sr-only">
            Source filter
          </label>
          <select
            id="source-filter-select"
            aria-label="Source"
            value={filters.source}
            onChange={(e) =>
              onChangeFilters((prev) => ({ ...prev, source: e.target.value, bucketFilter: null }))
            }
            className="h-8 px-2 text-[13px] rounded-[4px] border cursor-pointer"
            style={{
              backgroundColor: 'var(--canvas)',
              color: 'var(--text-primary)',
              borderColor: 'var(--border)',
            }}
          >
            <option value="all">All sources</option>
            {availableSources.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>

        {/* Typed ID exact/prefix search */}
        <div className="relative w-full lg:w-auto lg:min-w-[240px] lg:flex-1">
          <Search
            size={15}
            strokeWidth={1.75}
            className="absolute left-2.5 top-1/2 -translate-y-1/2 pointer-events-none"
            style={{ color: 'var(--text-muted)' }}
            aria-hidden="true"
          />
          <input
            type="search"
            value={filters.searchQuery}
            onChange={(e) =>
              onChangeFilters((prev) => ({
                ...prev,
                searchQuery: e.target.value,
                bucketFilter: null,
              }))
            }
            placeholder="Find an ID (req, corr, inv, tx, sub, dg…)"
            aria-label="Find an ID or event"
            className="w-full h-8 pl-8 pr-3 text-[13px] font-mono-data rounded-[4px] border"
            style={{
              backgroundColor: 'var(--canvas)',
              color: 'var(--text-primary)',
              borderColor: 'var(--border)',
            }}
          />
        </div>

        {/* Right side: Replay virtual clock */}
        <div className="ml-auto flex items-center gap-2 empty:hidden">
          {canStepReplay && (
            <div
              className="flex items-center gap-1 border rounded-[4px] px-1.5 h-8"
              style={{ backgroundColor: 'var(--canvas)', borderColor: 'var(--border)' }}
              title="Step virtual replay clock through retained sequences"
            >
              <span className="text-[12px] px-1" style={{ color: 'var(--text-muted)' }}>
                Replay
              </span>
              <button
                type="button"
                onClick={() => stepReplay(-5)}
                aria-label="Step replay back 5 events"
                className="p-1 rounded hover:opacity-80 cursor-pointer"
                style={{ color: 'var(--text-primary)' }}
              >
                <SkipBack size={13} aria-hidden="true" />
              </button>
              <span className="text-[12px] font-mono-data px-1" style={{ color: 'var(--text-primary)' }}>
                #{replayCursorSeq ?? maxSeq}
              </span>
              <button
                type="button"
                onClick={() => stepReplay(5)}
                aria-label="Step replay forward 5 events"
                className="p-1 rounded hover:opacity-80 cursor-pointer"
                style={{ color: 'var(--text-primary)' }}
              >
                <SkipForward size={13} aria-hidden="true" />
              </button>
              {replayCursorSeq !== null && (
                <button
                  type="button"
                  onClick={() => onChangeReplayCursor(null)}
                  aria-label="Reset replay to end"
                  className="text-[11px] px-1 underline cursor-pointer"
                  style={{ color: 'var(--accent)' }}
                >
                  End
                </button>
              )}
            </div>
          )}

          {!liveStatus.autoFollow && mode === 'live' && (
            <button
              type="button"
              onClick={() => onSetTimeWindow(null, null)}
              className="h-8 px-2.5 text-[12px] rounded-[4px] border inline-flex items-center gap-1 whitespace-nowrap shrink-0 cursor-pointer"
              style={{
                backgroundColor: 'var(--canvas)',
                borderColor: 'var(--accent)',
                color: 'var(--accent)',
              }}
            >
              <RotateCcw size={13} aria-hidden="true" />
              Follow live edge
            </button>
          )}
        </div>
      </div>

      {/* Removable active filter chips */}
      {hasFilters && (
        <div className="flex flex-wrap items-center gap-1.5 pt-1 border-t" style={{ borderColor: 'var(--border)' }}>
          <span className="text-[12px] mr-1" style={{ color: 'var(--text-muted)' }}>
            Active filters:
          </span>

          {filters.protocols.map((p) => (
            <button
              key={p}
              type="button"
              onClick={() =>
                onChangeFilters((prev) => ({
                  ...prev,
                  protocols: prev.protocols.filter((x) => x !== p),
                }))
              }
              className="h-6 px-2 text-[12px] rounded-[4px] border inline-flex items-center gap-1.5 cursor-pointer"
              style={{
                backgroundColor: 'var(--selected-bg)',
                borderColor: 'var(--accent)',
                color: 'var(--text-primary)',
              }}
            >
              <span>Protocol: {PROTOCOL_LABELS[p]}</span>
              <X size={12} aria-hidden="true" />
            </button>
          ))}

          {filters.kind !== 'all' && (
            <button
              type="button"
              onClick={() => onChangeFilters((prev) => ({ ...prev, kind: 'all' }))}
              className="h-6 px-2 text-[12px] font-mono-data rounded-[4px] border inline-flex items-center gap-1.5 cursor-pointer"
              style={{
                backgroundColor: 'var(--surface-alt)',
                borderColor: 'var(--border)',
                color: 'var(--text-primary)',
              }}
            >
              <span>Kind: {filters.kind}</span>
              <X size={12} aria-hidden="true" />
            </button>
          )}

          {filters.outcome !== 'all' && (
            <button
              type="button"
              onClick={() => onChangeFilters((prev) => ({ ...prev, outcome: 'all' }))}
              className="h-6 px-2 text-[12px] rounded-[4px] border inline-flex items-center gap-1.5 cursor-pointer"
              style={{
                backgroundColor: 'var(--surface-alt)',
                borderColor: 'var(--border)',
                color: 'var(--text-primary)',
              }}
            >
              <span>Outcome: {filters.outcome}</span>
              <X size={12} aria-hidden="true" />
            </button>
          )}

          {filters.source !== 'all' && (
            <button
              type="button"
              onClick={() => onChangeFilters((prev) => ({ ...prev, source: 'all' }))}
              className="h-6 px-2 text-[12px] rounded-[4px] border inline-flex items-center gap-1.5 cursor-pointer"
              style={{
                backgroundColor: 'var(--surface-alt)',
                borderColor: 'var(--border)',
                color: 'var(--text-primary)',
              }}
            >
              <span>Source: {filters.source}</span>
              <X size={12} aria-hidden="true" />
            </button>
          )}

          {filters.searchQuery.trim() && (
            <button
              type="button"
              onClick={() => onChangeFilters((prev) => ({ ...prev, searchQuery: '' }))}
              className="h-6 px-2 text-[12px] font-mono-data rounded-[4px] border inline-flex items-center gap-1.5 cursor-pointer"
              style={{
                backgroundColor: 'var(--surface-alt)',
                borderColor: 'var(--border)',
                color: 'var(--text-primary)',
              }}
            >
              <span>ID: {filters.searchQuery.trim()}</span>
              <X size={12} aria-hidden="true" />
            </button>
          )}

          {(filters.fromMs !== null || filters.toMs !== null) && (
            <button
              type="button"
              onClick={() => onSetTimeWindow(null, null)}
              className="h-6 px-2 text-[12px] font-mono-data rounded-[4px] border inline-flex items-center gap-1.5 cursor-pointer"
              style={{
                backgroundColor: 'var(--surface-alt)',
                borderColor: 'var(--border)',
                color: 'var(--text-primary)',
              }}
            >
              <span>
                Window: {filters.fromMs !== null ? formatUtcTime(filters.fromMs) : 'start'} →{' '}
                {filters.toMs !== null ? formatUtcTime(filters.toMs) : 'end'}
              </span>
              <X size={12} aria-hidden="true" />
            </button>
          )}

          {filters.cohortEventIds && (
            <button
              type="button"
              onClick={() =>
                onChangeFilters((prev) => ({
                  ...prev,
                  cohortEventIds: null,
                  cohortLabel: null,
                }))
              }
              className="h-6 px-2 text-[12px] rounded-[4px] border inline-flex items-center gap-1.5 cursor-pointer"
              style={{
                backgroundColor: 'var(--selected-bg)',
                borderColor: 'var(--accent)',
                color: 'var(--text-primary)',
              }}
            >
              <span>
                Cohort: {filters.cohortLabel || `${filters.cohortEventIds.length} observations`}
              </span>
              <X size={12} aria-hidden="true" />
            </button>
          )}

          {filters.bucketFilter && (
            <button
              type="button"
              onClick={() => onChangeFilters((prev) => ({ ...prev, bucketFilter: null }))}
              className="h-6 px-2 text-[12px] font-mono-data rounded-[4px] border inline-flex items-center gap-1.5 cursor-pointer"
              style={{
                backgroundColor: 'var(--selected-bg)',
                borderColor: 'var(--accent)',
                color: 'var(--text-primary)',
              }}
            >
              <span>
                Bucket ({filters.bucketFilter.count} events)
              </span>
              <X size={12} aria-hidden="true" />
            </button>
          )}

          <button
            type="button"
            onClick={onClearFilters}
            className="ml-auto text-[12px] font-medium px-2 py-0.5 rounded-[4px] underline cursor-pointer"
            style={{ color: 'var(--accent)' }}
          >
            Clear filters
          </button>
        </div>
      )}
    </section>
  );
};
