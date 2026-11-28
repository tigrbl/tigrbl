import type { WaterfallEdge } from './types';

export function groupTimelineNodes<T>(nodes: readonly T[], position: (node: T) => number) {
  const sorted = [...nodes].sort((a, b) => position(a) - position(b));
  const groups: Array<{ first: number; last: number; x: number; width: number }> = [];
  const widthFor = (count: number) => count === 1 ? 12 : Math.max(18, String(count).length * 7 + 8);
  for (const [last, node] of sorted.entries()) {
    const end = position(node);
    let first = last;
    let x = end;
    let width = widthFor(1);
    // Grow the badge around its actual time range and merge any neighbors it would cover.
    while (groups.length) {
      const previous = groups[groups.length - 1];
      if (x - width / 2 >= previous.x + previous.width / 2 + 2) break;
      groups.pop();
      first = previous.first;
      x = (position(sorted[first]) + end) / 2;
      width = widthFor(last - first + 1);
    }
    groups.push({ first, last, x, width });
  }
  return groups.map(({ first, last, x, width }) => ({
    nodes: sorted.slice(first, last + 1), x, width,
  }));
}

export interface EdgeGeometryInput {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  kind: WaterfallEdge['kind'];
  hasEndpointChip: boolean;
  plotWidth: number;
  fromIsRequester: boolean;
  toIsRequester: boolean;
}

export interface EdgeGeometryResult {
  dPath: string;
  routeStyle: 'horizontal' | 'ray' | 'elbow';
  startX: number;
  startY: number;
  endX: number;
  endY: number;
  peerAnchor?: { x: number; y: number };
  chipX: number;
  chipY: number;
}

function fmt(n: number): string {
  return Number.isFinite(n) ? Number(n.toFixed(1)).toString() : '0';
}

/**
 * Computes clean, non-kinking SVG path geometry for directional waterfall edges:
 * - Same-lane edges: trimmed straight horizontal line stopping cleanly before endpoint chips.
 * - Wire ingress / egress rays (to/from Requester): trimmed straight directional rays with a
 *   subtle peer contact anchor so arrowheads always align along the true travel direction.
 * - Forward internal cross-lane handoffs (dx >= 20): rounded orthogonal L-elbow dropping
 *   vertically from the source event and entering the destination mark cleanly from the left.
 * - Tight or backward clock-skewed cross-lane edges (dx < 20): trimmed straight directional ray.
 */
export function computeEdgeGeometry(input: EdgeGeometryInput): EdgeGeometryResult {
  const {
    x1,
    y1,
    x2,
    y2,
    kind,
    hasEndpointChip,
    plotWidth,
    fromIsRequester,
    toIsRequester,
  } = input;

  // 1. Same-lane horizontal edge (dashed sibling/evicted/external link)
  if (Math.abs(y2 - y1) < 0.5) {
    const startX = x1 + 6;
    const rawEndX = Math.abs(x2 - x1) < 28 ? x1 + 36 : x2;
    const maxEndX = plotWidth - (hasEndpointChip ? 142 : 16);
    const endX = Math.max(startX + 14, Math.min(maxEndX, rawEndX));
    const chipX = Math.min(plotWidth - 138, Math.max(8, endX + 6));

    return {
      dPath: `M ${fmt(startX)} ${fmt(y1)} L ${fmt(endX)} ${fmt(y1)}`,
      routeStyle: 'horizontal',
      startX,
      startY: y1,
      endX,
      endY: y1,
      chipX,
      chipY: y1 - 9,
    };
  }

  const dx = x2 - x1;
  const dy = y2 - y1;
  const dirY = dy > 0 ? 1 : -1;

  // 2. Wire ingress / egress rays (Requester <-> Server/Stream)
  const isWireRay =
    kind === 'request_ingress' ||
    kind === 'response_egress' ||
    fromIsRequester ||
    toIsRequester;

  if (isWireRay || dx < 20) {
    const len = Math.max(1, Math.hypot(dx, dy));
    const ux = dx / len;
    const uy = dy / len;

    const desiredStartPad = fromIsRequester ? 4 : 6;
    const desiredEndPad = toIsRequester ? 5.5 : 7.5;
    const maxPadSum = Math.max(0, len - 6);
    const padScale =
      desiredStartPad + desiredEndPad > maxPadSum
        ? maxPadSum / (desiredStartPad + desiredEndPad)
        : 1;

    const startPad = desiredStartPad * padScale;
    const endPad = desiredEndPad * padScale;

    const startX = x1 + ux * startPad;
    const startY = y1 + uy * startPad;
    const endX = x2 - ux * endPad;
    const endY = y2 - uy * endPad;

    const peerAnchor = fromIsRequester
      ? { x: x1, y: y1 }
      : toIsRequester
      ? { x: x2, y: y2 }
      : undefined;

    const chipX = Math.min(plotWidth - 138, Math.max(8, x2 + 8));

    return {
      dPath: `M ${fmt(startX)} ${fmt(startY)} L ${fmt(endX)} ${fmt(endY)}`,
      routeStyle: 'ray',
      startX,
      startY,
      endX,
      endY,
      peerAnchor,
      chipX,
      chipY: y2 - 9,
    };
  }

  // 3. Forward internal cross-lane handoff (dx >= 20): rounded orthogonal L-elbow
  const startX = x1;
  const startY = y1 + dirY * 6;
  const endX = Math.max(startX + 10, x2 - 7);
  const endY = y2;

  const availV = Math.abs(endY - startY);
  const availH = Math.abs(endX - startX);
  const r = Math.min(12, availV * 0.45, availH * 0.45);

  const cornerStartY = endY - dirY * r;
  const cornerEndX = startX + r;

  const dPath = `M ${fmt(startX)} ${fmt(startY)} L ${fmt(startX)} ${fmt(cornerStartY)} Q ${fmt(startX)} ${fmt(endY)}, ${fmt(cornerEndX)} ${fmt(endY)} L ${fmt(endX)} ${fmt(endY)}`;
  const chipX = Math.min(plotWidth - 138, Math.max(8, x2 + 8));

  return {
    dPath,
    routeStyle: 'elbow',
    startX,
    startY,
    endX,
    endY,
    chipX,
    chipY: y2 - 9,
  };
}
