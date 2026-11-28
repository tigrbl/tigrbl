import React, { useMemo, useRef, useState } from 'react';
import { ArrowDown, ArrowUp, X } from 'lucide-react';
import { formatUtcTime, truncateId } from '../adapter/traceAdapter';
import { DENSITY_ROW_HEIGHT, PROTOCOL_LABELS } from '../theme/tokens';
import { DensityId, NormalizedEvent, SelectionState } from '../types/trace';
import { CorrelationLink } from './CorrelationLink';
import { RoleMark } from './RoleMark';

interface EventTableProps {
  events: NormalizedEvent[];
  density: DensityId;
  selection: SelectionState | null;
  onSelect: (sel: SelectionState) => void;
  onFollowCorrelation?: (href: string) => void;
  bucketFilter: { rowId: string; startMs: number; endMs: number; count: number } | null;
  onClearBucketFilter: () => void;
  title?: string;
  compact?: boolean;
}

type SortKey = 'sequence' | 'transport' | 'kind' | 'outcome' | 'duration';

export const EventTable: React.FC<EventTableProps> = ({
  events,
  density,
  selection,
  onSelect,
  onFollowCorrelation,
  bucketFilter,
  onClearBucketFilter,
  title = 'Event table',
  compact = false,
}) => {
  const [sortKey, setSortKey] = useState<SortKey>('sequence');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc');
  const [scrollTop, setScrollTop] = useState(0);
  const containerRef = useRef<HTMLDivElement | null>(null);

  const rowHeight = Math.max(32, DENSITY_ROW_HEIGHT[density]);
  const viewportHeight = compact ? 320 : 520;

  const sortedEvents = useMemo(() => {
    const arr = [...events];
    arr.sort((a, b) => {
      let cmp = 0;
      if (sortKey === 'sequence') cmp = a.sequence - b.sequence;
      else if (sortKey === 'transport') cmp = a.transport.localeCompare(b.transport);
      else if (sortKey === 'kind') cmp = a.kind.localeCompare(b.kind);
      else if (sortKey === 'outcome') cmp = a.outcomeLabel.localeCompare(b.outcomeLabel);
      else if (sortKey === 'duration') {
        const va = a.observation?.value ?? a.duration_ms ?? -1;
        const vb = b.observation?.value ?? b.duration_ms ?? -1;
        cmp = va - vb;
      }
      return sortDir === 'asc' ? cmp : -cmp;
    });
    return arr;
  }, [events, sortKey, sortDir]);

  const toggleSort = (key: SortKey) => {
    if (sortKey === key) setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    else {
      setSortKey(key);
      setSortDir('asc');
    }
  };

  // Virtual windowing for 10,000+ row stress performance
  const overscan = 10;
  const totalHeight = sortedEvents.length * rowHeight;
  const startIdx = Math.max(0, Math.floor(scrollTop / rowHeight) - overscan);
  const visibleCount = Math.ceil(viewportHeight / rowHeight) + overscan * 2;
  const endIdx = Math.min(sortedEvents.length, startIdx + visibleCount);
  const visibleSlice = sortedEvents.slice(startIdx, endIdx);

  const renderSortIcon = (key: SortKey) => {
    if (sortKey !== key) return null;
    return sortDir === 'asc' ? (
      <ArrowUp size={12} aria-hidden="true" />
    ) : (
      <ArrowDown size={12} aria-hidden="true" />
    );
  };

  const renderPrimaryIdLink = (ev: NormalizedEvent) => {
    const items: Array<{ label: string; value: string; entityId: string }> = [];
    if (ev.correlation_id) {
      items.push({
        label: 'corr',
        value: ev.correlation_id,
        entityId: ev.request_id
          ? `request:${ev.transport}:${ev.request_id}`
          : ev.transport_session_id
            ? `transport_session:${ev.transport_session_id}`
            : `protocol:${ev.transport}`,
      });
    }
    if (ev.invocation_id) {
      items.push({
        label: 'inv',
        value: ev.invocation_id,
        entityId: `invocation:${ev.invocation_id}`,
      });
    }
    if (ev.scopedTransactionKey && ev.transaction_id) {
      items.push({
        label: 'tx',
        value: ev.transaction_id,
        entityId: `transaction:${ev.scopedTransactionKey}`,
      });
    }
    if (ev.delivery_id) {
      items.push({
        label: 'deliv',
        value: ev.delivery_id,
        entityId: ev.subscription_id ? `subscription:${ev.subscription_id}` : `protocol:websocket`,
      });
    }
    if (ev.datagram_id) {
      items.push({
        label: 'dg',
        value: ev.datagram_id,
        entityId: ev.transport_session_id
          ? `datagrams:${ev.transport_session_id}`
          : `protocol:webtransport`,
      });
    }

    if (items.length === 0) return <span style={{ color: 'var(--text-muted)' }}>—</span>;

    return (
      <div className="flex items-center gap-2 overflow-hidden">
        {items.slice(0, 2).map((item) => item.label === 'corr' && onFollowCorrelation ? (
          <CorrelationLink
            key={item.value}
            id={item.value}
            sequence={ev.sequence}
            onFollowCorrelation={onFollowCorrelation}
          >
            corr:{truncateId(item.value, 14)}
          </CorrelationLink>
        ) : (
          <button
            key={`${item.label}-${item.value}`}
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              onSelect({ type: 'entity', id: item.entityId });
            }}
            className="font-mono-data text-[12px] hover:underline truncate cursor-pointer"
            style={{ color: 'var(--accent)' }}
            title={`${item.label}: ${item.value}`}
          >
            {item.label}:{truncateId(item.value, 14)}
          </button>
        ))}
      </div>
    );
  };

  return (
    <section
      aria-label={title}
      className="rounded-[5px] border overflow-hidden"
      style={{ backgroundColor: 'var(--panel)', borderColor: 'var(--border)' }}
    >
      <div
        className="px-3.5 py-2 border-b flex flex-wrap items-center justify-between gap-2"
        style={{ borderColor: 'var(--border)' }}
      >
        <div className="flex items-baseline gap-3">
          <h2 className="text-[16px] leading-[22px] font-semibold" style={{ color: 'var(--text-primary)' }}>
            {title}
          </h2>
          <span className="font-mono-data text-[12px]" style={{ color: 'var(--text-muted)' }}>
            {sortedEvents.length.toLocaleString()} rows · Ordered by sequence
          </span>
        </div>

        {bucketFilter && (
          <div className="flex items-center gap-2 text-[12px]">
            <span className="font-mono-data" style={{ color: 'var(--accent)' }}>
              Showing dense bucket ({bucketFilter.count} events)
            </span>
            <button
              type="button"
              onClick={onClearBucketFilter}
              className="px-2 py-0.5 rounded-[4px] border inline-flex items-center gap-1 cursor-pointer"
              style={{ borderColor: 'var(--border)', color: 'var(--text-primary)' }}
            >
              <X size={12} aria-hidden="true" />
              Clear bucket
            </button>
          </div>
        )}
      </div>

      {sortedEvents.length === 0 ? (
        <div className="px-4 py-10 text-center text-[13px]" style={{ color: 'var(--text-muted)' }}>
          No trace events in the current view.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <div className="min-w-[780px]">
            {/* Sticky Table Header */}
            <div
              role="row"
              className="grid grid-cols-[150px_112px_210px_130px_84px_1fr] px-3 h-9 border-b items-center text-[12px] font-medium"
              style={{
                backgroundColor: 'var(--surface-alt)',
                borderColor: 'var(--border)',
                color: 'var(--text-muted)',
              }}
            >
              <button
                type="button"
                onClick={() => toggleSort('sequence')}
                className="text-left inline-flex items-center gap-1 cursor-pointer"
              >
                Recorded at (UTC) {renderSortIcon('sequence')}
              </button>
              <button
                type="button"
                onClick={() => toggleSort('transport')}
                className="text-left inline-flex items-center gap-1 cursor-pointer"
              >
                Protocol {renderSortIcon('transport')}
              </button>
              <button
                type="button"
                onClick={() => toggleSort('kind')}
                className="text-left inline-flex items-center gap-1 cursor-pointer"
              >
                Kind {renderSortIcon('kind')}
              </button>
              <button
                type="button"
                onClick={() => toggleSort('outcome')}
                className="text-left inline-flex items-center gap-1 cursor-pointer"
              >
                Outcome {renderSortIcon('outcome')}
              </button>
              <button
                type="button"
                onClick={() => toggleSort('duration')}
                className="text-right inline-flex items-center justify-end gap-1 cursor-pointer pr-2"
              >
                Duration {renderSortIcon('duration')}
              </button>
              <span>Correlation / Invocation / Transaction ID</span>
            </div>

            {/* Virtualized Scroll Body */}
            <div
              ref={containerRef}
              onScroll={(e) => setScrollTop(e.currentTarget.scrollTop)}
              style={{ height: `${Math.min(viewportHeight, Math.max(rowHeight, totalHeight))}px` }}
              className="overflow-y-auto relative"
              role="grid"
              aria-rowcount={sortedEvents.length}
            >
              <div style={{ height: `${totalHeight}px`, position: 'relative' }}>
                {visibleSlice.map((ev, offset) => {
                  const idx = startIdx + offset;
                  const isSelected = selection?.type === 'event' && selection.id === ev.id;
                  const dur = ev.observation?.value ?? ev.duration_ms;

                  return (
                    <div
                      key={ev.id}
                      role="row"
                      tabIndex={0}
                      aria-rowindex={idx + 1}
                      aria-selected={isSelected}
                      onClick={() => onSelect({ type: 'event', id: ev.id })}
                      onKeyDown={(e) => {
                        if (e.target === e.currentTarget && (e.key === 'Enter' || e.key === ' ')) {
                          e.preventDefault();
                          onSelect({ type: 'event', id: ev.id });
                        }
                      }}
                      style={{
                        position: 'absolute',
                        top: `${idx * rowHeight}px`,
                        left: 0,
                        right: 0,
                        height: `${rowHeight}px`,
                        borderColor: 'var(--border)',
                      }}
                      className={`grid grid-cols-[150px_112px_210px_130px_84px_1fr] px-3 border-b items-center text-[13px] cursor-pointer lab-transition ${
                        isSelected ? 'row-selected' : 'row-hover'
                      }`}
                    >
                      <div className="font-mono-data text-[12px] truncate" style={{ color: 'var(--text-muted)' }}>
                        {formatUtcTime(ev.atMs)}{' '}
                        <span className="opacity-70">#{ev.sequence}</span>
                      </div>

                      <div className="truncate text-[12px]" style={{ color: 'var(--text-primary)' }}>
                        {PROTOCOL_LABELS[ev.transport] || ev.transport}
                      </div>

                      <div className="truncate pr-2">
                        <span
                          className="font-mono-data text-[12px]"
                          style={{
                            color: ev.knownKind ? 'var(--text-primary)' : 'var(--role-partial)',
                          }}
                          title={ev.knownKind ? ev.kind : `${ev.kind} (unrecognized kind)`}
                        >
                          {ev.kind}
                        </span>
                      </div>

                      <div className="truncate pr-2">
                        <RoleMark
                          role={ev.role}
                          kind={ev.kind}
                          size={11}
                          label={ev.outcomeLabel}
                          className="text-[12px]"
                        />
                      </div>

                      <div
                        className="font-mono-data text-[12px] text-right pr-2"
                        style={{ color: dur !== undefined ? 'var(--text-primary)' : 'var(--text-muted)' }}
                      >
                        {dur !== undefined ? `${dur.toPrecision(3)} ms` : '—'}
                      </div>

                      <div className="min-w-0">{renderPrimaryIdLink(ev)}</div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  );
};
