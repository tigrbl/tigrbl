import React, { useMemo, useState } from 'react';
import {
  ArrowUpRight,
  Pin,
  Search,
} from 'lucide-react';
import { buildKaryogram } from '../core/analytics';
import {
  formatUtcTime,
  protocolLabel,
  scopeLabel,
  searchCorrelations,
  httpStatusLabel,
} from '../core/correlationEngine';
import type {
  CorrelationGroup,
  CorrelationIndex,
  KaryogramBucket,
  KaryogramRow,
  SearchIdType,
  TransportProtocol,
} from '../core/types';
import { KaryogramPanel } from '../components/KaryogramPanel';
import { OutcomeLabel, ProtocolTag } from '../components/StatusIndicator';

interface CorrelationIndexViewProps {
  index: CorrelationIndex | null;
  loading: boolean;
  errorMessage: string | null;
  query: string;
  idType: SearchIdType;
  protocolFilter: TransportProtocol | 'all';
  showUnassigned: boolean;
  pinnedKeys: Set<string>;
  rowHeight: number;
  onQueryChange: (q: string) => void;
  onIdTypeChange: (t: SearchIdType) => void;
  onProtocolFilterChange: (p: TransportProtocol | 'all') => void;
  onToggleUnassigned: (show: boolean) => void;
  onOpenGroup: (groupKey: string) => void;
  onTogglePin: (groupKey: string) => void;
  onOpenCompare: () => void;
}

const ID_TYPE_OPTIONS: Array<{ value: SearchIdType; label: string; hint: string }> = [
  { value: 'correlation_id', label: 'Correlation ID (default)', hint: 'Paste correlation ID or prefix req:, rpc:, stream:, quic:, tx:' },
  { value: 'request_id', label: 'Request ID', hint: 'Search HTTP/RPC request_id' },
  { value: 'rpc_id', label: 'RPC Wire ID', hint: 'Search JSON-RPC wire rpc_id' },
  { value: 'stream_correlation_id', label: 'Stream Correlation ID', hint: 'Search WebTransport stream_correlation_id' },
  { value: 'quic_connection_id', label: 'QUIC Connection ID', hint: 'Search WebTransport quic_connection_id' },
  { value: 'transport_session_id', label: 'Transport Session ID', hint: 'Search WS/WT transport_session_id' },
  { value: 'transaction_id', label: 'DB Transaction Key', hint: 'Search engine_session_id::transaction_id' },
  { value: 'invocation_id', label: 'Invocation ID', hint: 'Search runtime invocation_id' },
];

const PAGE_SIZE = 60;

