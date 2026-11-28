import React, { useEffect, useMemo, useState } from 'react';
import {
  ArrowLeft,
  ArrowUpRight,
  Copy,
  PanelRight,
  Pin,
  ZoomIn,
  ZoomOut,
} from 'lucide-react';
import {
  formatUtcTime,
  protocolLabel,
  scopeLabel,
} from '../core/correlationEngine';
import type {
  CorrelationGroup,
  CorrelationIndex,
  WaterfallEdge,
  WaterfallMark,
} from '../core/types';
import { buildWaterfallModel } from '../core/waterfallBuilder';
import { DirectionalWaterfall } from '../components/DirectionalWaterfall';
import { EventsTableView } from '../components/EventsTableView';
import { OutcomeLabel, ProtocolTag } from '../components/StatusIndicator';
import { WaterfallInspector } from '../components/WaterfallInspector';

const MIN_ZOOM_SPAN_MS = 4;
const ZOOM_FACTOR = 0.7;

interface CorrelationDetailViewProps {
  index: CorrelationIndex;
  group: CorrelationGroup;
  viewMode: 'waterfall' | 'events';
  showLinkedContext: boolean;
  selectedItem: { type: 'mark' | 'edge'; id: string } | null;
  zoomWindow: { startMs: number; endMs: number } | null;
  isPinned: boolean;
  rowHeight: number;
  onBack: () => void;
  onViewModeChange: (mode: 'waterfall' | 'events') => void;
  onToggleLinkedContext: (show: boolean) => void;
  onSelectItem: (item: { type: 'mark' | 'edge'; id: string } | null) => void;
  onZoomChange: (win: { startMs: number; endMs: number } | null) => void;
  onFollowRelated: (groupKey: string) => void;
  onTogglePin: (groupKey: string) => void;
}

