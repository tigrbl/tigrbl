import React from 'react';
import { formatUtcTime, WorkspaceMetrics } from '../adapter/traceAdapter';
import { TraceSnapshot } from '../types/trace';

interface MetricStripProps {
  metrics: WorkspaceMetrics;
  hasData: boolean;
  windowMinMs: number;
  windowMaxMs: number;
  snapshot: TraceSnapshot | null;
  paginated?: boolean;
  onFocusMetric: (metricKey: 'connections' | 'sessions' | 'invocations' | 'transactions' | 'deliveries') => void;
}

const Sparkline: React.FC<{ values: number[]; color: string }> = ({ values, color }) => {
  const max = Math.max(1, ...values);
  const w = 56;
  const h = 18;
  const step = w / values.length;
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} aria-hidden="true" className="shrink-0">
      {values.map((v, i) => {
        const barH = v === 0 ? 1 : Math.max(2, (v / max) * (h - 2));
        return (
          <rect
            key={i}
            x={i * step + 0.5}
            y={h - barH}
            width={Math.max(2, step - 1.5)}
            height={barH}
            rx={0.5}
            fill={color}
            opacity={v === 0 ? 0.2 : 0.8}
          />
        );
      })}
    </svg>
  );
};

export const MetricStrip: React.FC<MetricStripProps> = ({
  metrics,
  hasData,
  windowMinMs,
  windowMaxMs,
  snapshot,
  paginated = false,
  onFocusMetric,
}) => {
  const evicted = snapshot?.retained_range.evicted_count ?? 0;
  const totalEmitted = snapshot?.retained_range.total_emitted ?? 0;
  const retainedCount = snapshot?.events.length ?? 0;

  const coverageText = !hasData
    ? 'Awaiting observations'
    : paginated
      ? `${retainedCount} events on this page`
      : evicted > 0
        ? `Bounded retention: ${retainedCount} of ${totalEmitted} retained (${evicted} evicted)`
        : `Full coverage: ${retainedCount} retained (limit ${snapshot?.retention_limit ?? 750})`;

  const cells: Array<{
    key: 'connections' | 'sessions' | 'invocations' | 'transactions' | 'deliveries';
    label: string;
    value: string;
    detail: string;
    definition: string;
    spark: number[];
    color: string;
  }> = [
    {
      key: 'connections',
      label: 'Connections',
      value: hasData ? String(metrics.connections) : '—',
      detail: hasData ? 'Distinct carrier IDs' : 'No baseline yet',
      definition: 'Distinct connection_id values observed in retained records within the active window.',
      spark: metrics.sparklines.connections,
      color: 'var(--role-carrier)',
    },
    {
      key: 'sessions',
      label: 'Transport sessions',
      value: hasData ? String(metrics.transportSessions) : '—',
      detail: hasData ? 'WS & WT sessions' : 'No baseline yet',
      definition: 'Distinct transport_session_id values observed across WebSocket and WebTransport.',
      spark: metrics.sparklines.sessions,
      color: 'var(--role-carrier)',
    },
    {
      key: 'invocations',
      label: 'Invocations',
      value: hasData ? String(metrics.invocations) : '—',
      detail: hasData ? 'Deduped operations' : 'No baseline yet',
      definition: 'Distinct invocation_id values deduplicated across lifecycle events.',
      spark: metrics.sparklines.invocations,
      color: 'var(--role-invocation)',
    },
    {
      key: 'transactions',
      label: 'Transactions',
      value: hasData ? String(metrics.transactions) : '—',
      detail: hasData
        ? `${metrics.transactionsCommitted} commit · ${metrics.transactionsRolledBack} rollback${metrics.transactionsOpen > 0 ? ` · ${metrics.transactionsOpen} open` : ''}`
        : 'No baseline yet',
      definition: 'Distinct (engine_session_id, transaction_id) pairs. Shared transactions count once.',
      spark: metrics.sparklines.transactions,
      color: 'var(--role-invocation)',
    },
    {
      key: 'deliveries',
      label: 'Deliveries',
      value: hasData ? String(metrics.deliveries) : '—',
      detail: hasData ? `${metrics.publications} publications` : 'No baseline yet',
      definition: 'Distinct recipient delivery_id notifications matched to broker publications.',
      spark: metrics.sparklines.deliveries,
      color: 'var(--role-success)',
    },
  ];

  return (
    <section
      aria-label="Observed metrics summary"
      className="rounded-[5px] border overflow-hidden"
      style={{ backgroundColor: 'var(--panel)', borderColor: 'var(--border)' }}
    >
      <div
        className="px-3.5 py-2 border-b flex flex-wrap items-center justify-between gap-2 text-[12px]"
        style={{ borderColor: 'var(--border)', color: 'var(--text-muted)' }}
      >
        <span className="font-mono-data">
          {hasData
            ? `Window: ${formatUtcTime(windowMinMs)} — ${formatUtcTime(windowMaxMs)}`
            : 'Window: —'}
        </span>
        <span
          className="font-mono-data"
          style={{ color: evicted > 0 ? 'var(--role-partial)' : 'var(--text-muted)' }}
        >
          {coverageText}
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 divide-y sm:divide-y-0 sm:divide-x" style={{ borderColor: 'var(--border)' }}>
        {cells.map((cell) => (
          <button
            key={cell.key}
            type="button"
            onClick={() => onFocusMetric(cell.key)}
            title={cell.definition}
            aria-label={`${cell.label}: ${cell.value}. ${cell.definition}`}
            className="text-left px-3.5 py-3 lab-transition row-hover cursor-pointer flex flex-col justify-between gap-1.5"
            style={{ borderColor: 'var(--border)' }}
          >
            <div className="flex items-start justify-between gap-2">
              <span
                className="font-mono-data text-[24px] leading-[28px] font-medium"
                style={{ color: hasData ? 'var(--text-primary)' : 'var(--text-muted)' }}
              >
                {cell.value}
              </span>
              {hasData && <Sparkline values={cell.spark} color={cell.color} />}
            </div>
            <div>
              <div className="text-[12px] leading-[16px] font-medium" style={{ color: 'var(--text-primary)' }}>
                {cell.label}
              </div>
              <div className="text-[12px] leading-[16px] truncate" style={{ color: 'var(--text-muted)' }}>
                {cell.detail}
              </div>
            </div>
          </button>
        ))}
      </div>
    </section>
  );
};