export function CorrelationIndexView({
  index,
  loading,
  errorMessage,
  query,
  idType,
  protocolFilter,
  showUnassigned,
  pinnedKeys,
  rowHeight,
  onQueryChange,
  onIdTypeChange,
  onProtocolFilterChange,
  onToggleUnassigned,
  onOpenGroup,
  onTogglePin,
  onOpenCompare,
}: CorrelationIndexViewProps) {
  const [selectedBucket, setSelectedBucket] = useState<{
    rowKey: string;
    bucketIndex: number;
    bucket: KaryogramBucket;
    row: KaryogramRow;
  } | null>(null);
  const [outcomeFilter, setOutcomeFilter] = useState<'all' | 'issues'>('all');
  const [visibleLimit, setVisibleLimit] = useState(PAGE_SIZE);

  // Search results & disambiguation candidates
  const searchResult = useMemo(() => {
    if (!index || !query.trim()) return null;
    return searchCorrelations(index, query, idType);
  }, [index, query, idType]);

  // Karyogram across retained capture (respecting protocol filter so it aligns with table)
  const karyogramData = useMemo(() => {
    if (!index || index.groups.length === 0) return null;
    const baseGroups =
      protocolFilter === 'all'
        ? index.groups
        : index.groups.filter((g) => g.protocol === protocolFilter);
    return buildKaryogram(baseGroups, index.minRecordedAtMs, index.maxRecordedAtMs, 32);
  }, [index, protocolFilter]);

  // Filtered correlation rows
  const filteredGroups = useMemo<CorrelationGroup[]>(() => {
    if (!index) return [];
    let list = searchResult ? searchResult.candidates.map((c) => c.group) : index.groups;

    if (protocolFilter !== 'all') {
      list = list.filter((g) => g.protocol === protocolFilter);
    }
    if (outcomeFilter === 'issues') {
      list = list.filter((g) => g.outcomeSummary !== 'ok');
    }
    if (selectedBucket) {
      const allowed = new Set(selectedBucket.bucket.groupKeys);
      list = list.filter((g) => allowed.has(g.groupKey));
    }
    return list;
  }, [index, searchResult, protocolFilter, outcomeFilter, selectedBucket]);

  const displayedGroups = filteredGroups.slice(0, visibleLimit);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchResult && searchResult.candidates.length === 1 && !searchResult.needsDisambiguation) {
      onOpenGroup(searchResult.candidates[0].groupKey);
    }
  };

  const activeHint =
    ID_TYPE_OPTIONS.find((o) => o.value === idType)?.hint ??
    'Paste correlation ID';

  return (
    <main className="flex-1 overflow-y-auto px-4 sm:px-6 py-5 max-w-[1600px] w-full mx-auto space-y-5">
      {errorMessage && (
        <div
          role="alert"
          className="px-4 py-2.5 rounded-[5px] border text-[12.5px]"
          style={{
            backgroundColor: 'var(--bg-panel)',
            borderColor: 'var(--status-err)',
            color: 'var(--status-err)',
          }}
        >
          {errorMessage} — retaining last verified trace snapshot.
        </div>
      )}

      {/* Page Title & Synthetic / Capture Context */}
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1
            className="font-display text-[32px] leading-[1.15] tracking-[-0.01em]"
            style={{ textWrap: 'balance' }}
          >
            Correlation index
          </h1>
          <div
            className="mt-1 flex flex-wrap items-center gap-x-2.5 gap-y-1 text-[12.5px]"
            style={{ color: 'var(--text-secondary)' }}
          >
            {index ? (
              <>
                <span className="font-mono-tabular">
                  {index.mode === 'recorded' ? `capture ${index.captureId}`
                    : query.trim() ? 'Persisted Tigrbl traces' : 'Recent persisted correlations'}
                </span>
                <span aria-hidden="true">·</span>
                <span className="font-mono-tabular">
                  {index.groups.length.toLocaleString()} correlations
                </span>
                <span aria-hidden="true">·</span>
                <span className="font-mono-tabular">
                  {index.retainedCount.toLocaleString()} event rows
                  {index.bounded && ' · bounded evidence'}
                </span>
                {index.evictedCount > 0 && (
                  <>
                    <span aria-hidden="true">·</span>
                    <span className="font-mono-tabular" style={{ color: 'var(--status-warn)' }}>
                      {index.evictedCount.toLocaleString()} evicted
                    </span>
                  </>
                )}
                {index.syntheticLabel && (
                  <>
                    <span aria-hidden="true">·</span>
                    <span className="font-medium" style={{ color: 'var(--accent)' }}>
                      {index.syntheticLabel}
                    </span>
                  </>
                )}
              </>
            ) : (
              <span>Loading trace capture…</span>
            )}
          </div>
        </div>

        {/* Pinned Compare shortcut */}
        {pinnedKeys.size > 0 && (
          <button
            type="button"
            onClick={onOpenCompare}
            className="inline-flex items-center gap-2 px-3 py-2 text-[12.5px] font-medium rounded-[5px] border cursor-pointer hover:opacity-90 whitespace-nowrap"
            style={{
              borderColor: 'var(--accent)',
              color: 'var(--accent)',
              backgroundColor: 'var(--accent-muted)',
            }}
          >
            <Pin className="w-3.5 h-3.5" />
            <span>Compare {pinnedKeys.size} pinned</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      {/* Search Bar & Typed Secondary ID Selector */}
      <form
        onSubmit={handleSearchSubmit}
        className="grid grid-cols-1 md:grid-cols-[1fr_220px_auto] gap-2 items-center"
        role="search"
        aria-label="Search correlations by ID"
      >
        <div className="relative">
          <Search
            className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none"
            style={{ color: 'var(--text-muted)' }}
            aria-hidden="true"
          />
          <input
            type="search"
            value={query}
            onChange={(e) => {
              onQueryChange(e.target.value);
              setVisibleLimit(PAGE_SIZE);
            }}
            placeholder={activeHint}
            aria-label="Paste correlation ID or search capture"
            className="w-full pl-9 pr-3 py-2 text-[13px] font-mono-tabular rounded-[5px] border min-h-[40px]"
            style={{
              backgroundColor: 'var(--bg-panel)',
              borderColor: 'var(--border-strong)',
              color: 'var(--text-primary)',
            }}
          />
        </div>

        <label className="sr-only" htmlFor="search-id-type">
          Identifier type
        </label>
        <select
          id="search-id-type"
          value={idType}
          onChange={(e) => onIdTypeChange(e.target.value as SearchIdType)}
          aria-label="Search identifier type"
          className="px-3 py-2 text-[12.5px] rounded-[5px] border min-h-[40px] cursor-pointer"
          style={{
            backgroundColor: 'var(--bg-panel)',
            borderColor: 'var(--border-rule)',
            color: 'var(--text-primary)',
          }}
        >
          {ID_TYPE_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>

        {query.trim() && (
          <button
            type="button"
            onClick={() => onQueryChange('')}
            className="px-3 py-2 text-[12.5px] rounded-[5px] border cursor-pointer min-h-[40px] whitespace-nowrap"
            style={{
              borderColor: 'var(--border-rule)',
              color: 'var(--text-secondary)',
            }}
          >
            Clear search
          </button>
        )}
      </form>

      {/* Disambiguated Candidates Panel when bare ID matches multiple requests/scopes/captures */}
      {searchResult && searchResult.needsDisambiguation && searchResult.candidates.length > 1 && (
        <section
          aria-label="Disambiguated correlation candidates"
          className="p-3.5 rounded-[6px] border space-y-2"
          style={{
            backgroundColor: 'var(--bg-panel)',
            borderColor: 'var(--accent)',
          }}
        >
          <div className="flex flex-wrap items-center justify-between gap-2 text-[12.5px]">
            <strong style={{ color: 'var(--accent)' }}>
              {searchResult.candidates.length} disambiguated candidates for “{searchResult.normalizedQuery}”
            </strong>
            <span style={{ color: 'var(--text-muted)' }}>
              Equal IDs across distinct requests, scopes, or captures remain separately selectable
            </span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
            {searchResult.candidates.slice(0, 6).map((cand) => (
              <button
                key={cand.groupKey}
                type="button"
                onClick={() => onOpenGroup(cand.groupKey)}
                className="text-left p-2.5 rounded-[5px] border hover:opacity-95 cursor-pointer flex items-center justify-between gap-2"
                style={{
                  backgroundColor: 'var(--bg-canvas)',
                  borderColor: 'var(--border-rule)',
                }}
              >
                <div className="min-w-0">
                  <div className="font-mono-tabular text-[12px] font-medium truncate">
                    {cand.group.displayTitle}
                  </div>
                  <div className="text-[11px] truncate" style={{ color: 'var(--text-muted)' }}>
                    {cand.disambiguationLabel}
                  </div>
                </div>
                <ArrowUpRight className="w-3.5 h-3.5 shrink-0" style={{ color: 'var(--accent)' }} />
              </button>
            ))}
          </div>
        </section>
      )}

      {/* Facet Filter Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2">
          <div
            className="inline-flex items-center p-0.5 rounded-[5px] border"
            style={{
              backgroundColor: 'var(--bg-panel)',
              borderColor: 'var(--border-rule)',
            }}
            role="group"
            aria-label="Filter by transport protocol"
          >
            {(
              [
                ['all', 'All transports'],
                ['rest', 'REST'],
                ['jsonrpc', 'JSON-RPC'],
                ['websocket', 'WebSocket'],
                ['webtransport', 'WebTransport'],
              ] as const
            ).map(([val, label]) => {
              const active = !showUnassigned && protocolFilter === val;
              return (
                <button
                  key={val}
                  type="button"
                  onClick={() => {
                    onToggleUnassigned(false);
                    onProtocolFilterChange(val);
                    setSelectedBucket(null);
                    setVisibleLimit(PAGE_SIZE);
                  }}
                  aria-pressed={active}
                  className="px-2.5 py-1 text-[12px] font-medium rounded-[4px] cursor-pointer whitespace-nowrap min-h-[30px]"
                  style={{
                    backgroundColor: active ? 'var(--accent)' : 'transparent',
                    color: active ? 'var(--accent-text)' : 'var(--text-secondary)',
                  }}
                >
                  {label}
                </button>
              );
            })}
          </div>

          <button
            type="button"
            onClick={() =>
              setOutcomeFilter((f) => (f === 'all' ? 'issues' : 'all'))
            }
            aria-pressed={outcomeFilter === 'issues'}
            className="px-2.5 py-1 text-[12px] font-medium rounded-[5px] border cursor-pointer whitespace-nowrap min-h-[32px]"
            style={{
              borderColor:
                outcomeFilter === 'issues' ? 'var(--status-warn)' : 'var(--border-rule)',
              backgroundColor:
                outcomeFilter === 'issues' ? 'var(--bg-panel-elevated)' : 'var(--bg-panel)',
              color:
                outcomeFilter === 'issues' ? 'var(--status-warn)' : 'var(--text-secondary)',
            }}
          >
            Incomplete / errors / skewed only
          </button>
        </div>

      </div>

      {/* Loading skeleton preserving layout stability */}
      {loading && !index && (
        <div className="space-y-3" aria-busy="true" aria-label="Loading correlations">
          <div
            className="h-32 rounded-[6px] border"
            style={{ backgroundColor: 'var(--bg-panel)', borderColor: 'var(--border-rule)' }}
          />
          <div
            className="h-64 rounded-[6px] border"
            style={{ backgroundColor: 'var(--bg-panel)', borderColor: 'var(--border-rule)' }}
          />
        </div>
      )}

      {/* Empty Live Data State */}
      {!loading && index && index.groups.length === 0 && index.unassignedEvents.length === 0 && (
        <section
          className="p-10 text-center rounded-[6px] border space-y-3"
          style={{
            backgroundColor: 'var(--bg-panel)',
            borderColor: 'var(--border-rule)',
          }}
        >
          <h2 className="font-display text-[22px]">No events in current capture</h2>
          <p className="text-[13px] max-w-md mx-auto" style={{ color: 'var(--text-secondary)' }}>
            The live loopback capture buffer is currently empty. Run the four-transport lab scenario to capture REST, HTTP JSON-RPC, WebSocket, and WebTransport handoffs.
          </p>
          <div className="pt-1">

          </div>
        </section>
      )}

      {/* Unassigned Events Surface */}
      {index && showUnassigned && (
        <section
          aria-label="Unassigned events without sufficient correlation context"
          className="rounded-[6px] border overflow-hidden"
          style={{
            backgroundColor: 'var(--bg-panel)',
            borderColor: 'var(--border-rule)',
          }}
        >
          <div
            className="px-4 py-3 border-b flex flex-wrap items-center justify-between gap-2"
            style={{ borderColor: 'var(--border-rule)' }}
          >
            <div>
              <h2 className="text-[14px] font-semibold">Unassigned events</h2>
              <p className="text-[12px]" style={{ color: 'var(--text-muted)' }}>
                Rows without a primary correlation ID or with ambiguous discriminators. Wire IDs are never promoted into synthetic correlation IDs.
              </p>
            </div>
            <button
              type="button"
              onClick={() => onToggleUnassigned(false)}
              className="px-2.5 py-1 text-[12px] border rounded-[4px] cursor-pointer"
              style={{ borderColor: 'var(--border-strong)' }}
            >
              Back to correlations
            </button>
          </div>

          {index.unassignedEvents.length === 0 ? (
            <div className="p-6 text-[13px]" style={{ color: 'var(--text-muted)' }}>
              Every retained event in this capture resolved unambiguously to a correlation group.
            </div>
          ) : (
            <div className="divide-y" style={{ borderColor: 'var(--border-rule)' }}>
              {index.unassignedEvents.map((u) => (
                <div
                  key={u.event.seq}
                  className="px-4 py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                >
                  <div className="space-y-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-2 font-mono-tabular text-[12px]">
                      <span style={{ color: 'var(--text-muted)' }}>#{u.event.seq}</span>
                      <span>{formatUtcTime(u.event.atMs)} UTC</span>
                      <ProtocolTag protocol={u.event.protocol} />
                      <span className="font-medium">{u.event.kind}</span>
                    </div>
                    <div className="text-[12.5px]" style={{ color: 'var(--status-warn)' }}>
                      {u.reason}
                    </div>
                    <div className="font-mono-tabular text-[11px]" style={{ color: 'var(--text-muted)' }}>
                      {[
                        u.event.correlationId && `correlation_id=${u.event.correlationId}`,
                        u.event.requestId && `request_id=${u.event.requestId}`,
                        u.event.transactionKey && `tx=${u.event.transactionKey}`,
                        u.event.allowlistedMeta.route && `route=${u.event.allowlistedMeta.route}`,
                      ]
                        .filter(Boolean)
                        .join(' · ')}
                    </div>
                  </div>

                  {u.ambiguousCandidateKeys.length > 0 && (
                    <div className="flex flex-wrap items-center gap-1.5 shrink-0">
                      <span className="text-[11.5px]" style={{ color: 'var(--text-muted)' }}>
                        Candidates:
                      </span>
                      {u.ambiguousCandidateKeys.map((ck) => {
                        const grp = index.groupsByKey.get(ck);
                        if (!grp) return null;
                        return (
                          <button
                            key={ck}
                            type="button"
                            onClick={() => onOpenGroup(ck)}
                            className="inline-flex items-center gap-1 px-2 py-1 text-[11.5px] font-mono-tabular border rounded-[4px] cursor-pointer hover:opacity-90"
                            style={{
                              borderColor: 'var(--accent)',
                              color: 'var(--accent)',
                            }}
                          >
                            <span>{grp.discriminatorLabel ?? grp.shortId}</span>
                            <ArrowUpRight className="w-3 h-3" />
                          </button>
                        );
                      })}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>
      )}

      {/* Karyogram & Correlation Groups Table */}
      {index && !showUnassigned && index.groups.length > 0 && (
        <>
          {karyogramData && (
            <KaryogramPanel
              data={karyogramData}
              selectedBucket={
                selectedBucket
                  ? {
                      rowKey: selectedBucket.rowKey,
                      bucketIndex: selectedBucket.bucketIndex,
                    }
                  : null
              }
              onSelectBucket={(sel) => {
                setSelectedBucket(sel);
                setVisibleLimit(PAGE_SIZE);
              }}
            />
          )}

          {/* No matches state preserving the search query */}
          {filteredGroups.length === 0 ? (
            <section
              className="p-8 text-center rounded-[6px] border space-y-2"
              style={{
                backgroundColor: 'var(--bg-panel)',
                borderColor: 'var(--border-rule)',
              }}
            >
              <h2 className="text-[15px] font-semibold">
                No matching correlations for {query.trim() ? `“${query.trim()}”` : 'active filters'}
              </h2>
              <p className="text-[12.5px]" style={{ color: 'var(--text-secondary)' }}>
                {idType === 'correlation_id' && query.trim()
                  ? 'Secondary IDs (request_id, rpc_id, stream_correlation_id, quic_connection_id, transaction_id) are searched only when you choose their type or add a prefix such as req: or rpc:.'
                  : 'Adjust the protocol, outcome, or karyogram bucket filters while keeping your query intact.'}
              </p>
            </section>
          ) : (
            <section
              aria-label="Recent correlation groups"
              className="rounded-[6px] border overflow-hidden"
              style={{
                backgroundColor: 'var(--bg-panel)',
                borderColor: 'var(--border-rule)',
              }}
            >
              <div className="overflow-x-auto">
                <table className="w-full border-collapse text-left min-w-[780px]">
                  <thead
                    className="border-b text-[11.5px] font-semibold"
                    style={{
                      backgroundColor: 'var(--bg-panel-elevated)',
                      borderColor: 'var(--border-rule)',
                      color: 'var(--text-secondary)',
                    }}
                  >
                    <tr>
                      <th className="px-3 py-2 w-10">
                        <span className="sr-only">Pin to compare</span>
                      </th>
                      <th className="px-3 py-2">Protocol / Scope</th>
                      <th className="px-3 py-2">Short ID & Discriminator</th>
                      <th className="px-3 py-2 font-mono-tabular">First → Last UTC</th>
                      <th className="px-3 py-2 font-mono-tabular text-right">Events</th>
                      <th className="px-3 py-2">Outcome & Coverage</th>
                      <th className="px-3 py-2">Related</th>
                      <th className="px-3 py-2 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y" style={{ borderColor: 'var(--border-rule)' }}>
                    {displayedGroups.map((group) => {
                      const isPinned = pinnedKeys.has(group.groupKey);
                      return (
                        <tr
                          key={group.groupKey}
                          className="transition-colors hover:bg-[var(--bg-panel-hover)]"
                          style={{ height: `${Math.max(rowHeight, 36)}px` }}
                        >
                          <td className="px-3 py-1.5">
                            <button
                              type="button"
                              onClick={() => onTogglePin(group.groupKey)}
                              aria-pressed={isPinned}
                              aria-label={`${isPinned ? 'Unpin' : 'Pin'} ${group.displayTitle} for comparison`}
                              className="p-1.5 rounded-[4px] cursor-pointer"
                              style={{
                                color: isPinned ? 'var(--accent)' : 'var(--text-muted)',
                              }}
                            >
                              <Pin className="w-3.5 h-3.5" />
                            </button>
                          </td>
                          <td className="px-3 py-1.5 whitespace-nowrap">
                            <div className="flex items-center gap-2">
                              <ProtocolTag protocol={group.protocol} />
                              <span className="text-[11.5px]" style={{ color: 'var(--text-muted)' }}>
                                {scopeLabel(group.scope)}
                              </span>
                            </div>
                          </td>
                          <td className="px-3 py-1.5">
                            <button
                              type="button"
                              onClick={() => onOpenGroup(group.groupKey)}
                              className="text-left group cursor-pointer"
                            >
                              <div className="font-mono-tabular text-[12.5px] font-medium group-hover:underline" style={{ color: 'var(--text-primary)' }}>
                                {group.shortId}
                              </div>
                              <div className="font-mono-tabular text-[11px]" style={{ color: 'var(--text-muted)' }}>
                                {[
                                  group.discriminatorLabel,
                                  group.service && `${group.environment} / ${group.service}`,
                                  group.quicConnectionId && `quic:${group.quicConnectionId}`,
                                  group.requesterSessionId && `req_sess:${group.requesterSessionId}`,
                                ]
                                  .filter(Boolean)
                                  .join(' · ') || 'primary scope'}
                              </div>
                            </button>
                          </td>
                          <td className="px-3 py-1.5 font-mono-tabular text-[12px] whitespace-nowrap">
                            <div>
                              {formatUtcTime(group.firstRecordedAtMs)} → {formatUtcTime(group.lastRecordedAtMs)}
                            </div>
                            <div className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>
                              recorded span {group.recordedSpanMs} ms
                            </div>
                          </td>
                          <td className="px-3 py-1.5 font-mono-tabular text-[12.5px] text-right whitespace-nowrap">
                            {group.metrics.observedEvents}
                          </td>
                          <td className="px-3 py-1.5 whitespace-nowrap">
                            <OutcomeLabel
                              outcome={group.outcomeSummary}
                              overrideLabel={group.httpStatus === undefined ? group.metrics.coverage : httpStatusLabel(group.httpStatus)}
                            />
                            {group.httpStatus !== undefined && (
                              <div className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>{group.metrics.coverage}</div>
                            )}
                          </td>
                          <td className="px-3 py-1.5 font-mono-tabular text-[11.5px] whitespace-nowrap" style={{ color: 'var(--text-secondary)' }}>
                            {group.relatedCorrelations.length > 0
                              ? `${group.relatedCorrelations.length} linked`
                              : '—'}
                          </td>
                          <td className="px-3 py-1.5 text-right whitespace-nowrap">
                            <button
                              type="button"
                              onClick={() => onOpenGroup(group.groupKey)}
                              aria-label={`Open waterfall for ${group.displayTitle}`}
                              className="inline-flex items-center gap-1 px-2.5 py-1 text-[12px] font-medium rounded-[4px] border cursor-pointer hover:opacity-90"
                              style={{
                                borderColor: 'var(--border-strong)',
                                color: 'var(--text-primary)',
                              }}
                            >
                              <span>Waterfall</span>
                              <ArrowUpRight className="w-3 h-3" />
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {filteredGroups.length > visibleLimit && (
                <div
                  className="px-4 py-2.5 border-t flex items-center justify-between text-[12px]"
                  style={{ borderColor: 'var(--border-rule)', color: 'var(--text-secondary)' }}
                >
                  <span className="font-mono-tabular">
                    Showing {displayedGroups.length} of {filteredGroups.length.toLocaleString()} correlations
                  </span>
                  <button
                    type="button"
                    onClick={() => setVisibleLimit((v) => v + PAGE_SIZE)}
                    className="px-3 py-1.5 rounded-[4px] border font-medium cursor-pointer"
                    style={{ borderColor: 'var(--border-strong)', color: 'var(--text-primary)' }}
                  >
                    Load {Math.min(PAGE_SIZE, filteredGroups.length - visibleLimit)} more
                  </button>
                </div>
              )}
            </section>
          )}
        </>
      )}
    </main>
  );
}
