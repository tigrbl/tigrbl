import React, { useEffect, useId, useLayoutEffect, useMemo, useRef, useState } from 'react';
import {
  ArrowUpRight,
  ChevronRight,
  Database,
  Radio,
} from 'lucide-react';
import { formatUtcTime } from '../core/correlationEngine';
import { computeEdgeGeometry, groupTimelineNodes } from '../core/waterfallGeometry';
import type {
  WaterfallEdge,
  WaterfallLane,
  WaterfallMark,
  WaterfallModel,
} from '../core/types';
import { OutcomeLabel, outcomeDisplay } from './StatusIndicator';
import { EventTooltip } from '../../components/EventTooltip';

interface DirectionalWaterfallProps {
  model: WaterfallModel;
  windowStartMs: number;
  windowEndMs: number;
  onPan: (startMs: number) => void;
  rowHeight: number;
  collapsedLaneKeys: Set<string>;
  onToggleLane: (laneKey: string) => void;
  selectedItem: { type: 'mark' | 'edge'; id: string } | null;
  onSelectMark: (mark: WaterfallMark) => void;
  onSelectEdge: (edge: WaterfallEdge) => void;
  onFollowRelated: (groupKey: string) => void;
}

interface MarkPreview {
  mark: WaterfallMark;
  element: Element;
}

interface NodeBucket {
  laneKey: string;
  nodes: WaterfallMark[];
  x: number;
  width: number;
}

function bucketKey(bucket: NodeBucket): string {
  return `${bucket.laneKey}:${bucket.nodes[0].id}`;
}

