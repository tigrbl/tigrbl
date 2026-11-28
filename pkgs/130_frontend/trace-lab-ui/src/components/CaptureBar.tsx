import { Pause, Play, Radio } from 'lucide-react';
import type { DatasetMode, RecordedDatasetId } from '../types/trace';

export interface CaptureStatus {
  connection: 'loading' | 'connected' | 'stale';
  at: string | null;
  sequence: number;
}

export function CaptureBar({
  mode, sample, status, paused, onDatasetChange, onTogglePause,
}: {
  mode: DatasetMode;
  sample: RecordedDatasetId;
  status: CaptureStatus;
  paused: CaptureStatus | null;
  onDatasetChange: (mode: DatasetMode, sample?: RecordedDatasetId) => void;
  onTogglePause: () => void;
}) {
  const at = paused?.at ?? status.at;
  const buffered = paused ? Math.max(0, status.sequence - paused.sequence) : 0;
  const statusText = status.connection === 'stale' ? 'Stale snapshot'
    : paused ? 'Paused' : status.connection === 'loading' ? 'Connecting…' : 'Live';
  const control = 'min-h-8 rounded border px-2.5 text-[13px]';
  const border = { borderColor: 'var(--border)', backgroundColor: 'var(--canvas)' };

  return (
    <section
      aria-label="Capture controls"
      className="flex shrink-0 flex-wrap items-center gap-x-3 gap-y-2 border-b px-3 py-2 sm:px-4"
      style={{ backgroundColor: 'var(--panel)', borderColor: 'var(--border)' }}
    >
      <div role="group" aria-label="Dataset mode" className="inline-flex rounded border p-0.5" style={border}>
        {(['live', 'recorded'] as const).map((option) => (
          <button
            key={option}
            type="button"
            aria-pressed={mode === option}
            onClick={() => onDatasetChange(option)}
            className="min-h-7 rounded-sm px-2.5 text-[13px] font-medium cursor-pointer"
            style={{
              backgroundColor: mode === option ? 'var(--accent)' : 'transparent',
              color: mode === option ? 'var(--accent-contrast)' : 'var(--text-primary)',
            }}
          >
            {option === 'live' ? 'Live' : 'Recorded'}
          </button>
        ))}
      </div>
      {mode === 'recorded' ? (
        <label className="flex items-center gap-2 text-[13px]">
          Recording
          <select
            className={control}
            style={border}
            value={sample}
            onChange={(event) => onDatasetChange('recorded', event.target.value as RecordedDatasetId)}
          >
            <option value="recorded-v1.2-synthetic">Synthetic sample</option>
            <option value="recorded-stress-10k">Synthetic stress (10,000 rows)</option>
          </select>
        </label>
      ) : (
        <>
          <button
            type="button"
            onClick={onTogglePause}
            disabled={!paused && !status.at}
            className={`${control} inline-flex items-center gap-1.5 cursor-pointer disabled:opacity-50`}
            style={border}
          >
            {paused ? <Play size={14} aria-hidden="true" /> : <Pause size={14} aria-hidden="true" />}
            {paused ? 'Resume live updates' : 'Pause live updates'}
            {buffered > 0 && ` (${buffered} buffered)`}
          </button>
          <div className="flex items-center gap-1.5 font-mono-data text-[12px]" style={{ color: 'var(--text-muted)' }}>
            <Radio size={14} aria-hidden="true" style={{ color: status.connection === 'stale' ? 'var(--role-rejected)' : paused ? 'var(--text-muted)' : 'var(--role-success)' }} />
            <span>{statusText}</span>
            {at && <time dateTime={at} title={at}>· {new Date(at).toISOString().slice(11, 19)}Z</time>}
          </div>
        </>
      )}
    </section>
  );
}
