import React from 'react';
import { protocolLabel } from '../core/correlationEngine';
import type { OutcomeStatus, TransportProtocol } from '../core/types';

export function protocolColorVar(protocol: TransportProtocol): string {
  switch (protocol) {
    case 'rest':
      return 'var(--proto-rest)';
    case 'jsonrpc':
      return 'var(--proto-rpc)';
    case 'websocket':
      return 'var(--proto-ws)';
    case 'webtransport':
      return 'var(--proto-wt)';
    case 'unknown':
      return 'var(--text-muted)';
  }
}

export function ProtocolTag({ protocol }: { protocol: TransportProtocol }) {
  const color = protocolColorVar(protocol);
  return (
    <span className="inline-flex items-center gap-1.5 font-mono-tabular text-[11.5px] font-medium whitespace-nowrap shrink-0">
      <span
        className="inline-block w-2 h-2 rounded-[2px] shrink-0"
        style={{ backgroundColor: color }}
        aria-hidden="true"
      />
      <span style={{ color }}>{protocolLabel(protocol)}</span>
    </span>
  );
}

export function outcomeDisplay(outcome: OutcomeStatus): {
  label: string;
  color: string;
  symbol: string;
} {
  switch (outcome) {
    case 'ok':
      return { label: 'OK', color: 'var(--status-ok)', symbol: '●' };
    case 'observed':
      return { label: 'Observed', color: 'var(--status-info)', symbol: '○' };
    case 'error':
      return { label: 'Error', color: 'var(--status-err)', symbol: '✕' };
    case 'no_reply_expected':
      return { label: 'No reply expected', color: 'var(--status-info)', symbol: '○' };
    case 'reply_not_observed':
      return { label: 'Reply not observed', color: 'var(--status-warn)', symbol: '△' };
    case 'incomplete':
      return { label: 'Incomplete', color: 'var(--status-warn)', symbol: '◌' };
    case 'partial':
      return { label: 'Partial', color: 'var(--status-warn)', symbol: '◐' };
  }
}

export function OutcomeLabel({
  outcome,
  overrideLabel,
}: {
  outcome: OutcomeStatus;
  overrideLabel?: string;
}) {
  const info = outcomeDisplay(outcome);
  const text =
    outcome === 'error' && overrideLabel && !/error|fail/i.test(overrideLabel)
      ? `Error · ${overrideLabel}`
      : overrideLabel ?? info.label;
  return (
    <span
      className="inline-flex items-center gap-1 text-[12px] font-medium whitespace-nowrap shrink-0"
      style={{ color: info.color }}
    >
      <span aria-hidden="true" className="text-[10px]">
        {info.symbol}
      </span>
      <span>{text}</span>
    </span>
  );
}
