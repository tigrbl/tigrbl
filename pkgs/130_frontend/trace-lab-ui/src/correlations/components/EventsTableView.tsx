import React from 'react';
import { formatUtcTime } from '../core/correlationEngine';
import type { WaterfallMark } from '../core/types';
import { OutcomeLabel } from './StatusIndicator';

interface EventsTableViewProps {
  marks: WaterfallMark[];
  selectedMarkId: string | null;
  rowHeight: number;
  onSelectMark: (mark: WaterfallMark) => void;
}

export function EventsTableView({
  marks,
  selectedMarkId,
  rowHeight,
  onSelectMark,
}: EventsTableViewProps) {
  return (
    <div
      className="flex-1 overflow-auto border-t"
      style={{ borderColor: 'var(--border-rule)' }}
    >
      <table className="w-full border-collapse text-left">
        <thead
          className="sticky top-0 z-10 border-b text-[11.5px] font-semibold"
          style={{
            backgroundColor: 'var(--bg-panel-elevated)',
            borderColor: 'var(--border-rule)',
            color: 'var(--text-secondary)',
          }}
        >
          <tr>
            <th className="px-3 py-2 font-mono-tabular">Seq</th>
            <th className="px-3 py-2 font-mono-tabular">Recorded UTC</th>
            <th className="px-3 py-2">Event / Lane</th>
            <th className="px-3 py-2">Direction</th>
            <th className="px-3 py-2">Provenance</th>
            <th className="px-3 py-2">Time basis</th>
            <th className="px-3 py-2">Measured</th>
            <th className="px-3 py-2">Outcome</th>
          </tr>
        </thead>
        <tbody className="divide-y" style={{ borderColor: 'var(--border-rule)' }}>
          {marks.map((mark) => {
            const isSelected = mark.id === selectedMarkId;
            return (
              <tr
                key={mark.id}
                onClick={() => onSelectMark(mark)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    onSelectMark(mark);
                  }
                }}
                tabIndex={0}
                aria-selected={isSelected}
                className="cursor-pointer transition-colors"
                style={{
                  height: `${rowHeight}px`,
                  backgroundColor: isSelected
                    ? 'var(--accent-muted)'
                    : mark.isLinkedContext
                    ? 'var(--bg-canvas)'
                    : 'transparent',
                  opacity: mark.isLinkedContext && !isSelected ? 0.72 : 1,
                }}
              >
                <td className="px-3 py-1 font-mono-tabular text-[12px]" style={{ color: 'var(--text-muted)' }}>
                  #{mark.seq}
                </td>
                <td className="px-3 py-1 font-mono-tabular text-[12px] whitespace-nowrap">
                  {formatUtcTime(mark.atMs)}
                </td>
                <td className="px-3 py-1">
                  <div className="text-[12.5px] font-medium truncate max-w-[260px]">
                    {mark.label}
                  </div>
                  <div className="font-mono-tabular text-[11px]" style={{ color: 'var(--text-muted)' }}>
                    {mark.kind}
                    {mark.event.streamCorrelationId ? ` · stream ${mark.event.streamCorrelationId}` : ''}
                    {mark.isLinkedContext ? ' · linked context' : ''}
                  </div>
                </td>
                <td className="px-3 py-1 text-[12px] whitespace-nowrap" style={{ color: 'var(--text-secondary)' }}>
                  {mark.directionLabel}
                </td>
                <td className="px-3 py-1 text-[12px] whitespace-nowrap">
                  <span
                    style={{
                      color:
                        mark.provenance === 'Linked by evidence'
                          ? 'var(--accent)'
                          : 'var(--text-secondary)',
                    }}
                  >
                    {mark.provenance}
                  </span>
                </td>
                <td className="px-3 py-1 font-mono-tabular text-[11.5px] whitespace-nowrap" style={{ color: 'var(--text-muted)' }}>
                  {mark.clockOrderUncertain
                    ? 'Clock order uncertain'
                    : mark.timeBasis === 'measured_monotonic'
                    ? 'Measured monotonic'
                    : mark.timeBasis === 'partial_mixed'
                    ? 'Partial timing'
                    : 'Recorded at'}
                </td>
                <td className="px-3 py-1 font-mono-tabular text-[12px] whitespace-nowrap">
                  {mark.measuredDurationMs !== undefined && !mark.clockOrderUncertain
                    ? `${mark.measuredDurationMs.toPrecision(3)} ms`
                    : '—'}
                </td>
                <td className="px-3 py-1">
                  <OutcomeLabel outcome={mark.outcome} />
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
