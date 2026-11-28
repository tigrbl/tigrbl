import React, { useCallback, useEffect, useId, useMemo, useRef, useState } from 'react';
import {
  ChevronLeft,
  ChevronRight,
  ChevronsDownUp,
  ChevronsUpDown,
  Maximize2,
  Play,
  Table2,
  ZoomIn,
  ZoomOut,
} from 'lucide-react';
import {
  formatOffsetMs,
  formatUtcTime,
} from '../adapter/traceAdapter';
import { DENSITY_ROW_HEIGHT, ThemePalette } from '../theme/tokens';
import {
  DensityId,
  KaryogramRow,
  NormalizedEvent,
  RelationshipArc,
  SelectionState,
} from '../types/trace';
import { RoleMark } from './RoleMark';
import { EventTooltip } from './EventTooltip';

interface EventKaryogramProps {
  rows: KaryogramRow[];
  arcs: RelationshipArc[];
  domainMinMs: number;
  domainMaxMs: number;
  fullMinMs: number;
  fullMaxMs: number;
  density: DensityId;
  themePalette: ThemePalette;
  selection: SelectionState | null;
  onSelect: (sel: SelectionState) => void;
  onToggleExpand: (entityId: string) => void;
  onExpandAll: () => void;
  onCollapseAll: () => void;
  onSetTimeWindow: (fromMs: number | null, toMs: number | null) => void;
  onSelectBucket: (bucket: { rowId: string; startMs: number; endMs: number; count: number }) => void;
  onOpenTable: () => void;
  isLoading: boolean;
  isEmptyCapture: boolean;
  onRunAll?: () => void;
  onOpenRecordedSample: () => void;
  onClearFilters: () => void;
}

interface HitTarget {
  x: number;
  y: number;
  w: number;
  h: number;
  rowId: string;
  events: NormalizedEvent[];
  isBucket: boolean;
  startMs: number;
  endMs: number;
}

