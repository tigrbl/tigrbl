import React, { useState } from 'react';
import { ArrowUpRight, Copy, X } from 'lucide-react';
import { formatUtcTime, protocolLabel, scopeLabel } from '../core/correlationEngine';
import type {
  CorrelationGroup,
  WaterfallEdge,
  WaterfallMark,
} from '../core/types';
import { OutcomeLabel } from './StatusIndicator';

interface WaterfallInspectorProps {
  group: CorrelationGroup;
  selectedMark: WaterfallMark | null;
  selectedEdge: WaterfallEdge | null;
  visibleEdges: WaterfallEdge[];
  onSelectEdge: (edge: WaterfallEdge) => void;
  onFollowRelated: (groupKey: string) => void;
  onClose?: () => void;
  showCloseButton?: boolean;
}

export function WaterfallInspector({
  group,
  selectedMark,
  selectedEdge,
  visibleEdges,
  onSelectEdge,
  onFollowRelated,
  onClose,
  showCloseButton = false,
}: WaterfallInspectorProps) {
  const [copiedKey, setCopiedKey] = useState<string | null>(null);
  const [showAllEdgesText, setShowAllEdgesText] = useState(false);

  const handleCopy = (label: string, val: string) => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(val).catch(() => {});
    }
    setCopiedKey(label);
    setTimeout(() => setCopiedKey(null), 1400);
  };

  const renderIdRow = (label: string, value?: string) => {
    if (!value) return null;
    return (
      <div
        key={label}
        className="flex items-center justify-between gap-2 py-1 border-b text-[12px]"
        style={{ borderColor: 'var(--border-rule)' }}
      >
        <span style={{ color: 'var(--text-muted)' }}>{label}</span>
        <div className="flex items-center gap-1.5 min-w-0">
          <span className="font-mono-tabular truncate max-w-[170px]" title={value}>
            {value}
          </span>
          <button
            type="button"
            onClick={() => handleCopy(label, value)}
            aria-label={`Copy ${label}`}
            className="p-1 rounded-[3px] hover:opacity-80 cursor-pointer shrink-0"
            style={{ color: copiedKey === label ? 'var(--status-ok)' : 'var(--text-muted)' }}
          >
            <Copy className="w-3 h-3" />
          </button>
        </div>
      </div>
    );
  };

  return (
    <aside
      aria-label="Handoff and event inspector"
      className="flex flex-col h-full overflow-hidden border-l"
      style={{
        backgroundColor: 'var(--bg-panel)',
        borderColor: 'var(--border-rule)',
      }}
    >
      <div
        className="flex items-center justify-between gap-2 px-4 py-2.5 border-b shrink-0"
        style={{ borderColor: 'var(--border-rule)' }}
      >
        <h2 className="text-[13px] font-semibold tracking-tight">
          {selectedEdge
            ? 'Selected handoff'
            : selectedMark
            ? 'Selected event mark'
            : 'Correlation summary'}
        </h2>
        {showCloseButton && onClose && (
          <button
            type="button"
            onClick={onClose}
            aria-label="Close inspector"
            className="p-1.5 rounded-[4px] hover:opacity-80 cursor-pointer min-w-[36px] min-h-[36px] flex items-center justify-center"
            style={{ color: 'var(--text-secondary)' }}
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-3 space-y-4">
        {/* Selected Edge Details */}
        {selectedEdge && (
          <div className="space-y-3">
            <div
              className="p-3 rounded-[5px] border"
              style={{
                backgroundColor: 'var(--bg-canvas)',
                borderColor: 'var(--border-rule)',
              }}
            >
              <div className="text-[11px] font-mono-tabular mb-1" style={{ color: 'var(--text-muted)' }}>
                From → To
              </div>
              <div className="text-[13px] font-semibold leading-snug">
                {selectedEdge.fromLabel} → {selectedEdge.toLabel}
              </div>
              <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-[12px]">
                <OutcomeLabel outcome={selectedEdge.outcome} />
                <span style={{ color: 'var(--text-muted)' }}>·</span>
                <span style={{ color: 'var(--text-secondary)' }}>{selectedEdge.direction}</span>
              </div>
            </div>

            {selectedEdge.clockOrderUncertain && (
              <div
                className="px-3 py-2 rounded-[4px] border text-[12px]"
                style={{
                  borderColor: 'var(--status-warn)',
                  color: 'var(--status-warn)',
                }}
              >
                <strong>Clock order uncertain:</strong> Explicit link retained without flipping direction or deriving elapsed time.
              </div>
            )}

            {selectedEdge.reason && (
              <div className="text-[12px]" style={{ color: 'var(--text-secondary)' }}>
                <span style={{ color: 'var(--text-muted)' }}>Basis / reason: </span>
                {selectedEdge.reason}
              </div>
            )}

            <div className="space-y-1 text-[12px]">
              <div className="flex justify-between py-1 border-b" style={{ borderColor: 'var(--border-rule)' }}>
                <span style={{ color: 'var(--text-muted)' }}>Recorded start</span>
                <span className="font-mono-tabular">{formatUtcTime(selectedEdge.startAtMs)} UTC</span>
              </div>
              <div className="flex justify-between py-1 border-b" style={{ borderColor: 'var(--border-rule)' }}>
                <span style={{ color: 'var(--text-muted)' }}>Recorded target</span>
                <span className="font-mono-tabular">{formatUtcTime(selectedEdge.endAtMs)} UTC</span>
              </div>
              <div className="flex justify-between py-1 border-b" style={{ borderColor: 'var(--border-rule)' }}>
                <span style={{ color: 'var(--text-muted)' }}>Time basis</span>
                <span className="font-mono-tabular">
                  {selectedEdge.clockOrderUncertain
                    ? 'Clock skewed'
                    : selectedEdge.timeBasis === 'measured_monotonic'
                    ? 'Measured monotonic'
                    : 'Recorded at'}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b" style={{ borderColor: 'var(--border-rule)' }}>
                <span style={{ color: 'var(--text-muted)' }}>Measured duration</span>
                <span className="font-mono-tabular">
                  {selectedEdge.measuredDurationMs !== undefined && !selectedEdge.clockOrderUncertain
                    ? `${selectedEdge.measuredDurationMs.toFixed(1)} ms`
                    : 'Unavailable'}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b" style={{ borderColor: 'var(--border-rule)' }}>
                <span style={{ color: 'var(--text-muted)' }}>Evidence rows</span>
                <span className="font-mono-tabular">
                  {selectedEdge.evidenceSequences.map((s) => `#${s}`).join(', ')}
                </span>
              </div>
            </div>

            {selectedEdge.relatedGroupKey && (
              <button
                type="button"
                onClick={() => onFollowRelated(selectedEdge.relatedGroupKey!)}
                className="w-full flex items-center justify-center gap-2 px-3 py-2 text-[12.5px] font-medium rounded-[5px] cursor-pointer min-h-[40px]"
                style={{
                  backgroundColor: 'var(--accent)',
                  color: 'var(--accent-text)',
                }}
              >
                <span>Follow related correlation</span>
                <ArrowUpRight className="w-4 h-4" />
              </button>
            )}
          </div>
        )}

        {/* Selected Mark Details */}
        {!selectedEdge && selectedMark && (
          <div className="space-y-3">
            <div
              className="p-3 rounded-[5px] border"
              style={{
                backgroundColor: 'var(--bg-canvas)',
                borderColor: 'var(--border-rule)',
              }}
            >
              <div className="flex items-center justify-between gap-2">
                <span className="font-mono-tabular text-[11px]" style={{ color: 'var(--text-muted)' }}>
                  seq #{selectedMark.seq} · {selectedMark.kind}
                </span>
                <OutcomeLabel outcome={selectedMark.outcome} />
              </div>
              <div className="mt-1 text-[13.5px] font-semibold">{selectedMark.label}</div>
              <div className="mt-1.5 flex flex-wrap items-center gap-2 text-[12px]">
                <span style={{ color: 'var(--text-secondary)' }}>{selectedMark.directionLabel}</span>
                <span style={{ color: 'var(--text-muted)' }}>·</span>
                <span
                  style={{
                    color:
                      selectedMark.provenance === 'Linked by evidence'
                        ? 'var(--accent)'
                        : 'var(--text-secondary)',
                  }}
                >
                  {selectedMark.provenance}
                </span>
              </div>
            </div>

            {selectedMark.reason && (
              <div
                className="px-3 py-2 rounded-[4px] border text-[12px]"
                style={{
                  borderColor: 'var(--status-warn)',
                  color: 'var(--status-warn)',
                }}
              >
                {selectedMark.reason}
              </div>
            )}

            <div className="space-y-0.5 text-[12px]">
              <div className="text-[11px] font-semibold mb-1" style={{ color: 'var(--text-muted)' }}>
                Timing & provenance
              </div>
              <div className="flex justify-between py-1 border-b" style={{ borderColor: 'var(--border-rule)' }}>
                <span style={{ color: 'var(--text-muted)' }}>Recorded at</span>
                <span className="font-mono-tabular">{formatUtcTime(selectedMark.event.atMs)} UTC</span>
              </div>
              <div className="flex justify-between py-1 border-b" style={{ borderColor: 'var(--border-rule)' }}>
                <span style={{ color: 'var(--text-muted)' }}>Time basis</span>
                <span className="font-mono-tabular">{selectedMark.timeBasis}</span>
              </div>
              {selectedMark.evidenceSequences && (
                <div className="flex flex-wrap justify-between gap-1 py-1 border-b" style={{ borderColor: 'var(--border-rule)' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Evidence rows</span>
                  <span className="font-mono-tabular">{selectedMark.evidenceSequences.map((seq) => `#${seq}`).join(', ')}</span>
                </div>
              )}
              {selectedMark.event.sourceStartedAt && (
                <div className="flex justify-between py-1 border-b" style={{ borderColor: 'var(--border-rule)' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Source start</span>
                  <span className="font-mono-tabular">
                    {formatUtcTime(selectedMark.event.sourceStartedAtMs ?? 0)}
                  </span>
                </div>
              )}
              {selectedMark.event.sourceEndedAt && (
                <div className="flex justify-between py-1 border-b" style={{ borderColor: 'var(--border-rule)' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Source end</span>
                  <span className="font-mono-tabular">
                    {formatUtcTime(selectedMark.event.sourceEndedAtMs ?? 0)}
                  </span>
                </div>
              )}
              <div className="flex justify-between py-1 border-b" style={{ borderColor: 'var(--border-rule)' }}>
                <span style={{ color: 'var(--text-muted)' }}>
                  {selectedMark.kind === 'round_trip' ? 'Round-trip duration'
                    : selectedMark.kind === 'db.tx.commit' || selectedMark.kind === 'db.tx.rollback'
                    ? 'Transaction duration'
                    : 'Measured duration'}
                </span>
                <span className="font-mono-tabular">
                  {selectedMark.measuredDurationMs !== undefined && !selectedMark.clockOrderUncertain
                    ? `${selectedMark.measuredDurationMs.toPrecision(3)} ms`
                    : selectedMark.kind === 'db.tx.begin' ? 'Start boundary' : 'Not measured'}
                </span>
              </div>
              <div className="py-1 border-b" style={{ borderColor: 'var(--border-rule)' }}>
                <div style={{ color: 'var(--text-muted)' }}>Linkage basis</div>
                <div className="mt-0.5 font-mono-tabular text-[11.5px]">{selectedMark.linkageBasis}</div>
              </div>
            </div>

            <div className="space-y-0.5">
              <div className="text-[11px] font-semibold mb-1" style={{ color: 'var(--text-muted)' }}>
                Typed identifiers
              </div>
              {renderIdRow('correlation_id', selectedMark.event.correlationId)}
              {renderIdRow('origin_correlation_id', selectedMark.event.originCorrelationId)}
              {renderIdRow('receiving_correlation_id', selectedMark.event.receivingCorrelationId)}
              {renderIdRow('request_id', selectedMark.event.requestId)}
              {renderIdRow('rpc_id', selectedMark.event.rpcId)}
              {renderIdRow('invocation_id', selectedMark.event.invocationId)}
              {renderIdRow('transport_session_id', selectedMark.event.transportSessionId)}
              {renderIdRow('requester_session_id', selectedMark.event.requesterSessionId)}
              {renderIdRow('quic_connection_id', selectedMark.event.quicConnectionId)}
              {renderIdRow('stream_id', selectedMark.event.streamId)}
              {renderIdRow('stream_correlation_id', selectedMark.event.streamCorrelationId)}
              {renderIdRow('datagram_id', selectedMark.event.datagramId)}
              {renderIdRow('subscription_id', selectedMark.event.subscriptionId)}
              {renderIdRow('attachment_generation', selectedMark.event.attachmentGeneration)}
              {renderIdRow('destination_id', selectedMark.event.destinationId)}
              {renderIdRow('transaction_key', selectedMark.event.transactionKey)}
            </div>

            {Object.keys(selectedMark.event.allowlistedMeta).length > 0 && (
              <div className="space-y-0.5">
                <div className="text-[11px] font-semibold mb-1" style={{ color: 'var(--text-muted)' }}>
                  Allowlisted metadata
                </div>
                {Object.entries(selectedMark.event.allowlistedMeta).map(([k, v]) => (
                  <div
                    key={k}
                    className="flex justify-between gap-2 py-1 border-b text-[12px]"
                    style={{ borderColor: 'var(--border-rule)' }}
                  >
                    <span style={{ color: 'var(--text-muted)' }}>{k}</span>
                    <span className="font-mono-tabular text-right break-all">{String(v)}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Default Group Summary when nothing is selected */}
        {!selectedEdge && !selectedMark && (
          <div className="space-y-3 text-[12px]">
            <p style={{ color: 'var(--text-secondary)' }}>
              Select any directional arrow or mark in the waterfall to inspect its{' '}
              <strong>From → To</strong> endpoints, provenance, time basis, and typed identifiers.
            </p>
            <div className="space-y-0.5">
              {renderIdRow('Scope', `${protocolLabel(group.protocol)} · ${scopeLabel(group.scope)}`)}
              {renderIdRow('correlation_id', group.scopeIdentity)}
              {renderIdRow('Discriminator', group.discriminator)}
              {renderIdRow('quic_connection_id', group.quicConnectionId)}
              {renderIdRow('transport_session_id', group.transportSessionId)}
              {renderIdRow('requester_session_id', group.requesterSessionId)}
              {renderIdRow('capture_id', group.captureId)}
            </div>
          </div>
        )}

        {/* Related Correlations (collapsed preview links, one action to follow) */}
        {group.relatedCorrelations.length > 0 && (
          <div className="pt-2 border-t" style={{ borderColor: 'var(--border-rule)' }}>
            <div className="text-[11.5px] font-semibold mb-2" style={{ color: 'var(--text-secondary)' }}>
              Related correlations ({group.relatedCorrelations.length})
            </div>
            <div className="space-y-1.5">
              {group.relatedCorrelations.map((rel) => (
                <div
                  key={rel.id}
                  className="p-2.5 rounded-[5px] border flex items-center justify-between gap-2"
                  style={{
                    backgroundColor: 'var(--bg-canvas)',
                    borderColor: 'var(--border-rule)',
                  }}
                >
                  <div className="min-w-0">
                    <div className="text-[12px] font-medium truncate">{rel.label}</div>
                    <div className="font-mono-tabular text-[10.5px]" style={{ color: 'var(--text-muted)' }}>
                      {protocolLabel(rel.targetProtocol)} · {rel.relationKind.replace(/_/g, ' ')}
                      {rel.attachmentGeneration ? ` · ${rel.attachmentGeneration}` : ''}
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => onFollowRelated(rel.targetGroupKey)}
                    className="inline-flex items-center gap-1 px-2.5 py-1.5 text-[11.5px] font-medium rounded-[4px] border shrink-0 cursor-pointer hover:opacity-90"
                    style={{
                      borderColor: 'var(--accent)',
                      color: 'var(--accent)',
                    }}
                  >
                    <span>Follow</span>
                    <ArrowUpRight className="w-3 h-3" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Accessible text representation of every visible edge in From -> To order */}
        <div className="pt-2 border-t" style={{ borderColor: 'var(--border-rule)' }}>
          <button
            type="button"
            onClick={() => setShowAllEdgesText((v) => !v)}
            aria-expanded={showAllEdgesText}
            className="w-full flex items-center justify-between py-1 text-[11.5px] font-semibold cursor-pointer"
            style={{ color: 'var(--text-secondary)' }}
          >
            <span>Visible edges as text ({visibleEdges.length})</span>
            <span className="font-mono-tabular text-[11px]" style={{ color: 'var(--accent)' }}>
              {showAllEdgesText ? 'Hide' : 'Show'}
            </span>
          </button>
          {showAllEdgesText && (
            <ul className="mt-2 space-y-1.5" aria-label="Visible edges in From to To order">
              {visibleEdges.map((edge) => (
                <li key={edge.id}>
                  <button
                    type="button"
                    onClick={() => onSelectEdge(edge)}
                    className="w-full text-left px-2 py-1.5 rounded-[4px] font-mono-tabular text-[11px] hover:opacity-90 cursor-pointer border"
                    style={{
                      borderColor:
                        selectedEdge?.id === edge.id ? 'var(--accent)' : 'var(--border-rule)',
                      backgroundColor:
                        selectedEdge?.id === edge.id ? 'var(--accent-muted)' : 'var(--bg-canvas)',
                    }}
                  >
                    {edge.textSummary}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </aside>
  );
}
