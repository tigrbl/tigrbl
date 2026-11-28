import React from 'react';
import { WorkspaceMetrics } from '../adapter/traceAdapter';
import { PROTOCOL_LABELS } from '../theme/tokens';
import { PrimaryProtocol } from '../types/trace';

interface ProtocolSummaryRowProps {
  metrics: WorkspaceMetrics;
  activeProtocols: PrimaryProtocol[];
  hasData: boolean;
  onToggleProtocol: (protocol: PrimaryProtocol) => void;
}

const PROTOCOLS: Array<{ id: PrimaryProtocol; subtitle: string }> = [
  { id: 'rest', subtitle: 'Request/response & DB write' },
  { id: 'http_jsonrpc', subtitle: 'RPC exchange & batch items' },
  { id: 'websocket', subtitle: 'Subscribe, publish & delivery' },
  { id: 'webtransport', subtitle: 'QUIC sessions, streams & datagrams' },
];

export const ProtocolSummaryRow: React.FC<ProtocolSummaryRowProps> = ({
  metrics,
  activeProtocols,
  hasData,
  onToggleProtocol,
}) => {
  return (
    <section
      aria-label="Protocol summaries"
      className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3"
    >
      {PROTOCOLS.map(({ id, subtitle }) => {
        const info = metrics.protocolSummary[id];
        const isActive = activeProtocols.includes(id);

        return (
          <button
            key={id}
            type="button"
            aria-pressed={isActive}
            onClick={() => onToggleProtocol(id)}
            className={`text-left px-3.5 py-3 rounded-[5px] border lab-transition cursor-pointer row-hover ${
              isActive ? 'row-selected' : ''
            }`}
            style={{
              backgroundColor: isActive ? 'var(--selected-bg)' : 'var(--panel)',
              borderColor: isActive ? 'var(--accent)' : 'var(--border)',
            }}
          >
            <div className="flex items-baseline justify-between gap-2">
              <span
                className="text-[14px] font-semibold tracking-[-0.01em]"
                style={{ color: 'var(--text-primary)' }}
              >
                {PROTOCOL_LABELS[id]}
              </span>
              <span
                className="font-mono-data text-[13px] font-medium"
                style={{ color: hasData ? 'var(--text-primary)' : 'var(--text-muted)' }}
              >
                {hasData ? `${info.events} ev` : '—'}
              </span>
            </div>

            <div
              className="mt-1 text-[12px] leading-[16px] truncate"
              style={{ color: 'var(--text-muted)' }}
            >
              {hasData ? info.highlight : subtitle}
            </div>

            {hasData && info.errors > 0 && (
              <div
                className="mt-1.5 text-[12px] font-mono-data"
                style={{ color: 'var(--role-rejected)' }}
              >
                {info.errors} rejected / failed
              </div>
            )}
          </button>
        );
      })}
    </section>
  );
};
