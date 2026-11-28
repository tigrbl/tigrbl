import React from 'react';
import { Play, RefreshCw, X } from 'lucide-react';
import { formatUtcTime } from '../adapter/traceAdapter';
import {
  DatasetMode,
  RouteId,
} from '../types/trace';
import { LiveStatusInfo } from '../hooks/useTraceLab';

interface HeaderProps {
  route: RouteId;
  mode: DatasetMode;
  liveStatus: LiveStatusInfo;
  isRunning: boolean;
  runElapsedMs: number;
  onRunAll?: () => void;
  onRetryFetch: () => void;
  runNotice: { tone: 'info' | 'success' | 'warning' | 'error'; message: string } | null;
  onDismissRunNotice: () => void;
  onDismissRestartNotice: () => void;
  liveAnnouncement: string;
  datasetLabel?: string;
}

export const Header: React.FC<HeaderProps> = ({
  route,
  mode,
  liveStatus,
  isRunning,
  runElapsedMs,
  onRunAll,
  onRetryFetch,
  runNotice,
  onDismissRunNotice,
  onDismissRestartNotice,
  liveAnnouncement,
  datasetLabel,
}) => {
  return (
    <>
      {/* Single polite live status region for run, load, reconnect, and pause announcements */}
      <div className="sr-only" role="status" aria-live="polite" aria-atomic="true">
        {liveAnnouncement}
      </div>

      {/* Quiet Editorial Title Strip */}
      <div
        className="border-b px-4 py-3 flex flex-wrap items-baseline justify-between gap-3"
        style={{ backgroundColor: 'var(--canvas)', borderColor: 'var(--border)' }}
      >
        <div className="flex flex-wrap items-baseline gap-x-4 gap-y-1">
          <h1
            className="font-editorial text-[28px] leading-[32px] md:text-[34px] md:leading-[38px] tracking-[-0.015em]"
            style={{ color: 'var(--text-primary)' }}
          >
            {route === 'explore' ? 'Transport Trace Explorer' : 'Observation Distributions'}
          </h1>
          <span className="text-[13px]" style={{ color: 'var(--text-muted)' }}>
            {mode === 'live'
              ? onRunAll
                ? 'Live loopback capture · REST, HTTP JSON-RPC, WebSocket, WebTransport & DB transactions'
                : 'Live Tigrbl traces from the collector'
              : `${datasetLabel || 'Recorded synthetic fixture'} · Isolated from live capture`}
          </span>
        </div>
        {onRunAll && (
          <button
            type="button"
            onClick={onRunAll}
            aria-disabled={isRunning}
            className="inline-flex min-h-8 items-center gap-1.5 rounded px-3.5 text-[13px] font-medium cursor-pointer"
            style={{ backgroundColor: 'var(--accent)', color: 'var(--accent-contrast)', opacity: isRunning ? 0.78 : 1 }}
          >
            <Play size={14} aria-hidden="true" />
            {isRunning ? `Running… ${(runElapsedMs / 1000).toFixed(1)}s` : 'Run all transports'}
          </button>
        )}
      </div>

      {/* Contextual Status Banners (Stale, Restart, Run Outcome/409/403) */}
      {mode === 'live' && liveStatus.connectionState === 'stale' && (
        <div
          role="alert"
          className="px-4 py-2 border-b flex items-center justify-between gap-3 text-[13px]"
          style={{
            backgroundColor: 'var(--surface-alt)',
            borderColor: 'var(--border)',
            color: 'var(--text-primary)',
          }}
        >
          <span>
            Live snapshot connection interrupted ({liveStatus.error}). Retaining last verified
            snapshot
            {liveStatus.lastGoodAt
              ? ` from ${formatUtcTime(Date.parse(liveStatus.lastGoodAt))}`
              : ''}
            .
          </span>
          <button
            type="button"
            onClick={onRetryFetch}
            className="px-2.5 py-1 text-[13px] rounded-[4px] border inline-flex items-center gap-1.5 cursor-pointer shrink-0"
            style={{
              backgroundColor: 'var(--panel)',
              borderColor: 'var(--border)',
              color: 'var(--text-primary)',
            }}
          >
            <RefreshCw size={13} aria-hidden="true" />
            Retry
          </button>
        </div>
      )}

      {liveStatus.restartNotice && (
        <div
          className="px-4 py-2 border-b flex items-center justify-between gap-3 text-[13px]"
          style={{
            backgroundColor: 'var(--surface-alt)',
            borderColor: 'var(--border)',
            color: 'var(--text-primary)',
          }}
        >
          <span>{liveStatus.restartNotice}</span>
          <button
            type="button"
            onClick={onDismissRestartNotice}
            aria-label="Dismiss restart notice"
            className="p-1 rounded-[4px] cursor-pointer"
            style={{ color: 'var(--text-muted)' }}
          >
            <X size={14} aria-hidden="true" />
          </button>
        </div>
      )}

      {runNotice && (
        <div
          className="px-4 py-2 border-b flex items-center justify-between gap-3 text-[13px]"
          style={{
            backgroundColor: 'var(--surface-alt)',
            borderColor: 'var(--border)',
            color: 'var(--text-primary)',
          }}
        >
          <span className="flex items-center gap-2">
            <span
              className="font-mono-data font-medium"
              style={{
                color:
                  runNotice.tone === 'success'
                    ? 'var(--role-success)'
                    : runNotice.tone === 'error'
                      ? 'var(--role-rejected)'
                      : runNotice.tone === 'warning'
                        ? 'var(--role-partial)'
                        : 'var(--accent)',
              }}
            >
              {runNotice.tone === 'success'
                ? 'Completed'
                : runNotice.tone === 'error'
                  ? 'Error'
                  : runNotice.tone === 'warning'
                    ? 'Notice'
                    : 'Running'}
            </span>
            <span aria-hidden="true">·</span>
            <span>{runNotice.message}</span>
          </span>
          <button
            type="button"
            onClick={onDismissRunNotice}
            aria-label="Dismiss scenario notice"
            className="p-1 rounded-[4px] cursor-pointer"
            style={{ color: 'var(--text-muted)' }}
          >
            <X size={14} aria-hidden="true" />
          </button>
        </div>
      )}
    </>
  );
};
