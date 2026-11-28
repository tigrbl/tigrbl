import React from 'react';
import { formatUtcTime } from '../core/correlationEngine';
import type { KaryogramBucket, KaryogramData, KaryogramRow } from '../core/types';
import { protocolColorVar } from './StatusIndicator';

interface KaryogramPanelProps {
  data: KaryogramData;
  selectedBucket: { rowKey: string; bucketIndex: number } | null;
  onSelectBucket: (selection: { rowKey: string; bucketIndex: number; bucket: KaryogramBucket; row: KaryogramRow } | null) => void;
}

export function KaryogramPanel({
  data,
  selectedBucket,
  onSelectBucket,
}: KaryogramPanelProps) {
  if (data.rows.length === 0) {
    return null;
  }

  const selectedRow = selectedBucket
    ? data.rows.find((r) => r.rowKey === selectedBucket.rowKey)
    : null;
  const selectedCell =
    selectedRow && selectedBucket
      ? selectedRow.buckets[selectedBucket.bucketIndex]
      : null;

  return (
    <section
      aria-label="Event-density karyogram"
      className="border rounded-[6px] overflow-hidden"
      style={{
        backgroundColor: 'var(--bg-panel)',
        borderColor: 'var(--border-rule)',
      }}
    >
      <div
        className="flex flex-wrap items-center justify-between gap-2 px-4 py-2 border-b"
        style={{ borderColor: 'var(--border-rule)' }}
      >
        <div className="flex items-center gap-3 min-w-0">
          <h2 className="text-[13px] font-semibold tracking-tight">
            Event-density karyogram
          </h2>
          <span
            className="font-mono-tabular text-[11.5px]"
            style={{ color: 'var(--text-muted)' }}
          >
            {formatUtcTime(data.minTimeMs)} — {formatUtcTime(data.maxTimeMs)} UTC
          </span>
        </div>

        <div className="flex items-center gap-3 text-[12px]">
          {selectedRow && selectedCell ? (
            <div className="flex items-center gap-2 font-mono-tabular">
              <span style={{ color: 'var(--text-secondary)' }}>
                {selectedRow.label} · {selectedCell.count} events ·{' '}
                {selectedCell.groupKeys.length} correlation
                {selectedCell.groupKeys.length === 1 ? '' : 's'}
              </span>
              <button
                type="button"
                onClick={() => onSelectBucket(null)}
                className="px-2 py-0.5 text-[11.5px] border rounded-[4px] hover:opacity-90 cursor-pointer whitespace-nowrap"
                style={{
                  borderColor: 'var(--border-strong)',
                  color: 'var(--text-primary)',
                }}
              >
                Clear bucket
              </button>
            </div>
          ) : (
            <span style={{ color: 'var(--text-muted)' }}>
              Select a bucket to inspect exact counts and filter rows
            </span>
          )}
        </div>
      </div>

      <div className="overflow-x-auto">
        <div className="min-w-[600px] divide-y" style={{ borderColor: 'var(--border-rule)' }}>
          {data.rows.map((row) => {
            const color = protocolColorVar(row.protocol);
            return (
              <div
                key={row.rowKey}
                className="grid items-center gap-3 px-4 py-1.5"
                style={{
                  gridTemplateColumns: '210px 1fr 96px',
                  borderColor: 'var(--border-rule)',
                }}
              >
                <div className="min-w-0">
                  <div className="text-[12.5px] font-medium truncate" title={row.label}>
                    {row.label}
                  </div>
                  <div
                    className="font-mono-tabular text-[11px]"
                    style={{ color: 'var(--text-muted)' }}
                  >
                    {row.groupCount} group{row.groupCount === 1 ? '' : 's'}
                  </div>
                </div>

                <div
                  className="grid gap-[2px] items-end h-6"
                  style={{
                    gridTemplateColumns: `repeat(${data.bucketCount}, minmax(0, 1fr))`,
                  }}
                  role="group"
                  aria-label={`${row.label} activity buckets`}
                >
                  {row.buckets.map((bucket) => {
                    const isSelected =
                      selectedBucket?.rowKey === row.rowKey &&
                      selectedBucket?.bucketIndex === bucket.index;
                    const ratio =
                      bucket.count > 0
                        ? Math.max(0.22, Math.sqrt(bucket.count / data.maxBucketCount))
                        : 0;

                    return (
                      <button
                        key={bucket.index}
                        type="button"
                        disabled={bucket.count === 0}
                        onClick={() =>
                          onSelectBucket(
                            isSelected
                              ? null
                              : {
                                  rowKey: row.rowKey,
                                  bucketIndex: bucket.index,
                                  bucket,
                                  row,
                                }
                          )
                        }
                        aria-label={`${row.label}, bucket ${bucket.index + 1}, ${formatUtcTime(
                          bucket.startMs
                        )} to ${formatUtcTime(bucket.endMs)}, ${bucket.count} events in ${
                          bucket.groupKeys.length
                        } correlations`}
                        aria-pressed={isSelected}
                        title={`${row.label}\n${formatUtcTime(bucket.startMs)}–${formatUtcTime(
                          bucket.endMs
                        )}\n${bucket.count} events · ${bucket.groupKeys.length} groups`}
                        className="relative h-6 flex items-end justify-center rounded-[2px] transition-opacity focus-visible:z-10 disabled:cursor-default enabled:cursor-pointer"
                        style={{
                          backgroundColor: isSelected
                            ? 'var(--accent-muted)'
                            : 'var(--grid-line)',
                          outline: isSelected ? '1px solid var(--accent)' : undefined,
                        }}
                      >
                        {bucket.count > 0 && (
                          <span
                            className="w-full rounded-[1px]"
                            style={{
                              height: `${Math.round(ratio * 100)}%`,
                              backgroundColor: isSelected ? 'var(--accent)' : color,
                              opacity: isSelected ? 1 : 0.35 + ratio * 0.65,
                            }}
                          />
                        )}
                      </button>
                    );
                  })}
                </div>

                <div
                  className="text-right font-mono-tabular text-[11.5px]"
                  style={{ color: 'var(--text-secondary)' }}
                >
                  {row.eventCount} ev
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