export function DirectionalWaterfall({
  model,
  windowStartMs,
  windowEndMs,
  onPan,
  rowHeight,
  collapsedLaneKeys,
  onToggleLane,
  selectedItem,
  onSelectMark,
  onSelectEdge,
  onFollowRelated,
}: DirectionalWaterfallProps) {
  const [hoveredMark, setHoveredMark] = useState<MarkPreview | null>(null);
  const [focusedMark, setFocusedMark] = useState<MarkPreview | null>(null);
  const [tooltipDismissed, setTooltipDismissed] = useState(false);
  const [cursor, setCursor] = useState<{ x: number; y: number } | null>(null);
  const [bucketPreview, setBucketPreview] = useState<{
    key: string;
    element: SVGElement;
    cursor?: { x: number; y: number };
  } | null>(null);
  const [hoveredEdgeId, setHoveredEdgeId] = useState<string | null>(null);
  const [focusedMarkId, setFocusedMarkId] = useState<string | null>(null);
  const [focusedEdgeId, setFocusedEdgeId] = useState<string | null>(null);
  const [crosshairMs, setCrosshairMs] = useState<number | null>(null);
  const [mobileMode, setMobileMode] = useState<'handoffs' | 'plot'>('handoffs');
  const [plotWidth, setPlotWidth] = useState<number>(820);
  const [viewportWidth, setViewportWidth] = useState(0);
  const roundTripCollapsed = collapsedLaneKeys.has('lane:round_trip');
  const scrollContainerRef = useRef<HTMLDivElement | null>(null);
  const plotContainerRef = useRef<HTMLDivElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const tooltipId = useId();
  const hover = hoveredMark?.element.isConnected ? hoveredMark : null;
  const preview = tooltipDismissed ? null : hover ?? focusedMark;

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setTooltipDismissed(true);
        setBucketPreview(null);
      }
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, []);

  const markPreviewHandlers = (mark: WaterfallMark) => ({
    'aria-describedby': preview?.mark.id === mark.id ? tooltipId : undefined,
    onMouseEnter: (event: React.MouseEvent<Element>) => {
      setHoveredMark({ mark, element: event.currentTarget });
      setCursor({ x: event.clientX, y: event.clientY });
      setTooltipDismissed(false);
      setCrosshairMs(mark.atMs);
    },
    onMouseMove: (event: React.MouseEvent<Element>) => {
      setCursor({ x: event.clientX, y: event.clientY });
    },
    onMouseLeave: () => setHoveredMark((current) => current?.mark.id === mark.id ? null : current),
    onFocus: (event: React.FocusEvent<Element>) => {
      setHoveredMark(null);
      setFocusedMarkId(mark.id);
      setFocusedMark({ mark, element: event.currentTarget });
      setTooltipDismissed(false);
    },
    onBlur: () => {
      setFocusedMarkId((current) => current === mark.id ? null : current);
      setFocusedMark((current) => current?.mark.id === mark.id ? null : current);
    },
  });

  useEffect(() => {
    const plot = plotContainerRef.current;
    const viewport = scrollContainerRef.current;
    if (!plot || !viewport) return;
    const measure = () => {
      setViewportWidth(viewport.clientWidth);
      setPlotWidth(Math.max(96, Math.round(plot.getBoundingClientRect().width)));
    };
    measure();
    const ro = new ResizeObserver(measure);
    ro.observe(viewport);
    ro.observe(plot);
    return () => ro.disconnect();
  }, []);

  const laneByKey = useMemo(() => {
    const map = new Map<string, WaterfallLane>();
    for (const lane of model.lanes) map.set(lane.laneKey, lane);
    return map;
  }, [model.lanes]);

  // Compute visible lanes based on accordion collapse state
  const visibleLanes = useMemo(() => {
    const out: WaterfallLane[] = [];
    for (const lane of model.lanes) {
      let hidden = false;
      let curr = lane.parentKey;
      while (curr) {
        if (collapsedLaneKeys.has(curr)) {
          hidden = true;
          break;
        }
        curr = laneByKey.get(curr)?.parentKey;
      }
      if (!hidden) out.push(lane);
    }
    return out;
  }, [model.lanes, collapsedLaneKeys, laneByKey]);

  const laneIndexMap = useMemo(() => {
    const map = new Map<string, number>();
    visibleLanes.forEach((l, i) => map.set(l.laneKey, i));
    return map;
  }, [visibleLanes]);

  // Resolve a lane key to itself or its nearest visible collapsed ancestor
  const resolveVisibleLaneIndex = (laneKey: string): { idx: number; collapsedAncestor: boolean } => {
    const direct = laneIndexMap.get(laneKey);
    if (direct !== undefined) return { idx: direct, collapsedAncestor: false };
    let curr = laneByKey.get(laneKey)?.parentKey;
    while (curr) {
      const parentIdx = laneIndexMap.get(curr);
      if (parentIdx !== undefined) return { idx: parentIdx, collapsedAncestor: true };
      curr = laneByKey.get(curr)?.parentKey;
    }
    return { idx: 0, collapsedAncestor: true };
  };

  // Aggregated marks for collapsed parent lanes
  const collapsedAggregateMarks = useMemo(() => {
    const agg = new Map<string, WaterfallMark[]>();
    for (const lane of visibleLanes) {
      if (!collapsedLaneKeys.has(lane.laneKey) || lane.kind === 'round_trip') continue;
      // Collect descendant marks
      const descendants: WaterfallMark[] = lane.collapseToTimeline ? [...lane.marks] : [];
      const queue = [...lane.childrenKeys];
      while (queue.length > 0) {
        const key = queue.shift()!;
        const child = laneByKey.get(key);
        if (!child) continue;
        descendants.push(...child.marks);
        queue.push(...child.childrenKeys);
      }
      agg.set(lane.laneKey, descendants);
    }
    return agg;
  }, [visibleLanes, collapsedLaneKeys, laneByKey]);

  const timeSpan = Math.max(1, windowEndMs - windowStartMs);
  const panRange = Math.max(0, model.maxTimeMs - model.minTimeMs - (windowEndMs - windowStartMs));
  const panPixels = panRange > 0
    ? Math.max(1, Math.min(1_000_000, Math.round((plotWidth - 48) * panRange / timeSpan)))
    : 0;
  const panFraction = panRange > 0 ? (windowStartMs - model.minTimeMs) / panRange : 0;
  const scrollPosition = Math.round(Math.max(0, Math.min(1, panFraction)) * panPixels);

  useLayoutEffect(() => {
    const viewport = scrollContainerRef.current;
    if (viewport && viewport.scrollLeft !== scrollPosition) viewport.scrollLeft = scrollPosition;
  }, [scrollPosition, panPixels, viewportWidth, mobileMode]);

  useEffect(() => {
    const container = scrollContainerRef.current;
    if (!container || !panPixels) return;
    const scrollOnShiftWheel = (event: WheelEvent) => {
      if (event.ctrlKey || !event.shiftKey || event.deltaX || !event.deltaY) return;
      event.preventDefault();
      const unit = event.deltaMode === WheelEvent.DOM_DELTA_LINE ? 16
        : event.deltaMode === WheelEvent.DOM_DELTA_PAGE ? container.clientWidth : 1;
      container.scrollLeft += event.deltaY * unit;
    };
    container.addEventListener('wheel', scrollOnShiftWheel, { passive: false });
    return () => container.removeEventListener('wheel', scrollOnShiftWheel);
  }, [panPixels]);

  const timeToX = (ms: number) => {
    const clamped = Math.max(windowStartMs - timeSpan * 0.05, Math.min(windowEndMs + timeSpan * 0.05, ms));
    return ((clamped - windowStartMs) / timeSpan) * (plotWidth - 48) + 24;
  };

  const laneCenterY = (idx: number) => idx * rowHeight + rowHeight / 2;
  const totalPlotHeight = Math.max(rowHeight * 2, visibleLanes.length * rowHeight);

  // 5 cleanly spaced ticks for the sticky time ruler (zero collision at any width)
  const rulerTicks = useMemo(() => {
    const count = 4;
    const ticks: Array<{ ms: number; pct: number; label: string; delta: string }> = [];
    for (let i = 0; i <= count; i++) {
      const ratio = i / count;
      const ms = windowStartMs + ratio * timeSpan;
      ticks.push({
        ms,
        pct: (timeToX(ms) / plotWidth) * 100,
        label: formatUtcTime(ms),
        delta: `+${Math.round(ms - model.minTimeMs)}ms`,
      });
    }
    return ticks;
  }, [windowStartMs, timeSpan, model.minTimeMs, plotWidth]);

  // Visible marks sorted chronologically for keyboard traversal
  const visibleMarks = useMemo(() => {
    const marks: WaterfallMark[] = [];
    for (const lane of visibleLanes) {
      if (!collapsedLaneKeys.has(lane.laneKey)) {
        marks.push(...lane.marks);
        continue;
      }
      const seen = new Set<string>();
      const addNode = (node: WaterfallMark) => {
        if (seen.has(node.id) || node.id.startsWith('transaction-boundary-row-')) return;
        seen.add(node.id);
        marks.push({
          ...node,
          laneKey: lane.laneKey,
          atMs: node.endAtMs ?? node.atMs,
          endAtMs: undefined,
          glyph: 'point',
          transactionBoundaries: undefined,
          stackOffset: 0,
          timelineNodeOffset: 0,
        });
      };
      const contents = lane.kind === 'round_trip'
        ? model.marks
        : new Set([...lane.marks, ...(collapsedAggregateMarks.get(lane.laneKey) ?? [])]);
      for (const mark of contents) {
        const isOwnBar = mark.laneKey === lane.laneKey && (
          mark.evidenceSequences || (!lane.collapseToTimeline && mark.glyph === 'interval')
        );
        if (isOwnBar) marks.push({ ...mark, stackOffset: 0, transactionBoundaries: undefined });
        else if (!mark.evidenceSequences) addNode(mark);
        for (const node of mark.transactionBoundaries ?? []) addNode(node);
      }
    }
    return marks.sort((a, b) => Number(b.timelineNodeOffset === undefined) - Number(a.timelineNodeOffset === undefined) ||
      a.atMs - b.atMs || a.seq - b.seq);
  }, [model.marks, visibleLanes, collapsedLaneKeys, collapsedAggregateMarks]);

  const bucketedMarks = new Set<WaterfallMark>();
  const nodeBuckets: NodeBucket[] = [];
  const collapsedNodesByLane = new Map<string, WaterfallMark[]>();
  for (const mark of visibleMarks) {
    if (mark.timelineNodeOffset === undefined || !collapsedLaneKeys.has(mark.laneKey)) continue;
    if (mark.atMs < windowStartMs || mark.atMs > windowEndMs) {
      bucketedMarks.add(mark);
      continue;
    }
    const nodes = collapsedNodesByLane.get(mark.laneKey) ?? [];
    nodes.push(mark);
    collapsedNodesByLane.set(mark.laneKey, nodes);
  }
  for (const [laneKey, nodes] of collapsedNodesByLane) {
    for (const bucket of groupTimelineNodes(nodes, (mark) => timeToX(mark.atMs))) {
      if (bucket.nodes.length < 2) continue;
      nodeBuckets.push({ ...bucket, laneKey });
      for (const mark of bucket.nodes) bucketedMarks.add(mark);
    }
  }
  const previewBucket = bucketPreview?.element.isConnected
    ? nodeBuckets.find((bucket) => bucketKey(bucket) === bucketPreview.key)
    : undefined;
  const navigableMarks = useMemo(() => visibleMarks
    .flatMap((mark) => [mark, ...(mark.transactionBoundaries ?? [])])
    .sort((a, b) => a.atMs - b.atMs || a.seq - b.seq), [visibleMarks]);

  const useDenseCanvas = visibleMarks.length > 400;

  // Dense point canvas rasterization fallback (> 400 marks)
  useEffect(() => {
    if (!useDenseCanvas || !canvasRef.current) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.clearRect(0, 0, plotWidth, totalPlotHeight);
    for (const mark of visibleMarks) {
      if (mark.evidenceSequences || mark.timelineNodeOffset !== undefined || mark.glyph === 'interval') continue;
      const idx = laneIndexMap.get(mark.laneKey);
      if (idx === undefined) continue;
      const x = timeToX(mark.atMs) + mark.stackOffset;
      const y = laneCenterY(idx);
      ctx.fillStyle = mark.outcome === 'error' ? '#e56b6f' : '#f0a454';
      ctx.beginPath();
      ctx.arc(x, y, 2.5, 0, Math.PI * 2);
      ctx.fill();
    }
  }, [useDenseCanvas, visibleMarks, laneIndexMap, totalPlotHeight, windowStartMs, windowEndMs, plotWidth]);

  const hoveredEdge = useMemo(
    () => (hoveredEdgeId ? model.edges.find((e) => e.id === hoveredEdgeId) ?? null : null),
    [hoveredEdgeId, model.edges]
  );

  // Keyboard traversal by time across marks
  const handlePlotKeyDown = (e: React.KeyboardEvent) => {
    if (navigableMarks.length === 0) return;
    const currentIdx =
      selectedItem?.type === 'mark'
        ? navigableMarks.findIndex((m) => m.id === selectedItem.id)
        : -1;

    if (e.key === 'ArrowRight') {
      e.preventDefault();
      const nextIdx = currentIdx < navigableMarks.length - 1 ? currentIdx + 1 : 0;
      const m = navigableMarks[nextIdx];
      setCrosshairMs(m.atMs);
      onSelectMark(m);
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault();
      const prevIdx = currentIdx > 0 ? currentIdx - 1 : navigableMarks.length - 1;
      const m = navigableMarks[prevIdx];
      setCrosshairMs(m.atMs);
      onSelectMark(m);
    }
  };

  // Mobile chronological handoffs grouped by From -> To
  const chronologicalHandoffs = useMemo(() => {
    return [...model.edges].sort((a, b) => a.startAtMs - b.startAtMs);
  }, [model.edges]);

  const laneIcon = (kind: WaterfallLane['kind']) => {
    if (kind === 'transactions_group' || kind === 'transaction_lane') {
      return <Database className="w-3.5 h-3.5 shrink-0" style={{ color: 'var(--status-info)' }} aria-hidden="true" />;
    }
    if (kind === 'datagrams_lane' || kind === 'streams_group' || kind === 'subscriptions_group') {
      return <Radio className="w-3.5 h-3.5 shrink-0" style={{ color: 'var(--accent)' }} aria-hidden="true" />;
    }
    return null;
  };

  return (
    <div className="flex-1 flex flex-col min-w-0 min-h-0">
      {/* Mobile (<768px) view switcher: leads with chronological handoffs list per brief */}
      <div
        className="flex md:hidden items-center justify-between gap-2 px-3 py-2 border-b"
        style={{
          backgroundColor: 'var(--bg-panel)',
          borderColor: 'var(--border-rule)',
        }}
      >
        <div
          className="inline-flex rounded-[4px] border p-0.5"
          style={{ borderColor: 'var(--border-rule)', backgroundColor: 'var(--bg-canvas)' }}
          role="tablist"
          aria-label="Mobile waterfall display"
        >
          <button
            type="button"
            role="tab"
            aria-selected={mobileMode === 'handoffs'}
            onClick={() => setMobileMode('handoffs')}
            className="px-3 py-1.5 text-[12px] font-medium rounded-[3px] min-h-[36px]"
            style={{
              backgroundColor: mobileMode === 'handoffs' ? 'var(--accent)' : 'transparent',
              color: mobileMode === 'handoffs' ? 'var(--accent-text)' : 'var(--text-secondary)',
            }}
          >
            Handoffs ({chronologicalHandoffs.length})
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={mobileMode === 'plot'}
            onClick={() => setMobileMode('plot')}
            className="px-3 py-1.5 text-[12px] font-medium rounded-[3px] min-h-[36px]"
            style={{
              backgroundColor: mobileMode === 'plot' ? 'var(--accent)' : 'transparent',
              color: mobileMode === 'plot' ? 'var(--accent-text)' : 'var(--text-secondary)',
            }}
          >
            Waterfall plot
          </button>
        </div>
        <span className="font-mono-tabular text-[11px] truncate" style={{ color: 'var(--text-muted)' }}>
          {model.marks.length} marks
        </span>
      </div>

      {/* Mobile chronological handoffs view (<768px when mobileMode === 'handoffs') */}
      <div className={`${mobileMode === 'handoffs' ? 'block md:hidden' : 'hidden'} flex-1 overflow-y-auto p-3 space-y-2`}>
        <div className="text-[11.5px] font-mono-tabular mb-2" style={{ color: 'var(--text-muted)' }}>
          {model.timeBasisSummary}
        </div>
        {chronologicalHandoffs.map((edge) => {
          const isSelected = selectedItem?.type === 'edge' && selectedItem.id === edge.id;
          return (
            <button
              key={edge.id}
              type="button"
              onClick={() => onSelectEdge(edge)}
              className="w-full text-left p-3 border rounded-[6px] transition-colors min-h-[44px]"
              style={{
                backgroundColor: isSelected ? 'var(--accent-muted)' : 'var(--bg-panel)',
                borderColor: isSelected ? 'var(--accent)' : 'var(--border-rule)',
              }}
            >
              <div className="flex items-center justify-between gap-2 text-[12px] font-medium">
                <span className="truncate">
                  {edge.fromLabel} → {edge.toLabel}
                </span>
                <OutcomeLabel outcome={edge.outcome} />
              </div>
              <div className="mt-1 flex flex-wrap items-center gap-2 font-mono-tabular text-[11px]" style={{ color: 'var(--text-muted)' }}>
                <span>{formatUtcTime(edge.startAtMs)}</span>
                <span>·</span>
                <span>{edge.direction}</span>
                {edge.clockOrderUncertain && (
                  <>
                    <span>·</span>
                    <span style={{ color: 'var(--status-warn)' }}>Clock order uncertain</span>
                  </>
                )}
                {edge.measuredDurationMs !== undefined && !edge.clockOrderUncertain && (
                  <>
                    <span>·</span>
                    <span>{edge.measuredDurationMs.toFixed(1)} ms</span>
                  </>
                )}
              </div>
              {edge.relatedGroupKey && (
                <div className="mt-2">
                  <span
                    className="inline-flex items-center gap-1 text-[11.5px] font-medium underline"
                    style={{ color: 'var(--accent)' }}
                  >
                    Follow related correlation <ArrowUpRight className="w-3 h-3" />
                  </span>
                </div>
              )}
            </button>
          );
        })}

        {/* Also list individual lane accordions for direct mark selection on narrow viewports */}
        <div className="pt-3 border-t" style={{ borderColor: 'var(--border-rule)' }}>
          <h3 className="text-[12px] font-semibold mb-2" style={{ color: 'var(--text-secondary)' }}>
            Lanes & recorded marks
          </h3>
          <div className="space-y-1.5">
            {visibleLanes.map((lane) => {
              const laneMarks = roundTripCollapsed && lane.kind === 'round_trip' ? visibleMarks : lane.marks;
              return (
              <div
                key={lane.laneKey}
                className="border rounded-[5px] overflow-hidden"
                style={{ borderColor: 'var(--border-rule)', backgroundColor: 'var(--bg-panel)' }}
              >
                <div className="flex items-center justify-between px-3 py-2 text-[12.5px] font-medium">
                  {lane.collapsible ? (
                    <button
                      type="button"
                      aria-expanded={!collapsedLaneKeys.has(lane.laneKey)}
                      onClick={() => onToggleLane(lane.laneKey)}
                      className="inline-flex items-center gap-1.5 text-left cursor-pointer"
                    >
                      <ChevronRight size={14} aria-hidden="true" className={collapsedLaneKeys.has(lane.laneKey) ? '' : 'rotate-90'} />
                      {lane.label}
                    </button>
                  ) : <span>{lane.label}</span>}
                  <span className="font-mono-tabular text-[11px]" style={{ color: 'var(--text-muted)' }}>
                    {laneMarks.reduce((count, mark) => count + 1 + (mark.transactionBoundaries?.length ?? 0), 0)} marks
                  </span>
                </div>
                {laneMarks.length > 0 && (
                  <div className="divide-y border-t" style={{ borderColor: 'var(--border-rule)' }}>
                    {laneMarks.flatMap((m) => [m, ...(m.transactionBoundaries ?? [])]).map((m) => (
                      <button
                        key={m.id}
                        type="button"
                        {...markPreviewHandlers(m)}
                        onClick={() => onSelectMark(m)}
                        className="w-full text-left px-3 py-2 flex items-center justify-between gap-2 text-[12px] min-h-[44px]"
                        style={{
                          backgroundColor:
                            selectedItem?.type === 'mark' && selectedItem.id === m.id
                              ? 'var(--accent-muted)'
                              : 'transparent',
                        }}
                      >
                        <span className="truncate">{m.label}</span>
                        <span className="font-mono-tabular text-[11px] shrink-0" style={{ color: 'var(--text-muted)' }}>
                          {formatUtcTime(m.atMs)}
                        </span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Desktop / Tablet (and Mobile Plot tab) Directional Waterfall Surface */}
      <div
        className={`${mobileMode === 'plot' ? 'flex' : 'hidden md:flex'} flex-1 flex-col min-w-0 min-h-0 overflow-hidden`}
      >
        {/* Single edge preview bar on focus/hover + time basis indicator */}
        <div
          className="flex items-center justify-between gap-3 px-3 py-1.5 border-b text-[11.5px] min-h-[28px]"
          style={{
            backgroundColor: 'var(--bg-canvas)',
            borderColor: 'var(--border-rule)',
            color: 'var(--text-secondary)',
          }}
        >
          <div className="truncate font-mono-tabular">
            {hoveredEdge ? (
              <span>
                <strong style={{ color: 'var(--accent)' }}>Preview:</strong> {hoveredEdge.textSummary}
                {hoveredEdge.clockOrderUncertain ? ' · Clock order uncertain' : ''}
              </span>
            ) : (
              <span>{model.timeBasisSummary}</span>
            )}
          </div>
          <div className="font-mono-tabular shrink-0 hidden sm:block" style={{ color: 'var(--text-muted)' }}>
            {crosshairMs !== null
              ? `Cursor ${formatUtcTime(crosshairMs)} UTC`
              : 'Use ← / → keys to step marks by time'}
          </div>
        </div>

        {/* Sticky Header: Label Column + Shared Time Ruler */}
        <div
          ref={scrollContainerRef}
          className="min-h-0 flex-1 overflow-auto overscroll-x-contain"
          data-testid="waterfall-scroll-container"
          role="region"
          aria-label="Scrollable waterfall timeline"
          tabIndex={0}
          onScroll={(event) => {
            const left = event.currentTarget.scrollLeft;
            if (!panPixels || Math.abs(left - scrollPosition) < 1) return;
            setCrosshairMs(null);
            setHoveredMark(null);
            setHoveredEdgeId(null);
            setBucketPreview(null);
            onPan(model.minTimeMs + Math.max(0, Math.min(1, left / panPixels)) * panRange);
          }}
        >
          {/* Scroll the time range while drawing only the visible plot and keeping lane labels in place. */}
          <div style={{ width: viewportWidth ? viewportWidth + panPixels : undefined }}>
            <div
              className="sticky left-0 top-0 z-20 grid grid-cols-[minmax(0,38%)_minmax(0,1fr)] border-b md:grid-cols-[minmax(0,272px)_minmax(0,1fr)]"
              style={{
                width: viewportWidth || undefined,
                backgroundColor: 'var(--bg-panel-elevated)',
                borderColor: 'var(--border-rule)',
              }}
            >
              <div
                className="px-3 py-2 text-[11.5px] font-semibold border-r flex items-center justify-between"
                style={{ borderColor: 'var(--border-rule)', color: 'var(--text-secondary)' }}
              >
                <span>Participant / lane</span>
                <span className="hidden font-mono-tabular font-normal text-[11px] sm:inline" style={{ color: 'var(--text-muted)' }}>
                  {visibleLanes.length} lanes
                </span>
              </div>

              <div className="relative h-9 select-none overflow-hidden" aria-label="Shared UTC time ruler">
                {rulerTicks.map((tick, idx) => (
                  <div
                    key={idx}
                    className="absolute top-0 bottom-0 flex flex-col justify-center"
                    style={{
                      left: `${tick.pct}%`,
                      transform:
                        idx === 0
                          ? 'translateX(0)'
                          : idx === rulerTicks.length - 1
                          ? 'translateX(-100%)'
                          : 'translateX(-50%)',
                    }}
                  >
                    <span className="font-mono-tabular text-[11px] whitespace-nowrap px-1" style={{ color: 'var(--text-primary)' }}>
                      {tick.label}
                    </span>
                    <span className="font-mono-tabular text-[10px] whitespace-nowrap px-1" style={{ color: 'var(--text-muted)' }}>
                      {tick.delta}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Body: Aligned HTML Label Rail + SVG Directional Plot */}
            <div
              className="sticky left-0 grid grid-cols-[minmax(0,38%)_minmax(0,1fr)] md:grid-cols-[minmax(0,272px)_minmax(0,1fr)]"
              style={{ width: viewportWidth || undefined }}
            >
              {/* Left HTML Accordion Lane Rail */}
              <div
                className="min-w-0 overflow-hidden border-r divide-y"
                style={{
                  borderColor: 'var(--border-rule)',
                  backgroundColor: 'var(--bg-panel)',
                }}
              >
                {visibleLanes.map((lane) => {
                  const isCollapsed = collapsedLaneKeys.has(lane.laneKey);
                  const aggCount = collapsedAggregateMarks.get(lane.laneKey)?.length ?? 0;
                  const indentPx = lane.depth * 14;

                  return (
                    <div
                      key={lane.laneKey}
                      className="flex items-center justify-between gap-1.5 px-2.5 transition-colors"
                      style={{
                        height: `${rowHeight}px`,
                        borderColor: 'var(--border-rule)',
                        paddingLeft: `${10 + indentPx}px`,
                        opacity: lane.isLinkedContext ? 0.72 : 1,
                        backgroundColor: lane.isLinkedContext
                          ? 'var(--bg-canvas)'
                          : 'transparent',
                      }}
                    >
                      <div className="flex items-center gap-1.5 min-w-0 flex-1">
                        {lane.collapsible ? (
                          <button
                            type="button"
                            onClick={() => onToggleLane(lane.laneKey)}
                            aria-expanded={!isCollapsed}
                            aria-label={`${isCollapsed ? 'Expand' : 'Collapse'} ${lane.label}`}
                            className="p-1 -ml-1 rounded-[3px] hover:opacity-80 cursor-pointer shrink-0"
                            style={{ color: 'var(--text-secondary)' }}
                          >
                            <ChevronRight
                              className="w-3.5 h-3.5 transition-transform duration-150"
                              style={{
                                transform: isCollapsed ? 'rotate(0deg)' : 'rotate(90deg)',
                              }}
                            />
                          </button>
                        ) : (
                          <span className="w-4 shrink-0" aria-hidden="true" />
                        )}
                        {laneIcon(lane.kind)}
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-1.5">
                            <span
                              className="text-[12.5px] font-medium truncate"
                              title={lane.label}
                            >
                              {lane.label}
                            </span>
                            {lane.relatedGroupKey && (
                              <button
                                type="button"
                                onClick={() => onFollowRelated(lane.relatedGroupKey!)}
                                aria-label={`Open related correlation ${lane.label}`}
                                className="inline-flex items-center gap-0.5 text-[11px] hover:underline shrink-0 cursor-pointer"
                                style={{ color: 'var(--accent)' }}
                              >
                                <ArrowUpRight className="w-3 h-3" />
                              </button>
                            )}
                          </div>
                          {rowHeight >= 32 && lane.sublabel && (
                            <div
                              className="font-mono-tabular text-[10.5px] truncate leading-tight"
                              style={{ color: 'var(--text-muted)' }}
                              title={lane.sublabel}
                            >
                              {lane.sublabel}
                            </div>
                          )}
                        </div>
                      </div>

                      <span
                        className="font-mono-tabular text-[10.5px] shrink-0"
                        style={{ color: 'var(--text-muted)' }}
                        title={
                          isCollapsed && aggCount > 0
                            ? `${lane.markCount} own + ${aggCount} collapsed marks`
                            : `${lane.markCount} marks`
                        }
                      >
                        {isCollapsed && aggCount > 0
                          ? `${lane.markCount + aggCount} (agg)`
                          : lane.markCount > 0
                          ? lane.markCount
                          : ''}
                      </span>
                    </div>
                  );
                })}
              </div>

              {/* Right Centered Directional Plot (SVG + optional dense Canvas layer) */}
              <div
                ref={plotContainerRef}
                className="relative select-none overflow-hidden"
                style={{
                  height: `${totalPlotHeight}px`,
                  backgroundColor: 'var(--bg-canvas)',
                }}
                tabIndex={0}
                role="region"
                aria-label="Directional waterfall plot"
                onKeyDown={handlePlotKeyDown}
                onMouseMove={(e) => {
                  const rect = e.currentTarget.getBoundingClientRect();
                  const relX = Math.max(0, Math.min(rect.width, e.clientX - rect.left));
                  const svgX = (relX / Math.max(1, rect.width)) * plotWidth;
                  const ms =
                    windowStartMs + ((svgX - 24) / (plotWidth - 48)) * timeSpan;
                  setCrosshairMs(ms);
                }}
                onMouseLeave={() => {
                  setCrosshairMs(null);
                  setHoveredEdgeId(null);
                  setHoveredMark(null);
                }}
              >
                {useDenseCanvas && (
                  <canvas
                    ref={canvasRef}
                    width={plotWidth}
                    height={totalPlotHeight}
                    className="absolute inset-0 w-full h-full pointer-events-none"
                  />
                )}

                <svg
                  viewBox={`0 0 ${plotWidth} ${totalPlotHeight}`}
                  className="w-full h-full block"
                  data-testid="waterfall-svg"
                >
                  <defs>
                    <marker
                      id="wf-arrow-default"
                      viewBox="0 0 10 10"
                      refX="7.5"
                      refY="5"
                      markerWidth="8"
                      markerHeight="8"
                      markerUnits="userSpaceOnUse"
                      orient="auto"
                    >
                      <path d="M 1.5 2 L 8.5 5 L 1.5 8 L 3.2 5 z" fill="var(--text-secondary)" />
                    </marker>
                    <marker
                      id="wf-arrow-accent"
                      viewBox="0 0 10 10"
                      refX="7.5"
                      refY="5"
                      markerWidth="8.5"
                      markerHeight="8.5"
                      markerUnits="userSpaceOnUse"
                      orient="auto"
                    >
                      <path d="M 1.5 2 L 8.5 5 L 1.5 8 L 3.2 5 z" fill="var(--accent)" />
                    </marker>
                    <marker
                      id="wf-arrow-warn"
                      viewBox="0 0 10 10"
                      refX="7.5"
                      refY="5"
                      markerWidth="8"
                      markerHeight="8"
                      markerUnits="userSpaceOnUse"
                      orient="auto"
                    >
                      <path d="M 1.5 2 L 8.5 5 L 1.5 8 L 3.2 5 z" fill="var(--status-warn)" />
                    </marker>
                    <marker
                      id="wf-arrow-err"
                      viewBox="0 0 10 10"
                      refX="7.5"
                      refY="5"
                      markerWidth="8"
                      markerHeight="8"
                      markerUnits="userSpaceOnUse"
                      orient="auto"
                    >
                      <path d="M 1.5 2 L 8.5 5 L 1.5 8 L 3.2 5 z" fill="var(--status-err)" />
                    </marker>
                  </defs>

                  {/* Horizontal lane dividers & alternating subtle tint */}
                  {visibleLanes.map((lane, idx) => (
                    <g key={`bg-${lane.laneKey}`}>
                      {lane.isLinkedContext && (
                        <rect
                          x={0}
                          y={idx * rowHeight}
                          width={plotWidth}
                          height={rowHeight}
                          fill="var(--grid-line)"
                        />
                      )}
                      <line
                        x1={0}
                        y1={(idx + 1) * rowHeight}
                        x2={plotWidth}
                        y2={(idx + 1) * rowHeight}
                        stroke="var(--border-rule)"
                        strokeWidth={1}
                      />
                    </g>
                  ))}

                  {/* Vertical time grid lines */}
                  {rulerTicks.map((tick, idx) => {
                    const x = timeToX(tick.ms);
                    return (
                      <line
                        key={`grid-${idx}`}
                        x1={x}
                        y1={0}
                        x2={x}
                        y2={totalPlotHeight}
                        stroke="var(--grid-line)"
                        strokeWidth={1}
                      />
                    );
                  })}

                  {/* Vertical hover/focus crosshair */}
                  {crosshairMs !== null && (
                    <line
                      x1={timeToX(crosshairMs)}
                      y1={0}
                      x2={timeToX(crosshairMs)}
                      y2={totalPlotHeight}
                      stroke="var(--accent)"
                      strokeWidth={1}
                      strokeDasharray="3 3"
                      opacity={0.32}
                      pointerEvents="none"
                    />
                  )}

                  {/* Collapsed lane aggregate range bars */}
                  {visibleLanes.map((lane, idx) => {
                    const agg = collapsedAggregateMarks.get(lane.laneKey);
                    if (!agg || agg.length === 0) return null;
                    if (!lane.collapseToTimeline && lane.marks.some((mark) => mark.glyph === 'interval')) return null;
                    const minMs = Math.min(...agg.map((m) => m.atMs));
                    const maxMs = Math.max(...agg.map((m) => m.endAtMs ?? m.atMs));
                    const x1 = timeToX(minMs);
                    const x2 = timeToX(maxMs);
                    const y = laneCenterY(idx);
                    return (
                      <g key={`agg-${lane.laneKey}`}>
                        <title>{`${agg.length} events · ${formatUtcTime(minMs)}–${formatUtcTime(maxMs)} UTC`}</title>
                        <rect
                          x={x1}
                          y={y - 5}
                          width={x2 - x1}
                          height={10}
                          rx={3}
                          fill="var(--accent-muted)"
                          stroke="var(--accent)"
                          strokeWidth={1}
                        />
                      </g>
                    );
                  })}

                  {/* Directional Edges (From -> To arrows), layered so dashed reference links sit beneath solid handoffs and active selection sits on top */}
                  {!roundTripCollapsed && [...model.edges]
                    .sort((a, b) => {
                      const rank = (e: WaterfallEdge) => {
                        const active =
                          (selectedItem?.type === 'edge' && selectedItem.id === e.id) ||
                          hoveredEdgeId === e.id ||
                          focusedEdgeId === e.id;
                        if (active) return 3;
                        const aDashed =
                          e.dashed ||
                          resolveVisibleLaneIndex(e.fromKey).collapsedAncestor ||
                          resolveVisibleLaneIndex(e.toKey).collapsedAncestor;
                        return aDashed ? 0 : e.kind === 'request_ingress' || e.kind === 'response_egress' ? 2 : 1;
                      };
                      return rank(a) - rank(b);
                    })
                    .map((edge) => {
                      const fromRes = resolveVisibleLaneIndex(edge.fromKey);
                      const toRes = resolveVisibleLaneIndex(edge.toKey);
                      const isSelected =
                        selectedItem?.type === 'edge' && selectedItem.id === edge.id;
                      const isHovered = hoveredEdgeId === edge.id;
                      const isFocused = focusedEdgeId === edge.id;
                      const isActive = isSelected || isHovered || isFocused;

                      const y1 = laneCenterY(fromRes.idx);
                      const y2 = laneCenterY(toRes.idx);
                      const x1 = timeToX(edge.startAtMs);
                      const x2 = timeToX(edge.endAtMs);

                      const isDashed =
                        edge.dashed || fromRes.collapsedAncestor || toRes.collapsedAncestor;

                      const chipText =
                        edge.endpointChip ??
                        (edge.clockOrderUncertain ? 'Clock order uncertain' : undefined);

                      const geom = computeEdgeGeometry({
                        x1,
                        y1,
                        x2,
                        y2,
                        kind: edge.kind,
                        hasEndpointChip: Boolean(chipText),
                        plotWidth,
                        fromIsRequester: edge.fromKey === 'lane:requester',
                        toIsRequester: edge.toKey === 'lane:requester',
                      });

                      const strokeColor = isActive
                        ? 'var(--accent)'
                        : edge.clockOrderUncertain || edge.outcome === 'reply_not_observed'
                        ? 'var(--status-warn)'
                        : edge.outcome === 'error'
                        ? 'var(--status-err)'
                        : 'var(--text-secondary)';

                      const markerUrl = isActive
                        ? 'url(#wf-arrow-accent)'
                        : edge.clockOrderUncertain || edge.outcome === 'reply_not_observed'
                        ? 'url(#wf-arrow-warn)'
                        : edge.outcome === 'error'
                        ? 'url(#wf-arrow-err)'
                        : 'url(#wf-arrow-default)';

                      return (
                        <g
                          key={edge.id}
                          role="button"
                          tabIndex={0}
                          aria-label={`Edge: ${edge.textSummary}`}
                          onClick={() => onSelectEdge(edge)}
                          onFocus={() => setFocusedEdgeId(edge.id)}
                          onBlur={() => setFocusedEdgeId((prev) => (prev === edge.id ? null : prev))}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter' || e.key === ' ') {
                              e.preventDefault();
                              onSelectEdge(edge);
                            }
                          }}
                          onMouseEnter={() => setHoveredEdgeId(edge.id)}
                          onMouseLeave={() => setHoveredEdgeId(null)}
                          className="cursor-pointer"
                        >
                          {/* Wide transparent hit target */}
                          <path
                            d={geom.dPath}
                            fill="none"
                            stroke="transparent"
                            strokeWidth={14}
                          />
                          {/* Subtle canvas overpass halo behind solid arrows so crossings over dashed links read cleanly */}
                          {!isDashed && (
                            <path
                              d={geom.dPath}
                              fill="none"
                              stroke="var(--bg-canvas)"
                              strokeWidth={4.2}
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              opacity={0.85}
                            />
                          )}
                          {/* Path-hugging selection / keyboard-focus halo (replaces rectangular bounding box) */}
                          {isActive && (
                            <path
                              d={geom.dPath}
                              fill="none"
                              stroke="var(--accent)"
                              strokeWidth={6}
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              opacity={0.22}
                            />
                          )}
                          {/* Primary directional edge stroke */}
                          <path
                            d={geom.dPath}
                            fill="none"
                            stroke={strokeColor}
                            strokeWidth={isActive ? 1.9 : isDashed ? 1.25 : 1.4}
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeDasharray={isDashed ? '4 3.5' : undefined}
                            markerEnd={markerUrl}
                            opacity={isActive ? 1 : isDashed ? 0.68 : 0.86}
                          />
                          {/* Subtle contact anchor on Requester / peer lane so wire rays start/land intentionally */}
                          {geom.peerAnchor && (
                            <circle
                              cx={geom.peerAnchor.x}
                              cy={geom.peerAnchor.y}
                              r={isActive ? 3.2 : 2.4}
                              fill="var(--bg-canvas)"
                              stroke={strokeColor}
                              strokeWidth={1.4}
                              opacity={isActive ? 1 : 0.82}
                            />
                          )}
                          {chipText && (
                            <g
                              transform={`translate(${geom.chipX}, ${geom.chipY})`}
                              onClick={(ev) => {
                                ev.stopPropagation();
                                if (edge.relatedGroupKey) {
                                  onFollowRelated(edge.relatedGroupKey);
                                } else {
                                  onSelectEdge(edge);
                                }
                              }}
                            >
                              <rect
                                x={0}
                                y={0}
                                width={Math.min(132, chipText.length * 6.3 + 14)}
                                height={18}
                                rx={3}
                                fill="var(--bg-panel-elevated)"
                                stroke={
                                  edge.relatedGroupKey
                                    ? 'var(--accent)'
                                    : 'var(--status-warn)'
                                }
                                strokeWidth={1}
                              />
                              <text
                                x={7}
                                y={12.5}
                                fontSize="10"
                                fontFamily="var(--font-mono)"
                                fill={
                                  edge.relatedGroupKey
                                    ? 'var(--accent)'
                                    : 'var(--text-primary)'
                                }
                              >
                                {chipText.length > 19 ? `${chipText.slice(0, 18)}…` : chipText}
                              </text>
                            </g>
                          )}
                        </g>
                      );
                    })}

                  {/* Event Marks (Points, Measured Interval Bars, Datagrams, Transactions) */}
                  {visibleMarks.map((mark) => {
                      if (bucketedMarks.has(mark)) return null;
                      const idx = laneIndexMap.get(mark.laneKey);
                      if (idx === undefined) return null;
                      const x = timeToX(mark.atMs) + mark.stackOffset;
                      const laneY = laneCenterY(idx);
                      const y = laneY + (mark.timelineNodeOffset ?? 0);
                      const isSelected =
                        selectedItem?.type === 'mark' && selectedItem.id === mark.id;
                      const isHovered = hoveredMark?.mark.id === mark.id;
                      const isFocused = focusedMarkId === mark.id;
                      const color =
                        isSelected || isHovered || isFocused
                          ? 'var(--accent)'
                          : outcomeDisplay(mark.outcome).color;

                      const hasInterval =
                        mark.glyph === 'interval' &&
                        mark.endAtMs !== undefined &&
                        !mark.clockOrderUncertain;
                      const barWidth = hasInterval
                        ? Math.max(0, timeToX(mark.endAtMs!) - timeToX(mark.atMs))
                        : 0;
                      const summaryDuration = mark.evidenceSequences && mark.measuredDurationMs !== undefined
                        ? `${mark.measuredDurationMs.toPrecision(3)} ms`
                        : undefined;
                      const rasterized = useDenseCanvas && !hasInterval &&
                        !mark.evidenceSequences && mark.timelineNodeOffset === undefined;

                      return (
                        <React.Fragment key={mark.id}>
                        <g
                          role="button"
                          tabIndex={0}
                          aria-label={`${mark.label}, ${summaryDuration ? `${summaryDuration}, ` : ''}${formatUtcTime(mark.atMs)} UTC, ${mark.directionLabel}, ${mark.provenance}`}
                          {...markPreviewHandlers(mark)}
                          onClick={() => onSelectMark(mark)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter' || e.key === ' ') {
                              e.preventDefault();
                              onSelectMark(mark);
                            }
                          }}
                          className="cursor-pointer"
                          opacity={mark.isLinkedContext && !isSelected ? 0.58 : 1}
                        >
                          <rect
                            x={x - 4}
                            y={y - 7}
                            width={rasterized ? 8 : hasInterval ? barWidth + 8 : mark.glyph === 'open_ended' ? 26 : 8}
                            height={14}
                            fill="transparent"
                            aria-hidden="true"
                          />
                          {/* Selection / keyboard focus halo */}
                          {(isSelected || isFocused || (useDenseCanvas && isHovered)) && (
                            <circle
                              cx={x}
                              cy={y}
                              r={9}
                              fill="var(--accent-muted)"
                              stroke="var(--accent)"
                              strokeWidth={1.2}
                            />
                          )}

                          {!rasterized && <>
                          {mark.timelineNodeOffset !== undefined && (
                            <line x1={x} x2={x} y1={laneY} y2={y} stroke={color} strokeWidth={1.2} />
                          )}
                          {/* Measured or recorded interval */}
                          {hasInterval && (
                            <g>
                              <rect
                                x={x}
                                y={y - 4}
                                width={barWidth}
                                height={8}
                                rx={2}
                                fill={color}
                                opacity={0.3}
                                stroke={color}
                                strokeWidth={1.2}
                                strokeDasharray={mark.timeBasis === 'measured_monotonic' ? undefined : '3 2'}
                              />
                              {!mark.transactionBoundaries && !collapsedLaneKeys.has(mark.laneKey) && (
                                <>
                                  <circle cx={x} cy={y} r={3.5} fill={color} />
                                  <circle cx={x + barWidth} cy={y} r={3} fill={color} />
                                </>
                              )}
                              {summaryDuration && (
                                <text
                                  x={x + barWidth > plotWidth - 64 ? x - 7 : x + barWidth + 7}
                                  y={y}
                                  textAnchor={x + barWidth > plotWidth - 64 ? 'end' : 'start'}
                                  dominantBaseline="central"
                                  className="font-mono-tabular"
                                  fontSize={10}
                                  fill="var(--text-primary)"
                                  aria-hidden="true"
                                >
                                  {summaryDuration}
                                </text>
                              )}
                            </g>
                          )}

                          {/* Datagram diamond mark */}
                          {!hasInterval && mark.glyph === 'datagram' && (
                            <polygon
                              points={`${x},${y - 5.5} ${x + 5.5},${y} ${x},${y + 5.5} ${x - 5.5},${y}`}
                              fill="var(--bg-canvas)"
                              stroke={color}
                              strokeWidth={1.8}
                            />
                          )}

                          {/* Database transaction square mark */}
                          {!hasInterval && mark.glyph === 'tx' && (
                            <rect
                              x={x - 4.5}
                              y={y - 4.5}
                              width={9}
                              height={9}
                              rx={1.5}
                              fill={color}
                              stroke="var(--bg-canvas)"
                              strokeWidth={1}
                            />
                          )}

                          {/* Open-ended incomplete mark */}
                          {!hasInterval && mark.glyph === 'open_ended' && (
                            <g>
                              <circle
                                cx={x}
                                cy={y}
                                r={4.5}
                                fill="var(--bg-canvas)"
                                stroke="var(--status-warn)"
                                strokeWidth={1.8}
                                strokeDasharray="2 1.5"
                              />
                              <line
                                x1={x + 5}
                                y1={y}
                                x2={x + 22}
                                y2={y}
                                stroke="var(--status-warn)"
                                strokeWidth={1.2}
                                strokeDasharray="3 2"
                              />
                            </g>
                          )}

                          {/* Standard point or unknown event mark */}
                          {!hasInterval &&
                            mark.glyph !== 'datagram' &&
                            mark.glyph !== 'tx' &&
                            mark.glyph !== 'open_ended' && (
                              <circle
                                cx={x}
                                cy={y}
                                r={isSelected || isHovered ? 5 : 4}
                                fill={mark.glyph === 'unknown' ? 'var(--bg-canvas)' : color}
                                stroke={color}
                                strokeWidth={1.8}
                              />
                            )}
                          </>}
                        </g>
                        {mark.transactionBoundaries?.map((node) => {
                          const nodeX = timeToX(node.atMs);
                          const active = selectedItem?.type === 'mark' && selectedItem.id === node.id ||
                            focusedMarkId === node.id || hoveredMark?.mark.id === node.id;
                          const ink = active ? 'var(--accent)' : outcomeDisplay(node.outcome).color;
                          return (
                            <g
                              key={node.id}
                              role="button"
                              tabIndex={0}
                              aria-label={`${node.kind}, ${formatUtcTime(node.atMs)} UTC`}
                              {...markPreviewHandlers(node)}
                              className="cursor-pointer"
                              onClick={() => onSelectMark(node)}
                              onKeyDown={(event) => {
                                if (event.key === 'Enter' || event.key === ' ') {
                                  event.preventDefault();
                                  onSelectMark(node);
                                }
                              }}
                            >
                              <circle cx={nodeX} cy={y} r={8} fill="transparent" />
                              <circle
                                cx={nodeX}
                                cy={y}
                                r={active ? 6 : 4.5}
                                fill={node.kind === 'db.tx.begin' ? 'var(--bg-canvas)' : ink}
                                stroke={ink}
                                strokeWidth={2}
                              />
                            </g>
                          );
                        })}
                        </React.Fragment>
                      );
                    })}
                  {nodeBuckets.map((bucket) => {
                    const { laneKey, nodes, x, width } = bucket;
                    const y = laneCenterY(laneIndexMap.get(laneKey)!);
                    const count = nodes.length;
                    const key = bucketKey(bucket);
                    const ink = nodes.some((node) => node.outcome === 'error') ? outcomeDisplay('error').color
                      : nodes.some((node) => node.outcome === 'incomplete') ? outcomeDisplay('incomplete').color
                      : 'var(--accent)';
                    const expand = () => {
                      setBucketPreview(null);
                      onToggleLane(laneKey);
                    };
                    return (
                      <g
                        key={key}
                        role="button"
                        tabIndex={0}
                        aria-label={`${count} events. Expand ${laneByKey.get(laneKey)?.label} to inspect.`}
                        aria-describedby={previewBucket === bucket ? tooltipId : undefined}
                        className="cursor-pointer outline-none focus-visible:[&>rect]:stroke-[2.5]"
                        onMouseMove={(event) => setBucketPreview({
                          key, element: event.currentTarget, cursor: { x: event.clientX, y: event.clientY },
                        })}
                        onMouseLeave={(event) => {
                          if (document.activeElement === event.currentTarget) {
                            setBucketPreview({ key, element: event.currentTarget });
                          } else setBucketPreview(null);
                        }}
                        onFocus={(event) => setBucketPreview({ key, element: event.currentTarget })}
                        onBlur={() => setBucketPreview(null)}
                        onClick={expand}
                        onKeyDown={(event) => {
                          if (event.key === 'Enter' || event.key === ' ') {
                            event.preventDefault();
                            expand();
                          }
                        }}
                      >
                        <rect x={x - width / 2} y={y - 8} width={width} height={16} rx={3}
                          fill="var(--bg-panel-elevated)" stroke={ink} strokeWidth={1.25} />
                        <text x={x} y={y} textAnchor="middle" dominantBaseline="central"
                          className="pointer-events-none font-mono-tabular" fontSize={10}
                          fill="var(--text-primary)" aria-hidden="true">{count}</text>
                      </g>
                    );
                  })}
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>
      {previewBucket && bucketPreview ? (
        <EventTooltip
          id={tooltipId}
          anchor={bucketPreview.cursor ?? { element: bucketPreview.element }}
          container={bucketPreview.element.closest('.correlations-surface') ?? undefined}
          className="rounded-[5px] border px-3 py-2 text-[12px] shadow-lg"
          style={{ backgroundColor: 'var(--bg-panel-elevated)', borderColor: 'var(--border-strong)', color: 'var(--text-primary)' }}
        >
          <div className="font-semibold">{previewBucket.nodes.length} events in time segment</div>
          <div className="font-mono-tabular" style={{ color: 'var(--text-secondary)' }}>
            {formatUtcTime(previewBucket.nodes[0].atMs)}–{formatUtcTime(previewBucket.nodes.at(-1)!.atMs)} UTC
          </div>
          <div style={{ color: 'var(--accent-text)' }}>Expand row to inspect events</div>
        </EventTooltip>
      ) : preview && navigableMarks.some((mark) => mark.id === preview.mark.id) && (
        <EventTooltip
          id={tooltipId}
          anchor={hover && cursor ? cursor : { element: preview.element }}
          container={preview.element.closest('.correlations-surface') ?? undefined}
          className="rounded-[5px] border px-3 py-2 text-[12px] shadow-lg"
          style={{
            backgroundColor: 'var(--bg-panel-elevated)',
            borderColor: 'var(--border-strong)',
            color: 'var(--text-primary)',
          }}
        >
          <div className="font-semibold break-words">{preview.mark.label}</div>
          <div className="font-mono-tabular" style={{ color: 'var(--text-secondary)' }}>
            {preview.mark.timelineNodeOffset !== undefined
              ? preview.mark.kind.startsWith('db.flush.') || preview.mark.kind === 'hook.completed' ? 'Ended ' : 'Observed '
              : preview.mark.atMs !== preview.mark.event.atMs && !/^db\.tx\.(commit|rollback)$/.test(preview.mark.label) && 'Started '}
            {formatUtcTime(preview.mark.atMs)} UTC · {preview.mark.evidenceSequences
              ? `${preview.mark.evidenceSequences.length} evidence rows`
              : `Event #${preview.mark.seq}`}
          </div>
          <div className="mt-1 flex flex-wrap items-center gap-x-2" style={{ color: 'var(--text-muted)' }}>
            <OutcomeLabel outcome={preview.mark.outcome} />
            <span>{preview.mark.directionLabel}</span>
            {preview.mark.timeBasis === 'measured_monotonic' && preview.mark.measuredDurationMs !== undefined && (
              <span>
                {preview.mark.measuredDurationMs.toPrecision(3)} ms
                {preview.mark.kind === 'db.tx.commit' || preview.mark.kind === 'db.tx.rollback'
                  ? ' transaction total'
                  : ' measured'}
              </span>
            )}
          </div>
        </EventTooltip>
      )}
    </div>
  );
}