export const EventKaryogram: React.FC<EventKaryogramProps> = ({
  rows,
  arcs,
  domainMinMs,
  domainMaxMs,
  fullMinMs,
  fullMaxMs,
  density,
  themePalette,
  selection,
  onSelect,
  onToggleExpand,
  onExpandAll,
  onCollapseAll,
  onSetTimeWindow,
  onSelectBucket,
  onOpenTable,
  isLoading,
  isEmptyCapture,
  onRunAll,
  onOpenRecordedSample,
  onClearFilters,
}) => {
  const rowHeight = DENSITY_ROW_HEIGHT[density];
  const plotContainerRef = useRef<HTMLDivElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const hitTargetsRef = useRef<HitTarget[]>([]);
  const keyboardTarget = useRef(-1);
  const tooltipId = useId();
  const [plotWidth, setPlotWidth] = useState(640);

  // Brush interaction state
  const [brushStartX, setBrushStartX] = useState<number | null>(null);
  const [brushCurrentX, setBrushCurrentX] = useState<number | null>(null);

  // Hover tooltip state (transient, never stored in URL)
  const [hoverInfo, setHoverInfo] = useState<{
    cursor?: { x: number; y: number };
    target: HitTarget;
  } | null>(null);

  // Measure plot surface width via ResizeObserver
  useEffect(() => {
    const el = plotContainerRef.current;
    if (!el) return;
    const update = () => {
      const next = Math.max(260, Math.floor(el.clientWidth));
      setPlotWidth(next);
    };
    update();
    const ro = new ResizeObserver(update);
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  // Dismiss tooltip on Escape
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setHoverInfo(null);
        setBrushStartX(null);
        setBrushCurrentX(null);
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  const padX = 14;
  const usableW = Math.max(100, plotWidth - padX * 2);
  const spanMs = Math.max(1, domainMaxMs - domainMinMs);
  const isZoomed =
    Math.abs(domainMinMs - fullMinMs) > 2 || Math.abs(domainMaxMs - fullMaxMs) > 2;

  const timeToX = useCallback(
    (ms: number) => padX + ((ms - domainMinMs) / spanMs) * usableW,
    [domainMinMs, spanMs, usableW]
  );

  const xToTime = useCallback(
    (x: number) => domainMinMs + ((Math.max(padX, Math.min(plotWidth - padX, x)) - padX) / usableW) * spanMs,
    [domainMinMs, plotWidth, spanMs, usableW]
  );

  // Major & minor UTC ticks
  const majorTickCount = plotWidth >= 680 ? 6 : 4;
  const ticks = useMemo(() => {
    const major: Array<{ x: number; ms: number; label: string; offset: string }> = [];
    const minor: number[] = [];
    for (let i = 0; i <= majorTickCount; i++) {
      const ratio = i / majorTickCount;
      const ms = domainMinMs + ratio * spanMs;
      const x = padX + ratio * usableW;
      major.push({
        x,
        ms,
        label: formatUtcTime(ms, spanMs < 60000),
        offset: formatOffsetMs(ms - domainMinMs),
      });
      if (i < majorTickCount) {
        minor.push(padX + ((i + 0.5) / majorTickCount) * usableW);
      }
    }
    return { major, minor };
  }, [domainMinMs, spanMs, usableW, majorTickCount]);

  const totalHeight = Math.max(rowHeight, rows.length * rowHeight);

  // Draw DPR-aware canvas raster using shared timeToX & rowHeight transform
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || rows.length === 0) {
      hitTargetsRef.current = [];
      return;
    }

    const dpr = Math.min(2, window.devicePixelRatio || 1);
    canvas.width = Math.floor(plotWidth * dpr);
    canvas.height = Math.floor(totalHeight * dpr);
    canvas.style.width = `${plotWidth}px`;
    canvas.style.height = `${totalHeight}px`;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.save();
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, plotWidth, totalHeight);

    const targets: HitTarget[] = [];

    // 1. Row backgrounds & horizontal rules
    for (let i = 0; i < rows.length; i++) {
      const row = rows[i];
      const y = i * rowHeight;
      const isRowSelected = selection?.type === 'entity' && selection.id === row.entityId;

      if (isRowSelected) {
        ctx.fillStyle = themePalette.selectedBg;
        ctx.fillRect(0, y, plotWidth, rowHeight);
      } else if (row.isGroupBoundary) {
        ctx.fillStyle = themePalette.surfaceAlt;
        ctx.globalAlpha = 0.45;
        ctx.fillRect(0, y, plotWidth, rowHeight);
        ctx.globalAlpha = 1;
      }

      // Row divider
      ctx.strokeStyle = themePalette.border;
      ctx.globalAlpha = row.isGroupBoundary ? 0.55 : 0.28;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(0, y + rowHeight - 0.5);
      ctx.lineTo(plotWidth, y + rowHeight - 0.5);
      ctx.stroke();
      ctx.globalAlpha = 1;
    }

    // 2. Vertical minor (7%) and major (14%) gridlines
    ctx.lineWidth = 1;
    ctx.strokeStyle = themePalette.gridMinor;
    for (const mx of ticks.minor) {
      ctx.beginPath();
      ctx.moveTo(Math.round(mx) + 0.5, 0);
      ctx.lineTo(Math.round(mx) + 0.5, totalHeight);
      ctx.stroke();
    }
    ctx.strokeStyle = themePalette.gridMajor;
    for (const t of ticks.major) {
      ctx.beginPath();
      ctx.moveTo(Math.round(t.x) + 0.5, 0);
      ctx.lineTo(Math.round(t.x) + 0.5, totalHeight);
      ctx.stroke();
    }

    // 3. Draw intervals and marks/buckets per row
    const bucketPx = 14;
    for (let i = 0; i < rows.length; i++) {
      const row = rows[i];
      const y = i * rowHeight;
      const cy = y + rowHeight / 2;

      // Interval band behind event glyphs
      if (row.startMs !== null && row.endMs !== null && row.endMs > row.startMs) {
        const x1 = Math.max(padX, timeToX(row.startMs));
        const x2 = Math.min(plotWidth - padX, timeToX(row.endMs));
        if (x2 >= padX && x1 <= plotWidth - padX) {
          const roleColor = themePalette.roles[row.role];
          const bandH = row.entityKind === 'invocation' || row.entityKind === 'transaction' ? 10 : 6;

          ctx.save();
          ctx.fillStyle = roleColor;
          ctx.globalAlpha = themePalette.isDark ? 0.2 : 0.16;
          ctx.fillRect(x1, cy - bandH / 2, Math.max(2, x2 - x1), bandH);
          ctx.globalAlpha = 0.85;
          ctx.strokeStyle = roleColor;
          ctx.lineWidth = 1.5;

          if (row.isOpen) {
            ctx.setLineDash([3, 3]);
          }
          ctx.beginPath();
          ctx.moveTo(x1, cy);
          ctx.lineTo(x2, cy);
          ctx.stroke();
          ctx.setLineDash([]);

          // Start tick
          ctx.beginPath();
          ctx.moveTo(x1, cy - 5);
          ctx.lineTo(x1, cy + 5);
          ctx.stroke();

          // End tick or dotted open cap
          if (row.isOpen) {
            ctx.beginPath();
            ctx.arc(x2, cy, 3.5, 0, Math.PI * 2);
            ctx.setLineDash([2, 2]);
            ctx.strokeStyle = themePalette.roles.partial;
            ctx.stroke();
          } else {
            ctx.beginPath();
            ctx.moveTo(x2, cy - 5);
            ctx.lineTo(x2, cy + 5);
            ctx.stroke();
          }
          ctx.restore();
        }
      }

      // Group row events into aligned pixel bins when dense
      const visibleEvs = row.events.filter((e) => e.atMs >= domainMinMs && e.atMs <= domainMaxMs);
      const bins = new Map<number, NormalizedEvent[]>();
      for (const ev of visibleEvs) {
        const px = timeToX(ev.atMs);
        const bKey = Math.floor((px - padX) / bucketPx);
        const list = bins.get(bKey) ?? [];
        list.push(ev);
        bins.set(bKey, list);
      }

      for (const [bKey, evList] of bins.entries()) {
        if (evList.length > 2) {
          // Render aligned dense time bucket with count
          const bx = padX + bKey * bucketPx + bucketPx / 2;
          const hasError = evList.some((e) => e.role === 'rejected');
          const hasPartial = evList.some((e) => e.role === 'partial');
          const color = hasError
            ? themePalette.roles.rejected
            : hasPartial
              ? themePalette.roles.partial
              : themePalette.roles[row.role];
          const w = Math.max(18, String(evList.length).length * 7 + 8);
          const h = Math.min(rowHeight - 8, 18);

          ctx.save();
          ctx.fillStyle = themePalette.panel;
          ctx.strokeStyle = color;
          ctx.lineWidth = 1.25;
          ctx.beginPath();
          ctx.roundRect(bx - w / 2, cy - h / 2, w, h, 3);
          ctx.fill();
          ctx.stroke();

          ctx.fillStyle = themePalette.textPrimary;
          ctx.font = '500 10px "IBM Plex Mono", monospace';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(String(evList.length), bx, cy + 0.5);
          ctx.restore();

          targets.push({
            x: bx - w / 2 - 2,
            y: cy - h / 2 - 2,
            w: w + 4,
            h: h + 4,
            rowId: row.rowId,
            events: evList,
            isBucket: true,
            startMs: evList[0].atMs,
            endMs: evList[evList.length - 1].atMs,
          });
        } else {
          // Render discrete role marks
          for (let j = 0; j < evList.length; j++) {
            const ev = evList[j];
            const px = timeToX(ev.atMs) + (evList.length === 2 ? (j === 0 ? -3 : 3) : 0);
            const color = themePalette.roles[ev.role];
            const isSelected = selection?.type === 'event' && selection.id === ev.id;

            ctx.save();
            if (isSelected) {
              ctx.strokeStyle = themePalette.accent;
              ctx.lineWidth = 2;
              ctx.beginPath();
              ctx.arc(px, cy, 8, 0, Math.PI * 2);
              ctx.stroke();
            }

            if (ev.role === 'success') {
              ctx.fillStyle = color;
              ctx.beginPath();
              ctx.arc(px, cy, 4.2, 0, Math.PI * 2);
              ctx.fill();
            } else if (ev.role === 'rejected') {
              ctx.strokeStyle = color;
              ctx.lineWidth = 2;
              ctx.lineCap = 'round';
              ctx.beginPath();
              ctx.moveTo(px - 4, cy - 4);
              ctx.lineTo(px + 4, cy + 4);
              ctx.moveTo(px + 4, cy - 4);
              ctx.lineTo(px - 4, cy + 4);
              ctx.stroke();
            } else if (ev.role === 'partial') {
              ctx.strokeStyle = color;
              ctx.lineWidth = 1.6;
              ctx.setLineDash([2, 2]);
              ctx.beginPath();
              ctx.arc(px, cy, 4.2, 0, Math.PI * 2);
              ctx.stroke();
            } else if (ev.kind.startsWith('wt.datagram')) {
              // Diamond for datagram
              ctx.fillStyle = themePalette.panel;
              ctx.strokeStyle = color;
              ctx.lineWidth = 1.6;
              ctx.beginPath();
              ctx.moveTo(px, cy - 5);
              ctx.lineTo(px + 5, cy);
              ctx.lineTo(px, cy + 5);
              ctx.lineTo(px - 5, cy);
              ctx.closePath();
              ctx.fill();
              ctx.stroke();
            } else if (ev.role === 'invocation') {
              // Tick / outlined vertical mark
              ctx.strokeStyle = color;
              ctx.lineWidth = 2;
              ctx.beginPath();
              ctx.moveTo(px, cy - 5.5);
              ctx.lineTo(px, cy + 5.5);
              ctx.stroke();
            } else if (ev.role === 'carrier') {
              ctx.strokeStyle = color;
              ctx.lineWidth = 1.8;
              ctx.beginPath();
              ctx.moveTo(px, cy - 4.5);
              ctx.lineTo(px, cy + 4.5);
              ctx.stroke();
            } else {
              // Hollow square for neutral event
              ctx.fillStyle = themePalette.panel;
              ctx.strokeStyle = color;
              ctx.lineWidth = 1.5;
              ctx.fillRect(px - 3.5, cy - 3.5, 7, 7);
              ctx.strokeRect(px - 3.5, cy - 3.5, 7, 7);
            }
            ctx.restore();

            targets.push({
              x: px - 7,
              y: cy - 7,
              w: 14,
              h: 14,
              rowId: row.rowId,
              events: [ev],
              isBucket: false,
              startMs: ev.atMs,
              endMs: ev.atMs,
            });
          }
        }
      }
    }

    ctx.restore();
    hitTargetsRef.current = targets;
    const firstTarget = targets[0];
    if (document.activeElement === canvas && keyboardTarget.current === -1 && firstTarget) {
      keyboardTarget.current = 0;
      setHoverInfo({ target: firstTarget });
    }
  }, [rows, plotWidth, totalHeight, rowHeight, themePalette, ticks, timeToX, domainMinMs, domainMaxMs, selection]);

  const findHitTarget = (clientX: number, clientY: number): { target: HitTarget | null; relX: number } => {
    const canvas = canvasRef.current;
    if (!canvas) return { target: null, relX: 0 };
    const rect = canvas.getBoundingClientRect();
    const relX = clientX - rect.left;
    const relY = clientY - rect.top;
    // Search in reverse so foreground glyphs win
    for (let i = hitTargetsRef.current.length - 1; i >= 0; i--) {
      const t = hitTargetsRef.current[i];
      if (relX >= t.x && relX <= t.x + t.w && relY >= t.y && relY <= t.y + t.h) {
        return { target: t, relX };
      }
    }
    return { target: null, relX };
  };

  const handleCanvasMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    setBrushStartX(x);
    setBrushCurrentX(x);
  };

  const handleCanvasMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const { target, relX } = findHitTarget(e.clientX, e.clientY);
    if (brushStartX !== null) {
      setBrushCurrentX(relX);
      setHoverInfo(null);
      return;
    }
    if (target) {
      setHoverInfo({ cursor: { x: e.clientX, y: e.clientY }, target });
    } else {
      setHoverInfo(null);
    }
  };

  const handleCanvasMouseUp = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const { target, relX } = findHitTarget(e.clientX, e.clientY);
    if (brushStartX !== null && Math.abs(relX - brushStartX) >= 10) {
      const a = xToTime(Math.min(brushStartX, relX));
      const b = xToTime(Math.max(brushStartX, relX));
      onSetTimeWindow(a, b);
    } else if (target) {
      selectHitTarget(target);
    } else {
      // Clicking an empty spot in a lane selects the row entity
      const canvas = canvasRef.current;
      if (canvas) {
        const rect = canvas.getBoundingClientRect();
        const rowIndex = Math.floor((e.clientY - rect.top) / rowHeight);
        const row = rows[rowIndex];
        if (row) onSelect({ type: 'entity', id: row.entityId });
      }
    }
    setBrushStartX(null);
    setBrushCurrentX(null);
  };

  const selectHitTarget = (target: HitTarget) => {
    if (target.isBucket) {
      onSelectBucket({
        rowId: target.rowId,
        startMs: target.startMs,
        endMs: target.endMs,
        count: target.events.length,
      });
    } else {
      onSelect({ type: 'event', id: target.events[0].id });
    }
  };

  const focusHitTarget = (index: number) => {
    const targets = hitTargetsRef.current;
    if (!targets.length) return;
    keyboardTarget.current = (index + targets.length) % targets.length;
    const target = targets[keyboardTarget.current];
    setHoverInfo({ target });
  };

  const handleCanvasKeyDown = (event: React.KeyboardEvent<HTMLCanvasElement>) => {
    if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') {
      event.preventDefault();
      focusHitTarget(keyboardTarget.current + (event.key === 'ArrowRight' ? 1 : -1));
    } else if (event.key === 'Enter' || event.key === ' ') {
      const target = hitTargetsRef.current[keyboardTarget.current];
      if (target) {
        event.preventDefault();
        selectHitTarget(target);
      }
    }
  };

  // Keyboard & button zoom/pan equivalents for brush
  const zoomBy = (factor: number) => {
    const center = (domainMinMs + domainMaxMs) / 2;
    const half = Math.max(10, ((domainMaxMs - domainMinMs) * factor) / 2);
    const nextFrom = Math.max(fullMinMs, center - half);
    const nextTo = Math.min(fullMaxMs, center + half);
    if (nextFrom <= fullMinMs + 1 && nextTo >= fullMaxMs - 1) {
      onSetTimeWindow(null, null);
    } else {
      onSetTimeWindow(nextFrom, nextTo);
    }
  };

  const panBy = (direction: -1 | 1) => {
    const shift = (domainMaxMs - domainMinMs) * 0.25 * direction;
    let nextFrom = domainMinMs + shift;
    let nextTo = domainMaxMs + shift;
    if (nextFrom < fullMinMs) {
      nextTo += fullMinMs - nextFrom;
      nextFrom = fullMinMs;
    }
    if (nextTo > fullMaxMs) {
      nextFrom -= nextTo - fullMaxMs;
      nextTo = fullMaxMs;
    }
    onSetTimeWindow(Math.max(fullMinMs, nextFrom), Math.min(fullMaxMs, nextTo));
  };

  // Build row index map for SVG relationship arcs
  const rowIndexById = useMemo(() => {
    const map = new Map<string, number>();
    rows.forEach((r, idx) => map.set(r.rowId, idx));
    return map;
  }, [rows]);

  // Loading skeleton state
  if (isLoading) {
    return (
      <div
        className="rounded-[5px] border p-4 space-y-2.5"
        style={{ backgroundColor: 'var(--panel)', borderColor: 'var(--border)' }}
        aria-busy="true"
        aria-label="Loading trace snapshot"
      >
        {[0, 1, 2, 3, 4, 5].map((i) => (
          <div
            key={i}
            className="h-8 rounded-[4px]"
            style={{ backgroundColor: 'var(--surface-alt)', opacity: 0.65 - i * 0.06 }}
          />
        ))}
      </div>
    );
  }

  // Empty live capture state (explicitly distinct from zero filter matches)
  if (isEmptyCapture) {
    return (
      <section
        aria-label="Empty trace capture"
        className="rounded-[5px] border px-6 py-12 flex flex-col items-center text-center gap-4"
        style={{ backgroundColor: 'var(--panel)', borderColor: 'var(--border)' }}
      >
        <div className="max-w-lg space-y-2">
          <h2
            className="text-[16px] leading-[22px] font-semibold"
            style={{ color: 'var(--text-primary)' }}
          >
            No trace records captured yet
          </h2>
          <p className="text-[13px] leading-[19px]" style={{ color: 'var(--text-muted)' }}>
            {onRunAll
              ? 'Run the four-transport server scenario to capture REST, HTTP JSON-RPC, WebSocket, WebTransport, and linked database events.'
              : 'Send a request to a monitored Tigrbl app or look up a different correlation ID.'}
          </p>
        </div>
        <div className="flex flex-wrap items-center justify-center gap-2.5">
          {onRunAll && <button
            type="button"
            onClick={onRunAll}
            className="h-9 px-4 text-[14px] font-medium rounded-[5px] inline-flex items-center gap-2 cursor-pointer"
            style={{ backgroundColor: 'var(--accent)', color: 'var(--accent-contrast)' }}
          >
            <Play size={14} aria-hidden="true" />
            Run all transports
          </button>}
          <button
            type="button"
            onClick={onOpenRecordedSample}
            className="h-9 px-4 text-[14px] font-medium rounded-[5px] border cursor-pointer"
            style={{
              backgroundColor: 'var(--canvas)',
              borderColor: 'var(--border)',
              color: 'var(--text-primary)',
            }}
          >
            Open recorded sample
          </button>
        </div>
      </section>
    );
  }

  // No filter matches state
  if (rows.length === 0) {
    return (
      <section
        aria-label="No matching trace events"
        className="rounded-[5px] border px-6 py-10 flex flex-col items-center text-center gap-3"
        style={{ backgroundColor: 'var(--panel)', borderColor: 'var(--border)' }}
      >
        <h2 className="text-[16px] font-semibold" style={{ color: 'var(--text-primary)' }}>
          No observations match the active filters
        </h2>
        <p className="text-[13px] max-w-md" style={{ color: 'var(--text-muted)' }}>
          The capture retains events, but none fall inside the current protocol, ID, outcome, or
          time-window constraints.
        </p>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={onClearFilters}
            className="h-8 px-3 text-[13px] font-medium rounded-[4px] border cursor-pointer"
            style={{
              backgroundColor: 'var(--canvas)',
              borderColor: 'var(--accent)',
              color: 'var(--text-primary)',
            }}
          >
            Clear filters
          </button>
          {isZoomed && (
            <button
              type="button"
              onClick={() => onSetTimeWindow(null, null)}
              className="h-8 px-3 text-[13px] rounded-[4px] border cursor-pointer"
              style={{
                backgroundColor: 'var(--canvas)',
                borderColor: 'var(--border)',
                color: 'var(--text-primary)',
              }}
            >
              Reset range
            </button>
          )}
        </div>
      </section>
    );
  }

  return (
    <section
      aria-label="Event karyogram"
      className="rounded-[5px] border overflow-hidden"
      style={{ backgroundColor: 'var(--panel)', borderColor: 'var(--border)' }}
    >
      {/* Chart Frame Header: Title, Unit, Scope, Plot Controls & Table Action */}
      <div
        className="px-3.5 py-2 border-b flex flex-wrap items-center justify-between gap-2"
        style={{ borderColor: 'var(--border)', backgroundColor: 'var(--panel)' }}
      >
        <div className="flex flex-wrap items-baseline gap-x-3 gap-y-0.5">
          <h2 className="text-[16px] leading-[22px] font-semibold" style={{ color: 'var(--text-primary)' }}>
            Event karyogram
          </h2>
          <span className="text-[12px] font-mono-data" style={{ color: 'var(--text-muted)' }}>
            UTC sink timestamps · Drag plot to zoom · {rows.length} visible lanes
          </span>
        </div>

        <div className="flex flex-wrap items-center gap-1.5">
          <button
            type="button"
            onClick={onExpandAll}
            className="h-7 px-2 text-[12px] rounded-[4px] border inline-flex items-center gap-1 cursor-pointer row-hover"
            style={{ borderColor: 'var(--border)', color: 'var(--text-primary)' }}
            title="Expand visible groups"
          >
            <ChevronsUpDown size={13} aria-hidden="true" />
            <span className="hidden sm:inline">Expand all</span>
          </button>
          <button
            type="button"
            onClick={onCollapseAll}
            className="h-7 px-2 text-[12px] rounded-[4px] border inline-flex items-center gap-1 cursor-pointer row-hover"
            style={{ borderColor: 'var(--border)', color: 'var(--text-primary)' }}
            title="Collapse visible groups"
          >
            <ChevronsDownUp size={13} aria-hidden="true" />
            <span className="hidden sm:inline">Collapse</span>
          </button>

          <span className="w-px h-4 mx-0.5" style={{ backgroundColor: 'var(--border)' }} aria-hidden="true" />

          {/* Keyboard-accessible zoom/pan equivalents for brush */}
          <button
            type="button"
            onClick={() => panBy(-1)}
            disabled={!isZoomed}
            aria-label="Pan time window earlier"
            className="h-7 w-7 rounded-[4px] border inline-flex items-center justify-center cursor-pointer disabled:opacity-40"
            style={{ borderColor: 'var(--border)', color: 'var(--text-primary)' }}
          >
            <ChevronLeft size={14} aria-hidden="true" />
          </button>
          <button
            type="button"
            onClick={() => zoomBy(0.5)}
            aria-label="Zoom in time range"
            title="Zoom in"
            className="h-7 w-7 rounded-[4px] border inline-flex items-center justify-center cursor-pointer row-hover"
            style={{ borderColor: 'var(--border)', color: 'var(--text-primary)' }}
          >
            <ZoomIn size={14} aria-hidden="true" />
          </button>
          <button
            type="button"
            onClick={() => zoomBy(2)}
            disabled={!isZoomed}
            aria-label="Zoom out time range"
            title="Zoom out"
            className="h-7 w-7 rounded-[4px] border inline-flex items-center justify-center cursor-pointer disabled:opacity-40"
            style={{ borderColor: 'var(--border)', color: 'var(--text-primary)' }}
          >
            <ZoomOut size={14} aria-hidden="true" />
          </button>
          <button
            type="button"
            onClick={() => panBy(1)}
            disabled={!isZoomed}
            aria-label="Pan time window later"
            className="h-7 w-7 rounded-[4px] border inline-flex items-center justify-center cursor-pointer disabled:opacity-40"
            style={{ borderColor: 'var(--border)', color: 'var(--text-primary)' }}
          >
            <ChevronRight size={14} aria-hidden="true" />
          </button>
          <button
            type="button"
            onClick={() => onSetTimeWindow(null, null)}
            disabled={!isZoomed}
            aria-label="Reset time range"
            title="Reset range"
            className="h-7 px-2 text-[12px] rounded-[4px] border inline-flex items-center gap-1 cursor-pointer disabled:opacity-40"
            style={{ borderColor: 'var(--border)', color: 'var(--text-primary)' }}
          >
            <Maximize2 size={13} aria-hidden="true" />
            <span className="hidden sm:inline">Reset</span>
          </button>

          <button
            type="button"
            onClick={onOpenTable}
            className="h-7 px-2 text-[12px] rounded-[4px] border inline-flex items-center gap-1 cursor-pointer row-hover"
            style={{ borderColor: 'var(--border)', color: 'var(--text-primary)' }}
            title="Switch to equivalent accessible event table"
          >
            <Table2 size={13} aria-hidden="true" />
            <span>Table</span>
          </button>
        </div>
      </div>

      {/* Role Legend Strip */}
      <div
        className="px-3.5 py-1.5 border-b flex flex-wrap items-center gap-x-4 gap-y-1 text-[12px]"
        style={{ borderColor: 'var(--border)', color: 'var(--text-muted)' }}
      >
        <RoleMark role="success" label="Terminal OK / Commit / Delivered" />
        <RoleMark role="rejected" label="Rejected / Failed / Rollback" />
        <RoleMark role="partial" label="Partial / Open" />
        <RoleMark role="carrier" label="Connection / Session / Stream" />
        <RoleMark role="invocation" label="Invocation / Attachment / Tx" />
        <RoleMark role="neutral" kind="wt.datagram.received" label="Datagram" />
      </div>

      {/* Aligned 3-Column Karyogram Grid (Scroll container on narrow widths) */}
      <div className="overflow-x-auto">
        <div className="min-w-[720px] grid grid-cols-[240px_1fr] xl:grid-cols-[272px_1fr_188px]">
          {/* Column Header: Entity Hierarchy */}
          <div
            className="h-10 px-3 border-b border-r flex items-center text-[12px] font-medium sticky left-0 z-10"
            style={{
              backgroundColor: 'var(--panel)',
              borderColor: 'var(--border)',
              color: 'var(--text-muted)',
            }}
          >
            Entity hierarchy
          </div>

          {/* Column Header: Shared UTC Time Axis (SVG) */}
          <div
            className="h-10 border-b relative overflow-hidden"
            style={{ backgroundColor: 'var(--panel)', borderColor: 'var(--border)' }}
          >
            <svg
              width={plotWidth}
              height={40}
              className="block"
              role="img"
              aria-label={`Shared UTC time axis from ${formatUtcTime(domainMinMs)} to ${formatUtcTime(domainMaxMs)}`}
            >
              {ticks.major.map((t, idx) => (
                <g key={idx} transform={`translate(${t.x}, 0)`}>
                  <line
                    x1={0}
                    y1={30}
                    x2={0}
                    y2={40}
                    stroke={themePalette.textMuted}
                    strokeOpacity={0.5}
                  />
                  <text
                    x={idx === 0 ? 2 : idx === ticks.major.length - 1 ? -2 : 0}
                    y={14}
                    textAnchor={
                      idx === 0 ? 'start' : idx === ticks.major.length - 1 ? 'end' : 'middle'
                    }
                    fill={themePalette.textMuted}
                    fontSize={11}
                    fontFamily="IBM Plex Mono, monospace"
                  >
                    {t.label}
                  </text>
                  {isZoomed && (
                    <text
                      x={idx === 0 ? 2 : idx === ticks.major.length - 1 ? -2 : 0}
                      y={27}
                      textAnchor={
                        idx === 0 ? 'start' : idx === ticks.major.length - 1 ? 'end' : 'middle'
                      }
                      fill={themePalette.accent}
                      fontSize={10}
                      fontFamily="IBM Plex Mono, monospace"
                    >
                      {t.offset}
                    </text>
                  )}
                </g>
              ))}
            </svg>
          </div>

          {/* Column Header: Lane Totals Margin (>= 1280px) */}
          <div
            className="hidden xl:flex h-10 px-3 border-b border-l items-center justify-between text-[12px] font-medium"
            style={{
              backgroundColor: 'var(--panel)',
              borderColor: 'var(--border)',
              color: 'var(--text-muted)',
            }}
          >
            <span>Lane totals</span>
            <span className="font-mono-data">p50</span>
          </div>

          {/* Left Column: Sticky Entity Hierarchy Accordion */}
          <div
            className="border-r sticky left-0 z-10"
            style={{ backgroundColor: 'var(--panel)', borderColor: 'var(--border)' }}
          >
            {rows.map((row) => {
              const isSelected = selection?.type === 'entity' && selection.id === row.entityId;
              return (
                <div
                  key={row.rowId}
                  style={{
                    height: `${rowHeight}px`,
                    paddingLeft: `${8 + row.depth * 16}px`,
                    borderColor: 'var(--border)',
                    backgroundColor: isSelected
                      ? 'var(--selected-bg)'
                      : row.isGroupBoundary
                        ? 'var(--surface-alt)'
                        : 'var(--panel)',
                  }}
                  className={`pr-2 border-b flex items-center gap-1 lab-transition ${
                    isSelected ? 'row-selected' : 'row-hover'
                  }`}
                >
                  {/* Distinct disclosure button vs entity selection link */}
                  {row.hasChildren ? (
                    <button
                      type="button"
                      onClick={() => onToggleExpand(row.entityId)}
                      aria-expanded={row.isExpanded}
                      aria-label={`${row.isExpanded ? 'Collapse' : 'Expand'} ${row.label} ${row.shortId}`}
                      className="w-6 h-6 rounded-[3px] inline-flex items-center justify-center shrink-0 cursor-pointer"
                      style={{ color: 'var(--text-muted)' }}
                    >
                      <ChevronRight
                        size={14}
                        strokeWidth={1.75}
                        className="lab-transition"
                        style={{
                          transform: row.isExpanded ? 'rotate(90deg)' : 'rotate(0deg)',
                        }}
                        aria-hidden="true"
                      />
                    </button>
                  ) : (
                    <span className="w-6 shrink-0 inline-flex items-center justify-center" aria-hidden="true">
                      <RoleMark role={row.role} kind={row.entityKind === 'datagrams' ? 'wt.datagram.received' : undefined} size={10} />
                    </span>
                  )}

                  <button
                    type="button"
                    onClick={() => onSelect({ type: 'entity', id: row.entityId })}
                    className="flex-1 min-w-0 h-full text-left flex items-center justify-between gap-1.5 cursor-pointer"
                  >
                    <span
                      className="truncate text-[13px]"
                      style={{
                        color: 'var(--text-primary)',
                        fontWeight: row.depth === 0 ? 600 : 400,
                      }}
                    >
                      {row.label}
                    </span>
                    {row.depth > 0 && (
                      <span
                        className="font-mono-data text-[11px] shrink-0"
                        style={{ color: 'var(--text-muted)' }}
                      >
                        {row.shortId}
                      </span>
                    )}
                  </button>
                </div>
              );
            })}
          </div>

          {/* Center Column: Shared DPR Canvas + SVG Relationship Arcs + Brush */}
          <div
            ref={plotContainerRef}
            className="relative select-none"
            style={{ height: `${totalHeight}px`, backgroundColor: 'var(--panel)' }}
          >
            <canvas
              ref={canvasRef}
              tabIndex={0}
              aria-label="Event plot. Use the arrow keys to browse events and Enter to inspect."
              aria-describedby={hoverInfo ? tooltipId : undefined}
              onFocus={() => focusHitTarget(0)}
              onBlur={() => {
                keyboardTarget.current = -1;
                setHoverInfo(null);
              }}
              onKeyDown={handleCanvasKeyDown}
              onMouseDown={handleCanvasMouseDown}
              onMouseMove={handleCanvasMouseMove}
              onMouseUp={handleCanvasMouseUp}
              onMouseLeave={() => {
                setHoverInfo(null);
                setBrushStartX(null);
                setBrushCurrentX(null);
              }}
              className="block cursor-crosshair"
            />

            {/* SVG Overlay: Directional Relationship Arcs (selected record only) & Brush */}
            <svg
              width={plotWidth}
              height={totalHeight}
              className="absolute inset-0 pointer-events-none"
              aria-hidden="true"
            >
              <defs>
                <marker
                  id="arc-arrow"
                  viewBox="0 0 8 8"
                  refX="6"
                  refY="4"
                  markerWidth="6"
                  markerHeight="6"
                  orient="auto-start-reverse"
                >
                  <path d="M 0 1 L 7 4 L 0 7 z" fill={themePalette.accent} />
                </marker>
              </defs>

              {arcs.map((arc) => {
                const idxA = rowIndexById.get(arc.fromRowId);
                const idxB = rowIndexById.get(arc.toRowId);
                if (idxA === undefined || idxB === undefined) return null;
                const x1 = timeToX(arc.fromMs);
                const y1 = idxA * rowHeight + rowHeight / 2;
                const x2 = timeToX(arc.toMs);
                const y2 = idxB * rowHeight + rowHeight / 2;
                const ctrlX = Math.max(x1, x2) + Math.min(48, Math.abs(y2 - y1) * 0.25 + 16);
                const ctrlY = (y1 + y2) / 2;
                return (
                  <path
                    key={arc.id}
                    d={`M ${x1} ${y1} Q ${ctrlX} ${ctrlY} ${x2} ${y2}`}
                    fill="none"
                    stroke={themePalette.accent}
                    strokeWidth={1.5}
                    strokeDasharray={arc.dashed ? '4 3' : undefined}
                    markerEnd="url(#arc-arrow)"
                    opacity={0.9}
                  />
                );
              })}

              {brushStartX !== null && brushCurrentX !== null && Math.abs(brushCurrentX - brushStartX) > 4 && (
                <rect
                  x={Math.min(brushStartX, brushCurrentX)}
                  y={0}
                  width={Math.abs(brushCurrentX - brushStartX)}
                  height={totalHeight}
                  fill={themePalette.accent}
                  fillOpacity={0.16}
                  stroke={themePalette.accent}
                  strokeWidth={1}
                />
              )}
            </svg>

            {/* Hover Tooltip */}
            {hoverInfo && canvasRef.current && (
              <EventTooltip
                id={tooltipId}
                anchor={hoverInfo.cursor ?? { element: canvasRef.current, bounds: hoverInfo.target }}
                className="px-2.5 py-2 rounded-[5px] border"
                style={{
                  backgroundColor: 'var(--canvas)',
                  borderColor: 'var(--border)',
                  boxShadow: 'var(--overlay-shadow)',
                }}
              >
                {hoverInfo.target.isBucket ? (
                  <div className="space-y-0.5 text-[12px]">
                    <div className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                      {hoverInfo.target.events.length} events in time bin
                    </div>
                    <div className="font-mono-data" style={{ color: 'var(--text-muted)' }}>
                      {formatUtcTime(hoverInfo.target.startMs)} →{' '}
                      {formatUtcTime(hoverInfo.target.endMs)}
                    </div>
                    <div style={{ color: 'var(--accent)' }}>Click to inspect bucket in table</div>
                  </div>
                ) : (
                  <div className="space-y-0.5 text-[12px]">
                    <div className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                      {hoverInfo.target.events[0].displayLabel}
                    </div>
                    <div className="flex items-center gap-2" style={{ color: 'var(--text-muted)' }}>
                      <RoleMark
                        role={hoverInfo.target.events[0].role}
                        kind={hoverInfo.target.events[0].kind}
                        label={hoverInfo.target.events[0].outcomeLabel}
                        size={10}
                      />
                    </div>
                    <div className="font-mono-data" style={{ color: 'var(--text-muted)' }}>
                      Recorded: {formatUtcTime(hoverInfo.target.events[0].atMs)} · seq #
                      {hoverInfo.target.events[0].sequence}
                    </div>
                    {hoverInfo.target.events[0].duration_ms !== undefined && (
                      <div className="font-mono-data" style={{ color: 'var(--accent)' }}>
                        Measured: {hoverInfo.target.events[0].duration_ms} ms
                      </div>
                    )}
                  </div>
                )}
              </EventTooltip>
            )}
          </div>

          {/* Right Column: Lane Totals & Median Latency Margin (>= 1280px) */}
          <div
            className="hidden xl:block border-l"
            style={{ backgroundColor: 'var(--panel)', borderColor: 'var(--border)' }}
          >
            {rows.map((row) => {
              const isSelected = selection?.type === 'entity' && selection.id === row.entityId;
              return (
                <div
                  key={`tot-${row.rowId}`}
                  style={{
                    height: `${rowHeight}px`,
                    borderColor: 'var(--border)',
                    backgroundColor: isSelected
                      ? 'var(--selected-bg)'
                      : row.isGroupBoundary
                        ? 'var(--surface-alt)'
                        : 'var(--panel)',
                  }}
                  className="px-3 border-b flex items-center justify-between gap-2 text-[12px] font-mono-data"
                >
                  <button
                    type="button"
                    onClick={() => onSelect({ type: 'entity', id: row.entityId })}
                    className="truncate hover:underline cursor-pointer"
                    style={{
                      color:
                        row.role === 'rejected'
                          ? 'var(--role-rejected)'
                          : row.isOpen
                            ? 'var(--role-partial)'
                            : 'var(--text-muted)',
                    }}
                  >
                    {row.countLabel}
                  </button>
                  <span
                    className="shrink-0"
                    style={{ color: 'var(--text-muted)' }}
                    title={
                      row.measuredLatencyMedianMs != null
                        ? 'Nearest-rank p50 producer-measured duration'
                        : 'No producer-measured duration in this lane'
                    }
                  >
                    {row.measuredLatencyMedianMs != null
                      ? `${row.measuredLatencyMedianMs.toFixed(1)}ms`
                      : '—'}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
};