export function CorrelationDetailView({
  index,
  group,
  viewMode,
  showLinkedContext,
  selectedItem,
  zoomWindow,
  isPinned,
  rowHeight,
  onBack,
  onViewModeChange,
  onToggleLinkedContext,
  onSelectItem,
  onZoomChange,
  onFollowRelated,
  onTogglePin,
}: CorrelationDetailViewProps) {
  const [collapsedLanes, setCollapsedLanes] = useState<Set<string>>(() => new Set());
  const [copiedId, setCopiedId] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [relatedMenuOpen, setRelatedMenuOpen] = useState(false);

  // Reset collapse state cleanly when switching to a different correlation group
  useEffect(() => {
    setCollapsedLanes(new Set());
    setRelatedMenuOpen(false);
  }, [group.groupKey]);

  const model = useMemo(
    () =>
      buildWaterfallModel(group, index, {
        showLinkedContext,
        collapsedLaneKeys: collapsedLanes,
        windowStartMs: zoomWindow?.startMs,
        windowEndMs: zoomWindow?.endMs,
      }),
    [group, index, showLinkedContext, collapsedLanes, zoomWindow]
  );

  const activeWindowStart = zoomWindow?.startMs ?? model.minTimeMs;
  const activeWindowEnd = zoomWindow?.endMs ?? model.maxTimeMs;
  const fullSpan = model.maxTimeMs - model.minTimeMs;
  const activeSpan = activeWindowEnd - activeWindowStart;
  const canZoomIn = activeSpan > MIN_ZOOM_SPAN_MS + 0.001;

  const selectedMark: WaterfallMark | null = useMemo(() => {
    if (selectedItem?.type !== 'mark') return null;
    const nodeId = selectedItem.id.replace(/^transaction-boundary-row-/, 'mark-');
    return model.marks.find((m) => m.id === selectedItem.id) ??
      model.marks.flatMap((m) => m.transactionBoundaries ?? []).find((node) => node.id === nodeId) ??
      model.marks.find((m) => m.evidenceSequences?.some((seq) => `mark-${seq}` === selectedItem.id)) ?? null;
  }, [selectedItem, model.marks]);

  const selectedEdge: WaterfallEdge | null = useMemo(() => {
    if (selectedItem?.type !== 'edge') return null;
    return model.edges.find((e) => e.id === selectedItem.id) ?? null;
  }, [selectedItem, model.edges]);

  const handleToggleLane = (laneKey: string) => {
    setCollapsedLanes((prev) => {
      const next = new Set(prev);
      if (next.has(laneKey)) next.delete(laneKey);
      else next.add(laneKey);
      return next;
    });
  };

  const zoomToSpan = (nextSpan: number) => {
    const center = (activeWindowStart + activeWindowEnd) / 2;
    if (nextSpan >= fullSpan - 0.001) {
      onZoomChange(null);
    } else {
      const start = Math.max(model.minTimeMs, Math.min(model.maxTimeMs - nextSpan, center - nextSpan / 2));
      onZoomChange({ startMs: start, endMs: start + nextSpan });
    }
  };

  const handlePan = (requestedStart: number) => {
    const start = Math.max(model.minTimeMs, Math.min(model.maxTimeMs - activeSpan, requestedStart));
    if (start !== activeWindowStart) {
      onZoomChange({ startMs: start, endMs: start + activeSpan });
    }
  };

  const handleCopyId = () => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(group.scopeIdentity).catch(() => {});
    }
    setCopiedId(true);
    setTimeout(() => setCopiedId(false), 1500);
  };

  const handleSelectMark = (mark: WaterfallMark) => {
    onSelectItem({ type: 'mark', id: mark.id });
    setDrawerOpen(true);
  };

  const handleSelectEdge = (edge: WaterfallEdge) => {
    onSelectItem({ type: 'edge', id: edge.id });
    setDrawerOpen(true);
  };

  const quicSiblings = group.relatedCorrelations.filter(
    (r) => r.relationKind === 'quic_sibling_session'
  );
  const { deliveryOutcomes } = group.metrics;

  return (
    <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
      {/* Sticky Correlation Header */}
      <section
        aria-label="Correlation header"
        className="px-4 sm:px-6 py-2.5 border-b shrink-0"
        style={{
          backgroundColor: 'var(--bg-panel)',
          borderColor: 'var(--border-rule)',
        }}
      >
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0 max-w-full">
            <button
              type="button"
              onClick={onBack}
              aria-label="Back to previous view"
              className="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-[12px] font-medium rounded-[4px] border cursor-pointer hover:opacity-90 shrink-0 min-h-[34px]"
              style={{
                borderColor: 'var(--border-strong)',
                color: 'var(--text-primary)',
              }}
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back</span>
            </button>

            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <ProtocolTag protocol={group.protocol} />
                <span className="text-[12px]" style={{ color: 'var(--text-muted)' }}>
                  {scopeLabel(group.scope)}
                </span>
                <h1 title={group.scopeIdentity} className="font-mono-tabular text-[15px] font-semibold max-w-full truncate">
                  {group.scopeIdentity}
                </h1>
                {group.discriminatorLabel && (
                  <span
                    className="font-mono-tabular text-[11.5px] max-w-full truncate"
                    title={group.discriminatorLabel}
                    style={{ color: 'var(--text-secondary)' }}
                  >
                    ({group.discriminatorLabel})
                  </span>
                )}
                <button
                  type="button"
                  onClick={handleCopyId}
                  aria-label="Copy correlation ID"
                  className="inline-flex items-center gap-1 px-2 py-0.5 text-[11.5px] border rounded-[4px] cursor-pointer hover:opacity-90"
                  style={{
                    borderColor: 'var(--border-rule)',
                    color: copiedId ? 'var(--status-ok)' : 'var(--text-secondary)',
                  }}
                >
                  <Copy className="w-3 h-3" />
                  <span>{copiedId ? 'Copied' : 'Copy ID'}</span>
                </button>
              </div>
              <div
                className="mt-0.5 flex flex-wrap items-center gap-x-2.5 gap-y-0.5 text-[11.5px] font-mono-tabular"
                style={{ color: 'var(--text-muted)' }}
              >
                <span>
                  Recorded {formatUtcTime(group.firstRecordedAtMs)} — {formatUtcTime(group.lastRecordedAtMs)} UTC
                </span>
                <span aria-hidden="true">·</span>
                <span>{group.service ? `${group.environment} / ${group.service}` : `capture ${group.captureId}`}</span>
                {group.quicConnectionId && (
                  <>
                    <span aria-hidden="true">·</span>
                    <span>QUIC {group.quicConnectionId}</span>
                  </>
                )}
                <span aria-hidden="true">·</span>
                {group.httpStatus !== undefined && (
                  <span className="font-semibold" style={{ color: 'var(--text-primary)' }}>{httpStatusLabel(group.httpStatus)} ·</span>
                )}
                <OutcomeLabel
                  outcome={group.outcomeSummary}
                  overrideLabel={group.metrics.coverage}
                />
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2 shrink-0">
            {/* QUIC sibling / Related correlations dropdown */}
            {group.relatedCorrelations.length > 0 && (
              <div className="relative">
                <button
                  type="button"
                  onClick={() => setRelatedMenuOpen((o) => !o)}
                  aria-expanded={relatedMenuOpen}
                  className="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-[12px] font-medium rounded-[4px] border cursor-pointer min-h-[34px] whitespace-nowrap"
                  style={{
                    borderColor: 'var(--accent)',
                    color: 'var(--accent)',
                    backgroundColor: 'var(--accent-muted)',
                  }}
                >
                  <span>
                    {quicSiblings.length > 0
                      ? `Related & QUIC siblings (${group.relatedCorrelations.length})`
                      : `Related correlations (${group.relatedCorrelations.length})`}
                  </span>
                  <ArrowUpRight className="w-3.5 h-3.5" />
                </button>

                {relatedMenuOpen && (
                  <div
                    role="menu"
                    className="absolute right-0 mt-1.5 w-80 max-w-[90vw] rounded-[6px] border p-2 z-30 shadow-lg space-y-1"
                    style={{
                      backgroundColor: 'var(--bg-panel-elevated)',
                      borderColor: 'var(--border-strong)',
                    }}
                  >
                    <div className="px-2 py-1 text-[11px] font-semibold" style={{ color: 'var(--text-muted)' }}>
                      Select a related correlation to navigate
                    </div>
                    {group.relatedCorrelations.map((rel) => (
                      <button
                        key={rel.id}
                        type="button"
                        role="menuitem"
                        onClick={() => {
                          setRelatedMenuOpen(false);
                          onFollowRelated(rel.targetGroupKey);
                        }}
                        className="w-full text-left px-2.5 py-2 rounded-[4px] hover:bg-[var(--bg-panel-hover)] cursor-pointer flex items-center justify-between gap-2"
                      >
                        <div className="min-w-0">
                          <div className="text-[12px] font-medium truncate">{rel.label}</div>
                          <div className="font-mono-tabular text-[10.5px]" style={{ color: 'var(--text-muted)' }}>
                            {protocolLabel(rel.targetProtocol)} · {rel.relationKind.replace(/_/g, ' ')}
                          </div>
                        </div>
                        <ArrowUpRight className="w-3.5 h-3.5 shrink-0" style={{ color: 'var(--accent)' }} />
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}

            <button
              type="button"
              onClick={() => onTogglePin(group.groupKey)}
              aria-pressed={isPinned}
              className="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-[12px] font-medium rounded-[4px] border cursor-pointer min-h-[34px] whitespace-nowrap"
              style={{
                borderColor: isPinned ? 'var(--accent)' : 'var(--border-rule)',
                color: isPinned ? 'var(--accent)' : 'var(--text-secondary)',
              }}
            >
              <Pin className="w-3.5 h-3.5" />
              <span>{isPinned ? 'Pinned' : 'Pin'}</span>
            </button>

            <button
              type="button"
              onClick={() => setDrawerOpen((o) => !o)}
              aria-label="Toggle inspector drawer"
              className="xl:hidden inline-flex items-center gap-1.5 px-2.5 py-1.5 text-[12px] font-medium rounded-[4px] border cursor-pointer min-h-[34px]"
              style={{
                borderColor: 'var(--border-strong)',
                color: 'var(--text-primary)',
              }}
            >
              <PanelRight className="w-3.5 h-3.5" />
              <span>Inspector</span>
            </button>
          </div>
        </div>

        {/* Compact 1-line summary on <640px mobile; full distinct typed-key metrics strip on sm+ */}
        <div
          className="mt-2 pt-2 border-t flex sm:hidden flex-wrap items-center gap-x-3 gap-y-1 font-mono-tabular text-[11.5px]"
          style={{ borderColor: 'var(--border-rule)', color: 'var(--text-secondary)' }}
        >
          <span><strong>{group.metrics.observedEvents}</strong> ev</span>
          <span><strong>{group.metrics.invocations}</strong> inv</span>
          <span><strong>{group.metrics.transactions}</strong> tx</span>
          {group.protocol === 'webtransport' && (
            <>
              <span><strong>{group.metrics.streams ?? 0}</strong> streams</span>
              <span><strong>{group.metrics.datagrams ?? 0}</strong> dgrams</span>
            </>
          )}
          {group.committedTransactions > 0 && (
            <span style={{ color: 'var(--status-ok)' }}>{group.committedTransactions} committed</span>
          )}
          {group.rolledBackTransactions > 0 && (
            <span style={{ color: 'var(--status-err)' }}>{group.rolledBackTransactions} rolled back</span>
          )}
          {deliveryOutcomes.error > 0 && (
            <span style={{ color: 'var(--status-err)' }}>{deliveryOutcomes.error} err</span>
          )}
        </div>

        <div
          className="hidden sm:grid mt-2.5 pt-2.5 border-t sm:grid-cols-4 lg:grid-cols-7 gap-3 text-[12px]"
          style={{ borderColor: 'var(--border-rule)' }}
        >
          <div>
            <div className="text-[11px]" style={{ color: 'var(--text-muted)' }}>Observed events</div>
            <div className="font-mono-tabular text-[14px] font-semibold">{group.metrics.observedEvents}</div>
          </div>
          <div>
            <div className="text-[11px]" style={{ color: 'var(--text-muted)' }}>Invocations</div>
            <div className="font-mono-tabular text-[14px] font-semibold">{group.metrics.invocations}</div>
          </div>
          <div>
            <div className="text-[11px]" style={{ color: 'var(--text-muted)' }}>Transactions</div>
            <div className="font-mono-tabular text-[14px] font-semibold">{group.metrics.transactions}</div>
          </div>
          <div className="col-span-2 sm:col-span-1 lg:col-span-2">
            <div className="text-[11px]" style={{ color: 'var(--text-muted)' }}>{group.httpStatus === undefined ? 'Observed outcomes' : 'Transaction outcomes'}</div>
            <div className="font-mono-tabular text-[12px] mt-0.5 flex flex-wrap gap-x-2.5 gap-y-0.5">
              {group.httpStatus === undefined && <span style={{ color: 'var(--status-ok)' }}>{deliveryOutcomes.ok} ok</span>}
              {group.committedTransactions > 0 && <span style={{ color: 'var(--status-ok)' }}>{group.committedTransactions} committed</span>}
              {group.rolledBackTransactions > 0 && <span style={{ color: 'var(--status-err)' }}>{group.rolledBackTransactions} rolled back</span>}
              {group.httpStatus !== undefined && !group.committedTransactions && !group.rolledBackTransactions && <span>—</span>}
              {deliveryOutcomes.error > 0 && (
                <span style={{ color: 'var(--status-err)' }}>{deliveryOutcomes.error} err</span>
              )}
              {deliveryOutcomes.noReplyExpected > 0 && (
                <span style={{ color: 'var(--status-info)' }}>
                  {deliveryOutcomes.noReplyExpected} no-reply
                </span>
              )}
              {deliveryOutcomes.replyNotObserved > 0 && (
                <span style={{ color: 'var(--status-warn)' }}>
                  {deliveryOutcomes.replyNotObserved} reply-not-observed
                </span>
              )}
              {deliveryOutcomes.incomplete > 0 && (
                <span style={{ color: 'var(--status-warn)' }}>
                  {deliveryOutcomes.incomplete} incomplete
                </span>
              )}
            </div>
          </div>
          {group.protocol === 'webtransport' ? (
            <>
              <div>
                <div className="text-[11px]" style={{ color: 'var(--text-muted)' }}>Streams</div>
                <div className="font-mono-tabular text-[14px] font-semibold">{group.metrics.streams ?? 0}</div>
              </div>
              <div>
                <div className="text-[11px]" style={{ color: 'var(--text-muted)' }}>Datagrams</div>
                <div className="font-mono-tabular text-[14px] font-semibold">{group.metrics.datagrams ?? 0}</div>
              </div>
            </>
          ) : (
            <div className="col-span-2">
              <div className="text-[11px]" style={{ color: 'var(--text-muted)' }}>Coverage</div>
              <div className="mt-0.5">
                <OutcomeLabel
                  outcome={group.outcomeSummary}
                  overrideLabel={group.metrics.coverage}
                />
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Secondary Detail Control Strip: Waterfall/Events, Linked Context, Zoom */}
      <div
        className="flex flex-wrap items-center justify-between gap-2 px-4 sm:px-6 py-1.5 border-b shrink-0"
        style={{
          backgroundColor: 'var(--bg-panel-elevated)',
          borderColor: 'var(--border-rule)',
        }}
      >
        <div className="flex flex-wrap items-center gap-2">
          <div
            className="inline-flex p-0.5 rounded-[4px] border"
            style={{
              backgroundColor: 'var(--bg-canvas)',
              borderColor: 'var(--border-rule)',
            }}
            role="tablist"
            aria-label="Investigation surface"
          >
            <button
              type="button"
              role="tab"
              aria-selected={viewMode === 'waterfall'}
              onClick={() => onViewModeChange('waterfall')}
              className="px-3 py-1 text-[12px] font-medium rounded-[3px] cursor-pointer whitespace-nowrap"
              style={{
                backgroundColor: viewMode === 'waterfall' ? 'var(--accent)' : 'transparent',
                color: viewMode === 'waterfall' ? 'var(--accent-text)' : 'var(--text-secondary)',
              }}
            >
              Waterfall
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={viewMode === 'events'}
              onClick={() => onViewModeChange('events')}
              className="px-3 py-1 text-[12px] font-medium rounded-[3px] cursor-pointer whitespace-nowrap"
              style={{
                backgroundColor: viewMode === 'events' ? 'var(--accent)' : 'transparent',
                color: viewMode === 'events' ? 'var(--accent-text)' : 'var(--text-secondary)',
              }}
            >
              Events ({model.marks.length})
            </button>
          </div>

          {model.hasLinkedContext && (
            <label className="inline-flex items-center gap-2 text-[12px] cursor-pointer px-2 py-1 select-none">
              <input
                type="checkbox"
                checked={showLinkedContext}
                onChange={(e) => onToggleLinkedContext(e.target.checked)}
                className="accent-[var(--accent)]"
              />
              <span style={{ color: 'var(--text-secondary)' }}>
                Show linked context (muted)
              </span>
            </label>
          )}
        </div>

        <div className="ml-auto flex shrink-0 items-center gap-1.5" role="group" aria-label="Timeline zoom">
          <button
            type="button"
            onClick={() => zoomToSpan(Math.max(MIN_ZOOM_SPAN_MS, activeSpan * ZOOM_FACTOR))}
            disabled={!canZoomIn}
            title="Zoom in"
            aria-label="Zoom in time window"
            className="inline-flex items-center gap-1 px-2 py-1 text-[12px] border rounded-[4px] cursor-pointer enabled:hover:opacity-90 disabled:cursor-default disabled:opacity-50"
            style={{
              borderColor: 'var(--border-rule)',
              color: 'var(--text-primary)',
              backgroundColor: 'var(--bg-panel)',
            }}
          >
            <ZoomIn className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Zoom in</span>
          </button>
          <button
            type="button"
            onClick={() => zoomToSpan(activeSpan / ZOOM_FACTOR)}
            disabled={zoomWindow === null}
            title="Zoom out"
            aria-label="Zoom out time window"
            className="inline-flex items-center gap-1 px-2 py-1 text-[12px] border rounded-[4px] cursor-pointer enabled:hover:opacity-90 disabled:cursor-default disabled:opacity-50"
            style={{
              borderColor: 'var(--border-rule)',
              color: 'var(--text-primary)',
              backgroundColor: 'var(--bg-panel)',
            }}
          >
            <ZoomOut className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Zoom out</span>
          </button>
          <button
            type="button"
            onClick={() => onZoomChange(null)}
            disabled={zoomWindow === null}
            className="px-2 py-1 text-[11.5px] font-mono-tabular border rounded-[4px] cursor-pointer disabled:cursor-default disabled:opacity-50"
            style={{
              borderColor: 'var(--accent)',
              color: 'var(--accent)',
            }}
          >
            Reset zoom
          </button>
        </div>
      </div>

      {/* Main Content Area: Waterfall / Events + Responsive Inspector */}
      <div className="flex-1 flex min-h-0 overflow-hidden relative">
        <div className="flex-1 flex flex-col min-w-0 min-h-0 overflow-hidden">
          {viewMode === 'waterfall' ? (
            <DirectionalWaterfall
              model={model}
              windowStartMs={activeWindowStart}
              windowEndMs={activeWindowEnd}
              onPan={handlePan}
              rowHeight={rowHeight}
              collapsedLaneKeys={collapsedLanes}
              onToggleLane={handleToggleLane}
              selectedItem={selectedItem}
              onSelectMark={handleSelectMark}
              onSelectEdge={handleSelectEdge}
              onFollowRelated={onFollowRelated}
            />
          ) : (
            <EventsTableView
              marks={model.marks}
              selectedMarkId={selectedMark?.id ?? null}
              rowHeight={rowHeight}
              onSelectMark={handleSelectMark}
            />
          )}
        </div>

        {/* Desktop >= 1280px Inspector Rail (360px) */}
        <div className="hidden xl:block w-[360px] shrink-0 h-full overflow-hidden">
          <WaterfallInspector
            group={group}
            selectedMark={selectedMark}
            selectedEdge={selectedEdge}
            visibleEdges={model.edges}
            onSelectEdge={handleSelectEdge}
            onFollowRelated={onFollowRelated}
          />
        </div>

        {/* Tablet Drawer (768-1279px) & Mobile Full-Height Details Sheet (<768px) */}
        {drawerOpen && (
          <div className="xl:hidden fixed inset-0 z-40 flex justify-end">
            <div
              className="fixed inset-0 bg-black/50"
              onClick={() => setDrawerOpen(false)}
              aria-hidden="true"
            />
            <div className="relative z-10 w-full sm:w-[380px] h-full shadow-2xl">
              <WaterfallInspector
                group={group}
                selectedMark={selectedMark}
                selectedEdge={selectedEdge}
                visibleEdges={model.edges}
                onSelectEdge={handleSelectEdge}
                onFollowRelated={(key) => {
                  setDrawerOpen(false);
                  onFollowRelated(key);
                }}
                showCloseButton
                onClose={() => setDrawerOpen(false)}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
import { httpStatusLabel } from '../core/correlationEngine';
